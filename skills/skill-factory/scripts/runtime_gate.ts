/** The existing compiler task owns runtime checks and their Mastra proof. */
import { execFile } from 'node:child_process';
import { promisify, isDeepStrictEqual } from 'node:util';
import { isAbsolute, resolve, join } from 'node:path';
import { open, unlink } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { createStep, createWorkflow } from '@mastra/core/workflows';
import { Mastra } from '@mastra/core/mastra';
import { InMemoryStore, type MastraCompositeStore } from '@mastra/core/storage';
import { z } from 'zod';
import { bound, digest, runtimeIdentity, taskSnapshot } from './task_inventory.ts';
import { taskContract, taskContractSchema, workflowRoots } from './standardization_workflow.ts';
import { readThroughOwner } from './review_ledger_workflow.ts';
import { openStorage } from './run_standardization.ts';

const text = z.string().min(1), hash = z.string().regex(/^[a-f0-9]{64}$/);
const inputSchema = z.object({ root: text, request: z.unknown(), task: taskContractSchema,
  runtime: z.record(text, hash), input_sha256: hash }).strict();
const commandSchema = z.object({ command: z.array(text), stdout: z.string(), stderr: z.string(), code: z.literal(0) });
const outputSchema = z.object({ input: inputSchema, checks: z.array(commandSchema).length(3) }).strict();
const execute = promisify(execFile);
const storageProbe = "import {createRequire} from 'node:module'; import {pathToFileURL} from 'node:url'; "
  + "const load=createRequire(new URL('./runtime/standardization/package.json',import.meta.url)); "
  + "const path=load.resolve('@mastra/libsql'); const runtime=await import(pathToFileURL(path).href); "
  + "if(typeof runtime.LibSQLStore!=='function') throw Error('Storage runtime has no LibSQLStore'); "
  + "console.log(JSON.stringify({resolved:path,LibSQLStore:'available'}));";
const setupCommand = ['npm ci --include=dev --ignore-scripts 1>&2',
  'npm ci --prefix runtime/standardization --omit=peer --ignore-scripts 1>&2'];

async function capture(root: string, request: unknown) {
  const task = await taskContract(root, 'check-runtime', 'node scripts/runtime_gate.ts', ['setup-runtime']);
  const setup = (await taskSnapshot(root)).tasks.find(task => task.name === 'setup-runtime');
  if (!setup || !isDeepStrictEqual(setup.run, setupCommand) || !isDeepStrictEqual(setup.depends, []))
    throw Error('Runtime setup needs explicit command and prerequisite review');
  const input = { root, request, task, runtime: await runtimeIdentity(root) };
  return { ...input, input_sha256: identity(input) };
}

async function command(root: string, args: string[]) {
  try {
    const result = await execute('npm', args, { cwd: root, maxBuffer: 32 * 1024 * 1024 });
    return { command: ['npm', ...args], stdout: result.stdout, stderr: result.stderr, code: 0 as const };
  } catch (error) {
    const failed = error as { stdout?: string; stderr?: string };
    process.stderr.write((failed.stdout ?? '') + (failed.stderr ?? ''));
    throw error;
  }
}

function workflow() {
  const step = createStep({ id: 'compiler', inputSchema, outputSchema, execute: async ({ inputData }) => {
    const checks = [await command(inputData.root, ['ls', '--all', '--json']),
      await command(inputData.root, ['exec', '--no', '--', 'node', '--input-type=module', '--eval', storageProbe]),
      await command(inputData.root, ['exec', '--no', '--', 'tsc', '--noEmit', '--project', 'tsconfig.json'])];
    if ((await capture(inputData.root, inputData.request)).input_sha256 !== inputData.input_sha256)
      throw Error('Runtime inputs changed during checking');
    return { input: inputData, checks };
  } });
  return createWorkflow({ id: 'runtime-check', inputSchema, outputSchema,
    options: { validateInputs: true, autoRestartActiveRuns: false } }).then(step).commit();
}

const identity = (value: unknown) => digest(Buffer.from(JSON.stringify(value, (_key, item) =>
  item !== null && typeof item === 'object' && !Array.isArray(item)
    ? Object.fromEntries(Object.keys(item).sort().map(key => [key, item[key]])) : item)));

const owner = (storage: MastraCompositeStore) => new Mastra({ workflows: { 'runtime-check': workflow() }, storage, logger: false });

export async function requireRuntimeProof(root: string, storage: MastraCompositeStore, request: unknown) {
  const input = await capture(root, request);
  const saved = await owner(storage).getWorkflow('runtime-check').getWorkflowRunById(identity(request));
  if (saved?.status !== 'success') throw Error('Missing check-runtime prerequisite proof');
  const output = outputSchema.parse(saved.result);
  if (output.input.input_sha256 !== input.input_sha256) throw Error('Stale check-runtime prerequisite proof');
  return output;
}

async function checked(root: string, storage: MastraCompositeStore, request: unknown) {
  const input = await capture(root, request), selected = owner(storage).getWorkflow('runtime-check');
  const run = await selected.createRun();
  const result = await run.start({ inputData: input });
  return { ...result, run_id: run.runId };
}

async function savedCheck(root: string, storage: MastraCompositeStore, request: unknown) {
  const input = await capture(root, request), selected = owner(storage).getWorkflow('runtime-check');
  const saved = await selected.getWorkflowRunById(identity(request));
  if (saved?.status === 'success') {
    const result = await requireRuntimeProof(root, storage, request);
    return { status: 'success', result, reused: true };
  }
  if (saved) throw Error('Retain failed runtime work; use a new request after repair');
  return (await selected.createRun({ runId: identity(request) })).start({ inputData: input });
}

async function closeState(storage?: MastraCompositeStore, lock?: Awaited<ReturnType<typeof open>>, path?: string) {
  try { await storage?.close(); }
  finally { if (lock) { await lock.close(); await unlink(path!); } }
}

async function main() {
  let storage: MastraCompositeStore | undefined, lock: Awaited<ReturnType<typeof open>> | undefined, lockPath: string | undefined;
  try {
    if (process.argv.length !== 2 || process.env.MISE_TASK_NAME !== 'check-runtime')
      throw Error('Use mise run check-runtime');
    const root = fileURLToPath(new URL('../', import.meta.url));
    const state = process.env.SKILL_RULE_STATE, requestPath = process.env.SKILL_RULE_REQUEST;
    if (Boolean(state) !== Boolean(requestPath) || (requestPath && !isAbsolute(requestPath)))
      throw Error('Supply both absolute rule request and private state');
    const request = requestPath ? await readThroughOwner('parse', (await bound(requestPath)).raw.toString()) : {};
    if (state) await workflowRoots({ factory: root, state, environment: { UV_PYTHON: process.env.UV_PYTHON ?? '' } });
    storage = state ? await openStorage(state) : new InMemoryStore();
    if (state) { lockPath = join(state, 'rule-workflow.lock'); lock = await open(lockPath, 'wx', 0o600); }
    const result = state ? await savedCheck(root, storage, request) : await checked(root, storage, request);
    process.exitCode = result.status === 'success' ? 0 : 1;
    process.stdout.write(JSON.stringify({ ...result, execution_acceptance: 'pending' }) + '\n');
  } catch (error) {
    process.stderr.write((error instanceof Error ? error.stack ?? error.message : String(error)) + '\n');
    process.exitCode = 1;
  } finally { await closeState(storage, lock, lockPath); }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
