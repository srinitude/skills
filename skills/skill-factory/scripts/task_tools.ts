/** One live MCP tool per skill task. The host owns transport and permissions. */
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { realpath } from 'node:fs/promises';
import { watch, type FSWatcher } from 'node:fs';
import { dirname, isAbsolute, join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Server } from '@modelcontextprotocol/server';
import { z } from 'zod';
import { bound, digest } from './standardization_workflow.ts';

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
const nativeTask = z.object({ name: z.string().min(1), description: z.string(),
  source: z.string().refine(isAbsolute), config_sources: z.array(z.string()).default([]), depends: z.array(z.unknown()).default([]) }).passthrough();
type Task = z.infer<typeof nativeTask>;
type Input = z.infer<typeof inputs>;
type Snapshot = { tasks: Task[]; revision: string };

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
function inside(root: string, path: string) {
  const part = relative(root, path);
  return part !== '..' && !part.startsWith('..' + sep) && !isAbsolute(part);
}
async function nativeTasks(root: string, input = inputs.parse({})) {
  const { stdout } = await execute('mise', ['-C', root, 'tasks', 'ls', '--hidden', '--json'],
    { env: environment(input), maxBuffer: 16 * 1024 * 1024, timeout: 30000 });
  return z.array(nativeTask).parse(JSON.parse(stdout)).filter(task => inside(root, task.source))
    .sort((a, b) => a.name < b.name ? -1 : Number(a.name > b.name));
}
async function snapshot(root: string, input = inputs.parse({})): Promise<Snapshot> {
  const tasks = await nativeTasks(root, input);
  if (new Set(tasks.map(task => taskToolName(task.name))).size !== tasks.length)
    throw Error('Task tool name collision');
  const sources = [...new Set([join(root, 'mise.toml'),
    ...tasks.flatMap(task => [task.source, ...task.config_sources])])].sort();
  for (const source of sources)
    if (!inside(root, await realpath(source))) throw Error('Task source escapes this skill');
  const identities = await Promise.all(sources.map(async source => [source, (await bound(source)).sha256] as const));
  if (JSON.stringify(tasks) !== JSON.stringify(await nativeTasks(root, input))) throw Error('Tasks changed during discovery');
  for (const [source, sha256] of identities) await bound(source, sha256);
  return { tasks, revision: digest(Buffer.from(JSON.stringify([tasks, identities]))) };
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
async function refresh(state: State, input = inputs.parse({})) {
  await bound(state.codePath, state.codeHash);
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
  const codeHash = (await bound(codePath)).sha256;
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
