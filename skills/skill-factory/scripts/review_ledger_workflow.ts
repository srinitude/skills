/** Native read-only ledger operation. It cannot grant semantic or execution acceptance. */
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
export const requestSchema = z.object({
  action: z.enum(['catalog', 'show', 'relations', 'trace']),
  ledger: z.string().min(1).refine(isAbsolute, 'Use an absolute ledger path'),
  ledger_sha256: digest,
  selector: z.string().min(1).optional(),
  direction: z.enum(['in', 'out', 'both']).optional(),
  relation_type: z.string().min(1).optional(),
  depth: z.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER).optional(),
}).strict().superRefine((request, context) => {
  if (request.action !== 'catalog' && !request.selector)
    context.addIssue({ code: 'custom', message: 'This action requires a selector' });
  for (const field of ['direction', 'relation_type', 'depth'] as const) {
    if (request[field] !== undefined && !['relations', 'trace'].includes(request.action))
      context.addIssue({ code: 'custom', message: `${field} needs a relationship action` });
  }
  if (request.depth !== undefined && request.action !== 'trace')
    context.addIssue({ code: 'custom', message: 'depth requires trace' });
});
const bodySchema = z.object({ path: z.string(), sha256: digest, text: z.string().min(1) });
const capturedSchema = z.object({ request: requestSchema, body: bodySchema, ledger_text: z.string(), ledger_bytes: z.number().int().nonnegative() });
const viewSchema = z.object({ view_text: z.string(), source_sha256: digest }).strict();
const resultSchema = z.object({
  body: bodySchema, ledger: z.object({ path: z.string(), sha256: digest, bytes: z.number() }),
  view_text: z.string(), source_sha256: digest, execution_acceptance: z.literal('pending'),
  coverage: z.literal('asserted relationships and recorded context only'), limit: z.string(),
});

export function readThroughOwner(operation: 'parse' | 'view', input: string): Promise<unknown> {
  return new Promise((accept, reject) => {
    const child = spawn('python3', [reader, operation], { stdio: ['pipe', 'pipe', 'pipe'] });
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
      execution_acceptance: 'pending' as const, coverage: 'asserted relationships and recorded context only' as const,
      limit: 'Exact full ledger/body capture, recorded source-parent/review-inheritance context and asserted-edge reachability. Preserve conditions, review states, conjunctions and original endpoints; reachability is not transitive truth. File baselines and history remain distinct from recorded current package observations, which are not live file proof. Derived source, reading and task relationships remain incomplete. The full ledger still governs. No live source verification, semantic review, model use, protected write, durable recovery or final acceptance. The capture has no cross-file transaction or hostile-writer isolation.',
    };
  },
});
const workflow = createWorkflow({
  id: 'review-ledger-relationships', inputSchema: requestSchema, outputSchema: resultSchema,
  options: { validateInputs: true },
}).then(captureInputs).then(buildView).commit();

export async function runLedger(input: unknown) {
  const request = requestSchema.parse(input);
  const run = await workflow.createRun();
  return { ...await run.start({ inputData: request }), run_id: run.runId };
}
