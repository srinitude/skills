/** Persist one native-tool handoff; full goal acceptance remains separate. */
import { mkdir, rmdir, lstat, realpath } from 'node:fs/promises';
import { isAbsolute, join, relative, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { isDeepStrictEqual } from 'node:util';
import { createStep, createWorkflow } from '@mastra/core/workflows';
import { Mastra } from '@mastra/core/mastra';
import { z } from 'zod';
import { bound, digest } from './standardization_workflow.ts';
import { openStorage } from './run_standardization.ts';
import { requestSchema, runLedger, readThroughOwner } from './review_ledger_workflow.ts';

const text = z.string().min(1).refine(value => value.trim().length > 0), hash = z.string().regex(/^[a-f0-9]{64}$/);
const envelopeSchema = z.object({ run_id: text, turn: text, baseline: text,
  iteration: z.number().int().nonnegative(), request: requestSchema }).strict();
const inputSchema = envelopeSchema.extend({ root: text.refine(isAbsolute),
  pending: hash.optional(), runtime: z.record(text, hash) }).strict();
const replySchema = z.object({ run_id: text, request_sha256: hash, tool: text,
  status: z.enum(['success', 'error', 'interrupted']), result: text }).strict();
const checkedSchema = z.object({ input: inputSchema, request_sha256: hash,
  before_base64: z.string().nullable(), preflight: z.unknown() }).strict();
const outputSchema = checkedSchema.extend({ receipt: replySchema, readback: z.unknown(),
  execution_acceptance: z.literal('pending') }).strict();
type Input = z.infer<typeof inputSchema>;

async function nativeCheck(input: Input, phase: 'before' | 'after') {
  const result = await runLedger({ ...input.request, phase }, input.root, input.pending);
  if (result.status !== 'success') throw result.status === 'failed' ? result.error : new Error('Native check did not finish');
  return JSON.parse(result.result.view_text) as unknown;
}

async function runtimeBindings() {
  const files = ['native_file_workflow.ts', 'run_review_ledger.ts', 'review_ledger_workflow.ts',
    'review_ledger.py', 'review_ledger_native.py', 'review_ledger_write.py', 'review_ledger_body.py',
    'review_ledger_source.py', 'review_ledger_context.py', 'skill_package.py', 'agentic_request_contract.py', 'domain_text.py',
    'standardization_workflow.ts', 'run_standardization.ts', '../package-lock.json',
    '../runtime/standardization/package-lock.json'];
  return Object.fromEntries(await Promise.all(files.map(async name =>
    [name, (await bound(fileURLToPath(new URL(name, import.meta.url)))).sha256])));
}

function createHandoff(storage: Awaited<ReturnType<typeof openStorage>>) {
  const before = createStep({ id: 'native-preflight', inputSchema, outputSchema: checkedSchema, retries: 0,
    execute: async ({ inputData: input }) => {
      const preflight = await nativeCheck(input, 'before'), change = input.request.change!;
      const old = change.expected_sha256 === null ? null
        : (await bound(join(input.root, change.path), change.expected_sha256)).raw.toString('base64');
      return { input, request_sha256: digest(Buffer.from(JSON.stringify(input))), before_base64: old, preflight };
    } });
  const effect = createStep({ id: 'native-effect', inputSchema: checkedSchema, outputSchema,
    resumeSchema: replySchema, suspendSchema: checkedSchema, retries: 0,
    execute: async ({ inputData, resumeData, suspend }) => {
      if (!resumeData) return await suspend(inputData);
      const receipt = replySchema.parse(resumeData);
      if (receipt.run_id !== inputData.input.run_id || receipt.request_sha256 !== inputData.request_sha256)
        throw new Error('Native receipt belongs to another run or input');
      if (receipt.status !== 'success') throw new Error('Native tool failure retained: ' + receipt.result);
      const readback = await nativeCheck(inputData.input, 'after');
      return { ...inputData, receipt, readback, execution_acceptance: 'pending' as const };
    } });
  const workflow = createWorkflow({ id: 'native-file-handoff', inputSchema, outputSchema,
    options: { validateInputs: true, autoRestartActiveRuns: false } }).then(before).then(effect).commit();
  return new Mastra({ workflows: { native: workflow }, storage, logger: false }).getWorkflow('native');
}

async function executeHandoff(workflow: ReturnType<typeof createHandoff>, input: Input, reply?: unknown) {
  const saved = await workflow.getWorkflowRunById(input.run_id);
  if (saved && !isDeepStrictEqual(saved.payload, input)) throw new Error('Saved native inputs changed');
  if (saved?.status === 'success') {
    const result = outputSchema.parse(saved.result);
    if (reply !== undefined && !isDeepStrictEqual(reply, result.receipt)) throw new Error('Completed native receipt differs');
    await nativeCheck(input, 'after');
    return { status: 'success', result, reused: true, run_id: input.run_id, request_sha256: result.request_sha256 };
  }
  if (saved && saved.status !== 'suspended') throw new Error('Retain failed state; reconcile the effect before a new reviewed run');
  if (saved && reply === undefined) {
    await nativeCheck(input, 'before');
    const step = saved.steps?.['native-preflight'];
    if (!step || Array.isArray(step)) throw new Error('Missing saved preflight');
    const pending = checkedSchema.parse(step.output);
    return { status: 'suspended', run_id: input.run_id, request_sha256: pending.request_sha256, pending };
  }
  if (!saved && reply !== undefined) throw new Error('A native reply requires an existing suspended run');
  const run = await workflow.createRun({ runId: input.run_id });
  const result = saved ? await run.resume({ step: 'native-effect', resumeData: replySchema.parse(reply) })
    : await run.start({ inputData: input });
  const before = result.steps['native-preflight'];
  const captured = before?.status === 'success' ? checkedSchema.parse(before.output) : undefined;
  return { status: result.status, run_id: input.run_id, request_sha256: captured?.request_sha256,
    pending: result.status === 'suspended' ? captured : undefined,
    result: result.status === 'success' ? result.result : undefined,
    receipt: reply, error: result.status === 'failed' ? result.error.message : undefined };
}

function argumentsFor(args: string[]) {
  const [request, ...tail] = args;
  if (!request || tail.length % 2) throw new Error('Use an envelope, --write-root ROOT and --state STATE');
  const options = new Map<string, string>();
  for (let index = 0; index < tail.length; index += 2) {
    const key = tail[index], value = tail[index + 1];
    if (!key || !value || !['--write-root', '--state', '--reply', '--pending-body-review'].includes(key) || options.has(key))
      throw new Error('Unknown or duplicate native-loop option');
    options.set(key, value);
  }
  const root = options.get('--write-root'), state = options.get('--state');
  if (!root || !state || ![request, root, state, options.get('--reply') ?? request].every(isAbsolute))
    throw new Error('Use absolute input, root, state and reply paths');
  return { request, root, state, reply: options.get('--reply'), pending: options.get('--pending-body-review') };
}

async function checkState(state: string, root: string) {
  for (const path of [state, root]) {
    const info = await lstat(path);
    if (!info.isDirectory() || info.isSymbolicLink() || await realpath(path) !== path)
      throw new Error('Use canonical real directories');
  }
  const info = await lstat(state);
  if ((info.mode & 0o077) !== 0 || info.uid !== process.getuid?.()) throw new Error('State must be private and owned by this caller');
  const part = relative(root, state);
  if (part !== '..' && !part.startsWith('..' + sep) && !isAbsolute(part))
    throw new Error('Keep native workflow state outside the mutation root');
}

const help = `Usage: mise run ledger -- --native-loop ENVELOPE --write-root ROOT --state STATE
Optional: --reply RESPONSE and --pending-body-review SHA256.
Use absolute paths. ENVELOPE has run_id, turn, baseline, iteration and request.
Request is the existing native-file before contract. It grants no authority.
The first call checks inputs, saves the run and returns the pending operation.
Read that output, perform the authorized native effect, then resume the same run.
RESPONSE has run_id, request_sha256, tool, status and result.
Status is success, error or interrupted. Tool results are declarations, not acceptance.
Readback must match exact requested bytes, modes or absence.
Retain failed runs; inspect actual disk state before authorized recovery.
The state directory must be private, owned by this caller and outside the skill.
The lock protects each invocation, not the interval containing the native call.
Example: mise run ledger -- --native-loop /path/request.json --write-root /path/skill --state /path/state
Exit 0: readback passed; 1: rejected; 3: native effect needed. Goal acceptance stays pending.
`;

export async function runNativeHandoff(args: string[]) {
  if (args.length === 1 && args[0] === '--help') { process.stdout.write(help); return; }
  let storage, lock: string | undefined;
  try {
    const options = argumentsFor(args);
    await checkState(options.state, options.root);
    const candidate = join(options.state, '.native-handoff-lock');
    await mkdir(candidate, { mode: 0o700 }); lock = candidate;
    storage = await openStorage(options.state);
    const envelope = envelopeSchema.parse(await readThroughOwner('parse', new TextDecoder('utf-8', { fatal: true }).decode((await bound(options.request)).raw)));
    if (envelope.request.action !== 'native-file' || envelope.request.phase !== 'before')
      throw new Error('Native handoff requires the exact native-file before request');
    const input = inputSchema.parse({ ...envelope, root: options.root, ...(options.pending ? { pending: options.pending } : {}), runtime: await runtimeBindings() });
    const reply = options.reply ? await readThroughOwner('parse', new TextDecoder('utf-8', { fatal: true }).decode((await bound(options.reply)).raw)) : undefined;
    const result = await executeHandoff(createHandoff(storage), input, reply);
    process.stdout.write(JSON.stringify({ ...result, execution_acceptance: 'pending',
      limit: 'Cooperative saved handoff only. No file mutation, permission, event authentication, cross-call isolation or goal acceptance. Retain failed effects and inspect disk before recovery.' }) + '\n');
    process.exitCode = result.status === 'success' ? 0 : result.status === 'suspended' ? 3 : 1;
  } catch (error) {
    process.stderr.write((error instanceof Error ? error.message : String(error)) + '\n');
    process.exitCode = 1;
  } finally {
    await storage?.close();
    if (lock) await rmdir(lock);
  }
}
