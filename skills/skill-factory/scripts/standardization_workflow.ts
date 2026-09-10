/** Reviewed domain operation. Native Python owns validation and every package effect. */
import { createHash, randomUUID } from 'node:crypto';
import { spawn } from 'node:child_process';
import { readFile, writeFile, lstat, realpath } from 'node:fs/promises';
import { isAbsolute, join, relative, sep } from 'node:path';
import { createStep, createWorkflow } from '@mastra/core/workflows';
import { Mastra } from '@mastra/core/mastra';
import { InMemoryStore, type MastraCompositeStore } from '@mastra/core/storage';
import { z } from 'zod';

export const digest = (raw: Uint8Array) => createHash('sha256').update(raw).digest('hex');
const path = z.string().min(1).refine(isAbsolute);
const hash = z.string().regex(/^[a-f0-9]{64}$/);
export const inputSchema = z.object({ target: path, profile: path, scope: z.enum(['user', 'project']).optional(),
  rebase_tracked_text: z.boolean().optional(), placement_receipt: path.optional() }).strict();
const planBinding = z.object({ plan_path: path, plan_sha256: hash }).strict();
export const preparedSchema = inputSchema.extend(planBinding.shape).strict();
const resumedSchema = z.discriminatedUnion('decision', [
  z.object({ decision: z.literal('reject') }).strict(),
  z.object({ decision: z.literal('continue'), plan_sha256: hash, review_path: path, review_sha256: hash }).strict(),
]);
const reviewedSchema = preparedSchema.extend({ review_path: path, review_sha256: hash }).strict();
const appliedSchema = z.object({ target: path, mode: z.literal('apply'), writes: z.number().int().nonnegative(),
  changed: z.array(z.string()), file_writes: z.array(z.unknown()), execution_acceptance: z.literal('pending') }).passthrough();
type Input = z.infer<typeof inputSchema>;
type Reviewed = z.infer<typeof reviewedSchema>;
export type Runtime = { factory: string; state: string; environment: { UV_PYTHON: string } };
export type NativeResult = { code: number | null; stdout: string; stderr: string };
type Options = { storage?: MastraCompositeStore; preparedPlan?: z.infer<typeof planBinding>;
  onNativeResult?: (result: NativeResult) => void };

const outside = (root: string, target: string) => {
  const value = relative(root, target);
  return value === '..' || value.startsWith('..' + sep) || isAbsolute(value);
};

export async function workflowRoots(runtime: Runtime, target?: string) {
  if (!isAbsolute(runtime.environment.UV_PYTHON)) throw new Error('Use the Mise-resolved Python path');
  for (const value of [runtime.factory, runtime.state]) {
    if (!isAbsolute(value)) throw new Error('Runtime roots must be absolute real directories');
    const metadata = await lstat(value);
    if (!metadata.isDirectory() || metadata.isSymbolicLink()) throw new Error('Runtime roots must be real directories');
  }
  const factory = await realpath(runtime.factory), state = await realpath(runtime.state);
  if (!outside(factory, state)) throw new Error('Workflow state must be outside the factory');
  if (target !== undefined && !outside(await realpath(target), state)) throw new Error('Workflow state must be outside the target');
  return { factory, state };
}

export async function bound(file: string, expected?: string) {
  const metadata = await lstat(file);
  if (!metadata.isFile() || metadata.isSymbolicLink()) throw new Error('Expected a regular bound input');
  const raw = await readFile(file), sha256 = digest(raw);
  if (expected !== undefined && sha256 !== expected) throw new Error('Changed workflow input: ' + file);
  return { raw, sha256 };
}

function nativeArguments(runtime: Runtime, value: Input | Reviewed, apply: boolean) {
  const args = ['run', '--no-project', '--isolated', '--no-python-downloads', '--with', 'PyYAML==6.0.3',
    join(runtime.factory, 'scripts/standardize_registry_skill.py'), value.target, '--profile', value.profile];
  if (value.scope !== undefined) args.push('--scope', value.scope);
  if (value.rebase_tracked_text) args.push('--rebase-tracked-text');
  if (value.placement_receipt !== undefined) args.push('--placement-receipt', value.placement_receipt);
  if (apply) { const reviewed = reviewedSchema.parse(value); args.push('--apply', '--plan-file', reviewed.plan_path, '--review', reviewed.review_path); }
  return args;
}

async function finishOperation(runtime: Runtime, args: string[], started: number, result: NativeResult, notify?: Options['onNativeResult']) {
  notify?.(result);
  await writeFile(join(runtime.state, randomUUID() + '-native-command.json'), JSON.stringify({
    command: ['uv', ...args], cwd: runtime.factory, python: runtime.environment.UV_PYTHON,
    elapsed_ms: performance.now() - started, exit_code: result.code, stdout: result.stdout,
    stderr: result.stderr, execution_acceptance: 'pending',
  }), { flag: 'wx', mode: 0o600 });
  if (result.code !== 0) throw new Error(result.stderr || `Standardization exited ${result.code}`);
  return JSON.parse(result.stdout) as unknown;
}

function operation(runtime: Runtime, value: Input | Reviewed, apply: boolean, signal: AbortSignal | undefined, notify?: Options['onNativeResult']): Promise<unknown> {
  const args = nativeArguments(runtime, value, apply), started = performance.now();
  return new Promise((accept, reject) => {
    const child = spawn('uv', args, { cwd: runtime.factory, env: { ...process.env, ...runtime.environment },
      stdio: ['ignore', 'pipe', 'pipe'], signal });
    const output: Buffer[] = [], errors: Buffer[] = [];
    child.stdout.on('data', (chunk: Buffer) => output.push(chunk));
    child.stderr.on('data', (chunk: Buffer) => errors.push(chunk));
    child.on('error', reject);
    child.on('close', code => {
      const result = { code, stdout: Buffer.concat(output).toString(), stderr: Buffer.concat(errors).toString() };
      void finishOperation(runtime, args, started, result, notify).then(accept, reject);
    });
  });
}

function steps(runtime: Runtime, options: Options) {
  const prepare = createStep({ id: 'prepare-standardization', inputSchema, outputSchema: preparedSchema,
    execute: async ({ inputData, abortSignal }) => {
      await workflowRoots(runtime, inputData.target);
      if (options.preparedPlan) {
        const binding = planBinding.parse(options.preparedPlan);
        await bound(binding.plan_path, binding.plan_sha256);
        return { ...inputData, ...binding };
      }
      const result = z.object({ mode: z.literal('plan'), writes: z.literal(0), plan: z.object({
        execution_acceptance: z.literal('pending') }).passthrough() }).passthrough().parse(
          await operation(runtime, inputData, false, abortSignal, options.onNativeResult));
      const raw = Buffer.from(JSON.stringify(result)), plan_path = join(runtime.state, randomUUID() + '-plan.json');
      await writeFile(plan_path, raw, { flag: 'wx', mode: 0o600 });
      return { ...inputData, plan_path, plan_sha256: digest(raw) };
    } });
  const review = createStep({ id: 'review-standardization', inputSchema: preparedSchema, outputSchema: reviewedSchema,
    resumeSchema: resumedSchema, suspendSchema: preparedSchema,
    execute: async ({ inputData, resumeData, suspend }) => {
      if (!resumeData) return await suspend(inputData);
      const reply = resumedSchema.parse(resumeData);
      if (reply.decision === 'reject') throw new Error('Standardization review rejected');
      if (reply.plan_sha256 !== inputData.plan_sha256) throw new Error('Review refers to another plan');
      await bound(inputData.plan_path, inputData.plan_sha256);
      await bound(reply.review_path, reply.review_sha256);
      return { ...inputData, review_path: reply.review_path, review_sha256: reply.review_sha256 };
    } });
  const apply = createStep({ id: 'apply-reviewed-standardization', inputSchema: reviewedSchema, outputSchema: appliedSchema,
    execute: async ({ inputData, abortSignal }) => {
      const planned = JSON.parse((await bound(inputData.plan_path, inputData.plan_sha256)).raw.toString());
      await bound(inputData.review_path, inputData.review_sha256);
      const result = appliedSchema.parse(await operation(runtime, inputData, true, abortSignal, options.onNativeResult));
      for (const item of planned.plan.files) {
        const target = join(inputData.target, item.path), raw = await readFile(target);
        if (!raw.equals(Buffer.from(item.content_base64, 'base64')) || ((await lstat(target)).mode & 0o777) !== item.mode)
          throw new Error('Applied target differs from the exact reviewed plan: ' + item.path);
      }
      return result;
    } });
  return { prepare, review, apply };
}

export async function createStandardizationWorkflow(runtime: Runtime, options: Options = {}) {
  runtime = { ...runtime, ...await workflowRoots(runtime) };
  const { prepare, review, apply } = steps(runtime, options);
  const workflow = createWorkflow({ id: 'standardize-reviewed-package', inputSchema, outputSchema: appliedSchema,
    options: { validateInputs: true, autoRestartActiveRuns: false } }).then(prepare).then(review).then(apply).commit();
  const mastra = new Mastra({ workflows: { standardize: workflow },
    storage: options.storage ?? new InMemoryStore({ id: 'temporary-domain-workflow' }), logger: false });
  return { workflow: mastra.getWorkflow('standardize'), reviewStep: review };
}
