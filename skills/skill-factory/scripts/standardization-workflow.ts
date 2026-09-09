import { execFile } from 'node:child_process';
import { createHash } from 'node:crypto';
import { lstat, readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';
import { z } from 'zod';

process.env.MASTRA_TELEMETRY_DISABLED = '1';
const { createStep, createWorkflow } = await import('@mastra/core/workflows');
const executeFile = promisify(execFile);
export const factory = fileURLToPath(new URL('../', import.meta.url));
const digest = z.string().regex(/^[a-f0-9]{64}$/);
export const requestSchema = z.object({
  source: z.string().min(1), profile: z.string().min(1), candidate: z.string().min(1),
  scope: z.enum(['user', 'project']), audience: z.enum(['human', 'agent']),
  implementation: z.string().startsWith('sha256:'),
}).strict();
const frozenSchema = requestSchema.extend({
  baseline_digest: z.string().startsWith('sha256:'), profile_sha256: digest,
});
const inputsSchema = z.object({
  source: digest, profile: digest, scope: z.enum(['user', 'project']),
  audience: z.enum(['human', 'agent']),
}).strict();
export const preparedSchema = frozenSchema.extend({
  candidate_digest: digest, candidate_baseline: z.string().startsWith('sha256:'),
  consumer_inputs: inputsSchema,
});
const resultSchema = z.object({
  domain_status: z.literal('accepted'), target: z.string(), sha256: digest,
  limit: z.string().min(1),
}).strict();
const resumeSchema = z.object({ decision: z.enum(['continue', 'reject']) }).strict();
type Frozen = z.infer<typeof frozenSchema>;
type Prepared = z.infer<typeof preparedSchema>;

async function leaf(script: string, args: string[]) {
  const { stdout } = await executeFile('uv',
    ['run', '--with', 'PyYAML==6.0.3', 'python', factory + 'scripts/' + script, ...args],
    { cwd: factory, timeout: 60000, maxBuffer: 8 * 1024 * 1024 });
  return JSON.parse(stdout) as unknown;
}

export async function baseline(root: string) {
  const result = await leaf('plan_standardize.py', [root]);
  return z.object({ baseline_digest: z.string().startsWith('sha256:') }).parse(result).baseline_digest;
}

async function profileDigest(path: string) {
  const entry = await lstat(path);
  if (!entry.isFile() || entry.isSymbolicLink()) throw new Error('Profile must be a regular file');
  return createHash('sha256').update(await readFile(path)).digest('hex');
}

function argumentsFor(input: Frozen) {
  return [input.source, '--profile', input.profile, '--scope', input.scope, '--audience', input.audience];
}

async function fresh(input: Frozen) {
  if (await baseline(factory) !== input.implementation) throw new Error('Workflow implementation changed');
  if (await baseline(input.source) !== input.baseline_digest) throw new Error('Original skill changed');
  if (await profileDigest(input.profile) !== input.profile_sha256) throw new Error('Domain profile changed');
}

async function freeze(input: z.infer<typeof requestSchema>) {
  const result = frozenSchema.parse({ ...input, baseline_digest: await baseline(input.source),
    profile_sha256: await profileDigest(input.profile) });
  await fresh(result);
  return result;
}

async function prepare(input: Frozen) {
  await fresh(input);
  const result = z.object({
    acceptance: z.literal('pending'), sha256: digest, consumer_inputs: inputsSchema,
  }).parse(await leaf('standardize_registry_skill.py',
    [...argumentsFor(input), '--prepare', input.candidate]));
  await fresh(input);
  return preparedSchema.parse({ ...input, candidate_digest: result.sha256,
    candidate_baseline: await baseline(input.candidate), consumer_inputs: result.consumer_inputs });
}

async function promote(input: Prepared, bindings: string[]) {
  await preflight(input, bindings);
  const result = z.object({ acceptance: z.literal('passed'), limit: z.string() }).parse(
    await leaf('standardize_registry_skill.py',
      [...argumentsFor(input), '--apply', '--candidate', input.candidate, ...bindings]));
  if (await baseline(input.source) !== await baseline(input.candidate)) {
    throw new Error('Delivered skill differs from the reviewed candidate');
  }
  return resultSchema.parse({ domain_status: 'accepted', target: input.source,
    sha256: input.candidate_digest, limit: result.limit });
}

export async function preflight(input: Prepared, bindings: string[]) {
  await fresh(input);
  if (await baseline(input.candidate) !== input.candidate_baseline) throw new Error('Reviewed candidate changed');
  z.object({ acceptance: z.literal('pending'), evidence_readiness: z.literal('passed') }).parse(
    await leaf('standardize_registry_skill.py',
      [...argumentsFor(input), '--check-candidate', '--candidate', input.candidate, ...bindings]));
}

export async function savedInput(context: unknown, input: z.infer<typeof requestSchema>, bindings?: string[]) {
  const saved = z.object({ input: requestSchema,
    'prepare-candidate': z.object({ output: preparedSchema }) }).parse(context);
  if (JSON.stringify(saved.input) !== JSON.stringify(input)) throw new Error('Saved run inputs or implementation changed');
  if (bindings) await preflight(saved['prepare-candidate'].output, bindings);
}

export function standardizationWorkflow(bindings: string[]) {
  return createWorkflow({
    id: 'skill-factory-standardization-v1', inputSchema: requestSchema, outputSchema: resultSchema,
    retryConfig: { attempts: 0, delay: 0 },
  }).then(createStep({
    id: 'freeze-source', inputSchema: requestSchema, outputSchema: frozenSchema,
    execute: async ({ inputData }) => freeze(requestSchema.parse(inputData)),
  })).then(createStep({
    id: 'prepare-candidate', inputSchema: frozenSchema, outputSchema: preparedSchema,
    execute: async ({ inputData }) => prepare(frozenSchema.parse(inputData)),
  })).then(createStep({
    id: 'review-candidate', inputSchema: preparedSchema, outputSchema: preparedSchema,
    suspendSchema: z.object({ artifact: z.string(), question: z.string() }), resumeSchema,
    execute: async ({ inputData, resumeData, suspend }) => {
      const input = preparedSchema.parse(inputData);
      if (!resumeData) return suspend({ artifact: input.candidate,
        question: 'Review this prepared skill against its complete source and required evidence.' });
      if (resumeSchema.parse(resumeData).decision === 'reject') throw new Error('Candidate rejected');
      await fresh(input);
      return input;
    },
  })).then(createStep({
    id: 'promote-candidate', inputSchema: preparedSchema, outputSchema: resultSchema,
    execute: async ({ inputData }) => promote(preparedSchema.parse(inputData), bindings),
  })).commit();
}
