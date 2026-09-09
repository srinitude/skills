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
export const requestSchema = z.object({
  action: z.enum(['catalog', 'show', 'relations', 'trace', 'check-capture', 'check-sources', 'pairs', 'selections', 'work', 'impact', 'write-file']),
  ledger: z.string().min(1).refine(isAbsolute, 'Use an absolute ledger path'),
  ledger_sha256: digest,
  expected_documents: z.array(sourceBinding.extend({ name: z.string().min(1) }).strict()).min(1).optional(),
  original_source: sourceBinding.optional(),
  inventory_document: z.string().min(1).optional(),
  bootstrap_body: z.object({ body: sourceBinding, review: sourceBinding }).strict().optional(),
  change: z.object({
    path: z.string().min(1), expected_sha256: digest.nullable(), new_file: sourceBinding,
    body_sha256: digest, reviewer: z.string().min(1), review: z.record(z.string(), z.string().min(1)),
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
    { fields: ['expected_documents', 'original_source', 'inventory_document'], actions: ['check-sources', 'write-file'], required: true },
    { fields: ['change'], actions: ['write-file'], required: true },
    { fields: ['bootstrap_body'], actions: ['write-file'], required: false },
    { fields: ['selector'], actions: ['show', 'relations', 'trace', 'work', 'impact'], required: true },
    { fields: ['direction', 'relation_type'], actions: ['relations', 'trace'], required: false },
    { fields: ['depth'], actions: ['trace'], required: false },
    { fields: ['scope', 'budget'], actions: ['pairs'], required: true },
    { fields: ['selection'], actions: ['selections'], required: true },
    { fields: ['offset', 'limit'], actions: ['pairs', 'selections'], required: true },
  ] as const;
  for (const rule of rules) {
    const used = rule.actions.some(action => action === request.action);
    for (const field of rule.fields) {
      if (used && rule.required && request[field] === undefined)
        context.addIssue({ code: 'custom', message: `${request.action} requires ${field}` });
      if (!used && request[field] !== undefined)
        context.addIssue({ code: 'custom', message: `${field} does not apply to ${request.action}` });
    }
  }
});
const bodySchema = z.object({ path: z.string(), sha256: digest, text: z.string().min(1) });
const capturedSchema = z.object({ request: requestSchema, body: bodySchema, ledger_text: z.string(), ledger_bytes: z.number().int().nonnegative() });
const viewSchema = z.object({ view_text: z.string(), source_sha256: digest }).strict();
const resultSchema = z.object({
  body: bodySchema, ledger: z.object({ path: z.string(), sha256: digest, bytes: z.number() }),
  view_text: z.string(), source_sha256: digest, execution_acceptance: z.literal('pending'),
  coverage: z.enum(['recorded context, relationships and source checks only', 'bound non-body file write only']), limit: z.string(),
});

export function readThroughOwner(operation: 'parse' | 'view' | 'write', input: string, writeRoot?: string): Promise<unknown> {
  return new Promise((accept, reject) => {
    const args = [reader, operation, ...(writeRoot === undefined ? [] : ['--write-root', writeRoot])];
    const child = spawn('python3', args, { stdio: ['pipe', 'pipe', 'pipe'] });
    const stdout: Buffer[] = [], stderr: Buffer[] = [];
    child.stdout.on('data', (chunk: Buffer) => stdout.push(chunk));
    child.stderr.on('data', (chunk: Buffer) => stderr.push(chunk));
    child.on('error', reject);
    child.stdin.on('error', (error: NodeJS.ErrnoException) => { if (error.code !== 'EPIPE') reject(error); });
    child.on('close', code => {
      if (code !== 0) return reject(new Error(Buffer.concat(stderr).toString() || `Ledger reader exited ${code}`));
      try { accept(JSON.parse(Buffer.concat(stdout).toString())); } catch (error) { reject(error); }
    });
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

function writeWorkflow(root: string) {
  const inputSchema = z.object({ request: requestSchema, body: bodySchema });
  const captureBody = createStep({
    id: 'capture-write-body', inputSchema: requestSchema, outputSchema: inputSchema,
    execute: async ({ inputData }) => ({ request: inputData, body: await capture(bodyPath) }),
  });
  const applyFile = createStep({
    id: 'apply-bound-file-change', inputSchema, outputSchema: resultSchema,
    execute: async ({ inputData: { request, body } }) => {
      const result = viewSchema.extend({ ledger_bytes: z.number().int().nonnegative() }).parse(
        await readThroughOwner('write', JSON.stringify(request), root));
      return { body, ledger: { path: request.ledger, sha256: request.ledger_sha256, bytes: result.ledger_bytes },
        view_text: result.view_text, source_sha256: result.source_sha256,
        execution_acceptance: 'pending' as const, coverage: 'bound non-body file write only' as const,
        limit: 'The caller selected the write root outside request data. The file owner reads the full current '
          + 'ledger, target body and supplied governing inputs before and after this create/replacement. '
          + 'Review fields remain caller declarations. This does not guard other writers or confer source '
          + 'authority, semantic or human acceptance. See the returned per-file restoration and isolation limits.' };
    },
  });
  return createWorkflow({ id: 'review-ledger-file-write', inputSchema: requestSchema,
    outputSchema: resultSchema, options: { validateInputs: true },
  }).then(captureBody).then(applyFile).commit();
}

export async function runLedger(input: unknown, writeRoot?: string) {
  const request = requestSchema.parse(input);
  const writing = request.action === 'write-file';
  if (writing && (writeRoot === undefined || !isAbsolute(writeRoot)))
    throw new Error('write-file requires a caller-selected absolute --write-root');
  if (!writing && writeRoot !== undefined) throw new Error('Read actions reject --write-root');
  const selected = writing ? writeWorkflow(writeRoot as string) : workflow;
  const run = await selected.createRun();
  return { ...await run.start({ inputData: request }), run_id: run.runId };
}
