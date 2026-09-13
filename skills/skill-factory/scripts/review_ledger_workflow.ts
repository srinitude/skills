/** Native ledger reads and caller-scoped file writes; semantic acceptance remains separate. */
import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { lstat, readFile } from 'node:fs/promises';
import { isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createStep, createWorkflow } from '@mastra/core/workflows';
import { z } from 'zod';

const reader = fileURLToPath(new URL('./review_ledger.py', import.meta.url));
const bodyPath = fileURLToPath(new URL('../SKILL.md', import.meta.url));
const digest = z.string().regex(/^[a-f0-9]{64}$/);
const sourceBinding = z.object({
  path: z.string().min(1).refine(isAbsolute, 'Use an absolute source path'), sha256: digest,
}).strict();
function fieldIssue(request: Record<string, unknown>, context: z.RefinementCtx, field: string, used: boolean, required: boolean) {
  if (used && required && request[field] === undefined)
    context.addIssue({ code: 'custom', message: `${request.action} requires ${field}` });
  if (!used && request[field] !== undefined)
    context.addIssue({ code: 'custom', message: `${field} does not apply to ${request.action}` });
}

export const requestSchema = z.object({
  action: z.enum(['catalog', 'show', 'relations', 'trace', 'check-capture', 'check-sources', 'pairs', 'selections', 'work', 'impact', 'file-graph', 'write-file', 'native-file']),
  phase: z.enum(['before', 'after']).optional(),
  ledger: z.string().min(1).refine(isAbsolute, 'Use an absolute ledger path'),
  ledger_sha256: digest,
  expected_documents: z.array(sourceBinding.extend({ name: z.string().min(1) }).strict()).min(1).optional(),
  original_source: sourceBinding.optional(),
  inventory_document: z.string().min(1).optional(),
  initial_body_review: sourceBinding.optional(),
  bootstrap_body: z.object({ body: sourceBinding, review: sourceBinding }).strict().optional(),
  body_revision: z.object({ previous: sourceBinding.nullable(), review: sourceBinding }).strict().optional(),
  change: z.object({
    path: z.string().min(1), expected_sha256: digest.nullable(), new_file: sourceBinding.nullable(),
    operation: z.enum(['add', 'update', 'delete']).optional(),
    body_sha256: digest, reviewer: z.string().min(1), review: z.record(z.string(), z.string().min(1)),
    mode: z.object({ expected: z.number().int().min(0).max(0o777).nullable(),
      new: z.number().int().min(0).max(0o777).nullable() }).strict().optional(),
  }).strict().optional(),
  selector: z.string().min(1).optional(),
  direction: z.enum(['in', 'out', 'both']).optional(),
  relation_type: z.string().min(1).optional(),
  depth: z.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER).optional(),
  scope: z.enum(['all', 'rules']).optional(),
  offset: z.string().regex(/^(0|[1-9][0-9]*)$/).optional(),
  limit: z.number().int().positive().max(Number.MAX_SAFE_INTEGER).optional(),
  budget: z.number().int().positive().max(Number.MAX_SAFE_INTEGER).optional(),
  selection: z.object({
    members: z.array(z.string().min(1)),
    size: z.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER),
    order: z.enum(['ordered', 'unordered']), repeats: z.boolean(),
    budget: z.number().int().positive().max(Number.MAX_SAFE_INTEGER),
  }).strict().optional(),
}).strict().superRefine((request, context) => {
  const rules = [
    { fields: ['expected_documents', 'original_source', 'inventory_document'], actions: ['check-sources', 'write-file', 'native-file'], required: true },
    { fields: ['change'], actions: ['write-file', 'native-file'], required: true },
    { fields: ['initial_body_review', 'bootstrap_body', 'body_revision'], actions: ['write-file', 'native-file'], required: false },
    { fields: ['phase'], actions: ['native-file'], required: true },
    { fields: ['selector'], actions: ['show', 'relations', 'trace', 'work', 'impact'], required: true },
    { fields: ['direction', 'relation_type'], actions: ['relations', 'trace'], required: false },
    { fields: ['depth'], actions: ['trace'], required: false },
    { fields: ['scope'], actions: ['pairs'], required: true },
    { fields: ['budget'], actions: ['pairs', 'file-graph'], required: true },
    { fields: ['selection'], actions: ['selections'], required: true },
    { fields: ['offset', 'limit'], actions: ['pairs', 'selections'], required: true },
  ] as const;
  for (const rule of rules) {
    const used = rule.actions.some(action => action === request.action);
    for (const field of rule.fields) {
      fieldIssue(request, context, field, used, rule.required);
    }
  }
  if (request.action === 'write-file' && request.change && (request.change.operation !== undefined
    || request.change.new_file === null || request.change.mode?.new === null))
    context.addIssue({ code: 'custom', message: 'write-file requires replacement bytes and rejects native operation fields' });
});
const bodySchema = z.object({ path: z.string(), sha256: digest, text: z.string().min(1) });
const capturedSchema = z.object({ request: requestSchema, body: bodySchema, ledger_text: z.string(), ledger_bytes: z.number().int().nonnegative() });
const viewSchema = z.object({ view_text: z.string(), source_sha256: digest }).strict();
const resultSchema = z.object({
  body: bodySchema, ledger: z.object({ path: z.string(), sha256: digest, bytes: z.number() }),
  view_text: z.string(), source_sha256: digest, execution_acceptance: z.literal('pending'),
  coverage: z.enum(['recorded context, relationships and source checks only', 'bound non-body file write only', 'bound body revision only', 'bound native file check only']), limit: z.string(),
});

function pipeError(error: NodeJS.ErrnoException, reject: (reason?: unknown) => void) {
  if (error.code !== 'EPIPE') reject(error);
}

function finishRead(code: number | null, stdout: Buffer[], stderr: Buffer[], accept: (value: unknown) => void, reject: (reason?: unknown) => void) {
  if (code !== 0) return reject(new Error(Buffer.concat(stderr).toString() || `Ledger reader exited ${code}`));
  try { accept(JSON.parse(Buffer.concat(stdout).toString())); } catch (error) { reject(error); }
}

export function readThroughOwner(operation: 'parse' | 'view' | 'write' | 'native-before' | 'native-after', input: string, writeRoot?: string, pendingBodyReview?: string): Promise<unknown> {
  return new Promise((accept, reject) => {
    const args = [reader, operation, ...(writeRoot === undefined ? [] : ['--write-root', writeRoot]),
      ...(pendingBodyReview === undefined ? [] : ['--pending-body-review', pendingBodyReview])];
    const child = spawn('python3', args, { stdio: ['pipe', 'pipe', 'pipe'] });
    const stdout: Buffer[] = [], stderr: Buffer[] = [];
    child.stdout.on('data', (chunk: Buffer) => stdout.push(chunk));
    child.stderr.on('data', (chunk: Buffer) => stderr.push(chunk));
    child.on('error', reject);
    child.stdin.on('error', (error: NodeJS.ErrnoException) => pipeError(error, reject));
    child.on('close', code => finishRead(code, stdout, stderr, accept, reject));
    child.stdin.end(input);
  });
}

async function capture(path: string, expected?: string) {
  const metadata = await lstat(path);
  if (!metadata.isFile() || metadata.isSymbolicLink()) throw new Error('Expected a regular input file');
  const raw = await readFile(path);
  const sha256 = createHash('sha256').update(raw).digest('hex');
  if (expected !== undefined && sha256 !== expected) throw new Error('Ledger digest differs from required current input');
  const text = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true }).decode(raw);
  if (!text.trim()) throw new Error('Expected nonempty UTF-8 input');
  return { path, sha256, text, bytes: raw.length };
}

const captureInputs = createStep({
  id: 'capture-current-body-and-ledger', inputSchema: requestSchema, outputSchema: capturedSchema,
  execute: async ({ inputData: request }) => {
    const body = await capture(bodyPath);
    const ledger = await capture(request.ledger, request.ledger_sha256);
    return { request, body, ledger_text: ledger.text, ledger_bytes: ledger.bytes };
  },
});
const buildView = createStep({
  id: 'build-asserted-relationship-view', inputSchema: capturedSchema, outputSchema: resultSchema,
  execute: async ({ inputData }) => {
    const { request, body, ledger_text, ledger_bytes } = inputData;
    const view = viewSchema.parse(await readThroughOwner('view', JSON.stringify({ request, ledger_text })));
    return { body, ledger: { path: request.ledger, sha256: request.ledger_sha256, bytes: ledger_bytes }, ...view,
      execution_acceptance: 'pending' as const, coverage: 'recorded context, relationships and source checks only' as const,
      limit: 'Selected read/check action over exact full ledger/body capture. Capture checks validate present document bytes and source/clause locators. Source checks also compare supplied live original/document bindings and the frozen coverage inventory; the caller must establish their independent authority. Read views retain recorded source-parent/review-inheritance context and asserted/declared reachability. Preserve conditions, review states, conjunctions and original endpoints; reachability is not transitive truth. File baselines and history remain distinct from recorded current package observations, which are not live file proof. A declared versioned profile adds captured source structure and reading order. Version-2 TOML task observations expose whole declarations, same-file literal references, unresolved forms and conditional dependency/run edges bound to the recorded current file hash. Native task resolution and execution remain separate; other derived relationships remain incomplete. Candidate pages use explicit scopes or selected known IDs, exact decimal ranks/counts, declared order/repetition and work budgets. Direct ranking avoids prefix scans; candidates stay unreviewed and do not replace higher-order relationship records, complete matrix inventories or their actual use. Work and impact views retain complete recorded review steps, fields, body decisions and mechanism owners beside source/inherited relationship context. Recorded states remain observations; these views perform no work or invalidation. The full ledger still governs. No semantic review, model use, protected write, durable recovery or final acceptance. The capture has no cross-file transaction or hostile-writer isolation.',
    };
  },
});
const workflow = createWorkflow({
  id: 'review-ledger-relationships', inputSchema: requestSchema, outputSchema: resultSchema,
  options: { validateInputs: true },
}).then(captureInputs).then(buildView).commit();

function writeWorkflow(root: string, pendingBodyReview?: string, nativePhase?: 'before' | 'after') {
  const operation = nativePhase ? `native-${nativePhase}` as const : 'write';
  const inputSchema = z.object({ request: requestSchema, body: bodySchema });
  const captureBody = createStep({
    id: 'capture-write-body', inputSchema: requestSchema, outputSchema: inputSchema,
    execute: async ({ inputData }) => ({ request: inputData, body: await capture(bodyPath) }),
  });
  const applyFile = createStep({
    id: nativePhase ? 'check-bound-native-file' : 'apply-bound-file-change', inputSchema, outputSchema: resultSchema,
    execute: async ({ inputData: { request, body } }) => {
      const result = viewSchema.extend({ ledger_bytes: z.number().int().nonnegative() }).parse(
        await readThroughOwner(operation, JSON.stringify(request), root, pendingBodyReview));
      return { body, ledger: { path: request.ledger, sha256: request.ledger_sha256, bytes: result.ledger_bytes },
        view_text: result.view_text, source_sha256: result.source_sha256,
        execution_acceptance: 'pending' as const, coverage: nativePhase ? 'bound native file check only' as const : request.body_revision ? 'bound body revision only' as const : 'bound non-body file write only' as const,
        limit: nativePhase ? 'Read-only native preflight/readback through the shared owner. No effect, hook activation, authorization or acceptance. See view_text for exact limits.' : 'The caller selected the write root outside request data. The file owner reads the full current '
          + 'ledger, target body and supplied governing inputs before and after this create/replacement. '
          + 'Review fields remain caller declarations. This does not guard other writers or confer source '
          + 'authority, semantic or human acceptance. See the returned per-file restoration and isolation limits.' };
    },
  });
  return createWorkflow({ id: nativePhase ? 'review-ledger-native-check' : 'review-ledger-file-write', inputSchema: requestSchema,
    outputSchema: resultSchema, options: { validateInputs: true },
  }).then(captureBody).then(applyFile).commit();
}

export async function runLedger(input: unknown, writeRoot?: string, pendingBodyReview?: string) {
  const request = requestSchema.parse(input);
  const writing = request.action === 'write-file' || request.action === 'native-file';
  if (writing && (writeRoot === undefined || !isAbsolute(writeRoot)))
    throw new Error('write-file requires a caller-selected absolute --write-root');
  if (!writing && writeRoot !== undefined) throw new Error('Read actions reject --write-root');
  if (pendingBodyReview !== undefined && (!writing || !/^[a-f0-9]{64}$/.test(pendingBodyReview)))
    throw new Error('Pending body review requires a write and an exact lowercase SHA-256');
  const selected = writing ? writeWorkflow(writeRoot as string, pendingBodyReview, request.phase) : workflow;
  const run = await selected.createRun();
  return { ...await run.start({ inputData: request }), run_id: run.runId };
}
