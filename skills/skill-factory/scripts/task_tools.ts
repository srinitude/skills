/** One live MCP tool per skill task. The host owns transport and permissions. */
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { realpath } from 'node:fs/promises';
import { watch, type FSWatcher } from 'node:fs';
import { dirname, isAbsolute, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Server } from '@modelcontextprotocol/server';
import { StdioServerTransport } from '@modelcontextprotocol/server/stdio';
import { createStep, createWorkflow } from '@mastra/core/workflows';
import { taskContract, taskContractSchema } from './standardization_workflow.ts';
import { z } from 'zod';
import { bound, digest, taskSnapshot, type Task, type Snapshot } from './task_inventory.ts';

const execute = promisify(execFile);
const hash = z.string().regex(/^[a-f0-9]{64}$/);
const file = z.object({ path: z.string().refine(isAbsolute), sha256: hash }).strict();
const inputs = z.object({
  action: z.enum(['inspect', 'run']).default('inspect'),
  args: z.array(z.string().max(8192).refine(value => value !== ':::')).max(128).default([]),
  env: z.record(z.string().regex(/^SKILL_[A-Z0-9_]+$/), z.string()).default({}),
  files: z.array(file).default([]),
  revision: hash.optional(),
}).strict();
type Input = z.infer<typeof inputs>;

export function taskToolName(name: string) {
  const value = 'task_' + name.replaceAll(':', '__').replaceAll('-', '_').replaceAll('.', '_');
  if (!/^[a-zA-Z][a-zA-Z0-9_]{0,63}$/.test(value)) throw Error('Unsupported task tool name: ' + name);
  return value;
}
const result = (value: Record<string, unknown>, isError = false) => ({
  isError, structuredContent: value, content: [{ type: 'text' as const, text: JSON.stringify(value) }],
});
function environment(input: Input) {
  const env = { ...process.env, ...input.env };
  // The tool selects one task; inherited task-skip flags cannot choose a shorter path.
  for (const key of ['MISE_SKIP_TASKS', 'MISE_TASK_SKIP', 'MISE_TASK_NAME']) delete env[key];
  return { ...env, MISE_TASK_SKIP_DEPENDS: '0' };
}
async function snapshot(root: string, input = inputs.parse({})): Promise<Snapshot> {
  const state = await taskSnapshot(root, environment(input));
  if (new Set(state.tasks.map(task => taskToolName(task.name))).size !== state.tasks.length)
    throw Error('Task tool name collision');
  return state;
}

async function revision(state: Snapshot, name: string, input: Input) {
  for (const item of input.files) await bound(item.path, item.sha256);
  return digest(Buffer.from(JSON.stringify([state.revision, name, input.args, input.env, input.files])));
}
function description(task: Task) {
  const part = (heading: string) => task.description.split('## ' + heading + '\n')[1]?.trim().split('\n\n')[0];
  return 'When: ' + (part('When to run') ?? task.description) + '\nPurpose: ' +
    (part('Why this runs') ?? task.description) + '\nInspect full rules; run with that revision. Mise runs prerequisites.';
}
async function runTask(root: string, name: string, input: Input) {
  const command = ['-C', root, 'run', name, '--', ...input.args];
  try {
    const output = await execute('mise', command, { env: environment(input), maxBuffer: 16 * 1024 * 1024 });
    return { exit_code: 0, stdout: output.stdout, stderr: output.stderr };
  } catch (error) {
    const value = error as { code?: unknown; stdout?: string; stderr?: string; message?: string };
    return { exit_code: typeof value.code === 'number' ? value.code : null,
      stdout: value.stdout ?? '', stderr: value.stderr ?? value.message ?? String(error) };
  }
}
function handoff(output: Awaited<ReturnType<typeof runTask>>) {
  if (output.exit_code !== 3 && output.exit_code !== 0) return;
  try {
    const text = z.string().trim().min(1), hash = z.string().regex(/^[a-f0-9]{64}$/);
    const base = z.object({ status: z.literal('suspended'), run_id: text.optional(), runId: text.optional() })
      .passthrough().refine(value => Boolean(value.run_id || value.runId));
    const mastra = z.object({ suspended: z.array(z.union([text, z.array(text).min(1)])).min(1),
      suspendPayload: z.record(z.string(), z.unknown()) }).passthrough();
    const native = z.object({ request_sha256: hash, pending: z.object({
      request_sha256: hash, input: z.object({ run_id: text }).passthrough() }).passthrough() })
      .passthrough().refine(value => value.request_sha256 === value.pending.request_sha256);
    const standard = z.object({ review_step: text, persistent: z.boolean() }).passthrough();
    const raw = JSON.parse(output.stdout.trimEnd().split('\n').at(-1) ?? '');
    const selected = raw.workflow ?? raw, identity = base.safeParse(selected);
    if (!identity.success) return;
    const pending = native.safeParse(selected);
    if (pending.success && pending.data.pending.input.run_id === identity.data.run_id) return identity.data;
    if (mastra.safeParse(selected).success || standard.safeParse(selected).success) return identity.data;
  } catch { /* Preserve unrecognized output as an error or ordinary task result. */ }
}
type State = { root: string; codePath: string; codeHash: string; current: Snapshot; server: Server; busy: boolean };
async function adapterIdentity(codePath: string) {
  const files = [codePath, fileURLToPath(new URL('./task_inventory.ts', import.meta.url))];
  const raw = await Promise.all(files.map(async path => (await bound(path)).raw));
  return digest(Buffer.concat(raw));
}
async function refresh(state: State, input = inputs.parse({})) {
  if (await adapterIdentity(state.codePath) !== state.codeHash) throw Error('Task adapter changed; reconnect tools.');
  const next = await snapshot(state.root, input), changed = next.revision !== state.current.revision;
  state.current = next;
  if (changed && state.server.transport) await state.server.sendToolListChanged();
  return next;
}
async function callTask(state: State, name: string, raw: unknown) {
  if (state.busy) return result({ status: 'error', message: 'Another task tool call is running; wait.' }, true);
  state.busy = true;
  let output: Awaited<ReturnType<typeof runTask>> | undefined;
  try {
    const input = inputs.parse(raw), current = await refresh(state, input);
    const task = current.tasks.find(item => taskToolName(item.name) === name);
    if (!task) throw Error('Task was removed or does not exist; refresh tools.');
    const identity = await revision(current, task.name, input);
    if (input.action === 'inspect') return result({ status: 'inspected', task, revision: identity });
    if (identity !== input.revision) throw Error('Task or inputs changed; inspect this exact task again.');
    if (task.name === 'task-tools') throw Error('The host opens task-tools; do not start a nested tool connection.');
    output = await runTask(state.root, task.name, input);
    const after = await refresh(state, input), unchanged = identity === await revision(after, task.name, input);
    const workflow = handoff(output), failed = output.exit_code !== 0 && !workflow;
    return result({ task: task.name, ...output, inputs_unchanged: unchanged, workflow,
      status: !unchanged ? 'stale' : workflow ? 'suspended' : failed ? 'failed' : 'success',
      status_scope: 'task', execution_acceptance: 'pending' }, failed || !unchanged);
  } catch (error) {
    return result({ status: 'error', ...output, execution_acceptance: 'pending',
      message: error instanceof Error ? error.message : String(error) }, true);
  } finally { state.busy = false; }
}
function refreshIdle(state: State) {
  if (!state.busy) void refresh(state).catch(error => console.error(String(error)));
}
function watchTasks(state: State) {
  const watchers: FSWatcher[] = [];
  let timer: ReturnType<typeof setTimeout> | undefined;
  const changed = () => {
    clearTimeout(timer);
    timer = setTimeout(refreshIdle, 50, state);
  };
  // Native tools/list also refreshes; file watches are only a prompt to inspect again.
  for (const folder of new Set([state.root, ...state.current.tasks.map(task => dirname(task.source))]))
    watchers.push(watch(folder, changed));
  state.server.onclose = () => { clearTimeout(timer); for (const watcher of watchers) watcher.close(); };
}
export async function createTaskTools(directory: string) {
  const root = await realpath(directory), codePath = fileURLToPath(import.meta.url);
  const codeHash = await adapterIdentity(codePath);
  const server = new Server({ name: 'agent-skill-tasks', version: '1.0.0' },
    { capabilities: { tools: { listChanged: true } },
      instructions: 'Inspect the relevant individual task tool. Read its full rules, then run the same tool with its revision. Mise owns dependencies; the model and human retain their judgment and approval duties.' });
  const state: State = { root, codePath, codeHash, server, current: await snapshot(root), busy: false };
  server.setRequestHandler('tools/list', async () => ({ tools: (await refresh(state)).tasks.map(task => ({
    name: taskToolName(task.name), title: task.name, description: description(task),
    inputSchema: z.toJSONSchema(inputs, { io: 'input' }) as { type: 'object' },
    annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: true },
  })) }));
  server.setRequestHandler('tools/call', async request => callTask(state, request.params.name, request.params.arguments ?? {}));
  watchTasks(state);
  return { server, refresh: () => refresh(state) };
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 1 && args[0] === '--help') {
    process.stdout.write('Usage: mise run task-tools\nOne MCP tool per live skill task over stdin/stdout.\nExample: mise -C /path/to/skill run task-tools\nExit 0: closed; 1: startup failure; 2: bad usage.\n');
    return;
  }
  if (args.length || process.env.MISE_TASK_NAME !== 'task-tools') {
    console.error('Start through mise run task-tools with no arguments.'); process.exitCode = 2; return;
  }
  const root = fileURLToPath(new URL('..', import.meta.url));
  const task = await taskContract(root, 'task-tools', 'node scripts/task_tools.ts', ['check-runtime']);
  const ready = createStep({ id: 'check-task-source', inputSchema: taskContractSchema, outputSchema: taskContractSchema,
    execute: async ({ inputData }) => { await bound(inputData.source, inputData.sha256); return inputData; } });
  const workflow = createWorkflow({ id: 'task-tools-readiness', inputSchema: taskContractSchema,
    outputSchema: taskContractSchema }).then(ready).commit();
  const checked = await (await workflow.createRun()).start({ inputData: task });
  if (checked.status !== 'success') throw Error('Task tool readiness failed');
  // Transport serves independent task calls after the readiness workflow has ended.
  const { server } = await createTaskTools(root);
  process.stdin.once('end', () => { void server.close().catch(error => { console.error(error); process.exitCode = 1; }); });
  await server.connect(new StdioServerTransport());
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url))
  await main().catch(error => { console.error(error); process.exitCode = 1; });
