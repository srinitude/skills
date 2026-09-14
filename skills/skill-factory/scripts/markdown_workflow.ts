/** Each public Markdown task runs one guarded Mastra step. */
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { isDeepStrictEqual } from 'node:util';
import { dirname, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createStep, createWorkflow } from '@mastra/core/workflows';
import { Mastra } from '@mastra/core/mastra';
import type { MastraCompositeStore } from '@mastra/core/storage';
import { z } from 'zod';
import { bound, digest, taskContract, taskContractSchema } from './standardization_workflow.ts';
import { taskSnapshot } from './task_inventory.ts';

export const phases = ['inventory', 'mechanical', 'review-request', 'macro-review', 'micro-review', 'line-review', 'review-check', 'accept'] as const;
const text = z.string().trim().min(1), hash = z.string().regex(/^[a-f0-9]{64}$/);
const path = text.refine(isAbsolute);
const binding = z.object({ path, sha256: hash }).strict();
export const requestSchema = z.object({ run_id: text, turn: text, baseline: text,
  iteration: z.number().int().nonnegative(), obligation: text, roots: z.array(path).min(1),
  context: z.array(binding.extend({ role: z.enum(['source', 'body', 'ledger', 'graph', 'policy', 'render']), subject: path.optional() }).strict()).min(1),
}).strict();
const answer = z.object({ state: z.enum(['pass', 'fail', 'pending']), reason: text,
  citations: z.array(binding.extend({ quote: text.optional() }).strict()).min(1) }).strict();
export const questions = {
  capability_ownership: 'Does the model keep every task it does best, including creative judgment, meaning and perception with available tools? Cite which work code checks and humans own; check task and workflow creation too. Do all scripts and Mastra starts or resumes use declared Mise tasks? Does each skill file reach its required task as input and get used? Do code checks leave model-owned judgment with the model?',
  task_dependencies: 'For each new or changed Mise task, did the model trace inputs, setup, checks and consumers, then declare every needed task dependency? Cite the task and its review. If its list is empty, cite why it truly needs none. The model owns this judgment; a graph check alone cannot prove it.',
  purpose: 'Read the whole file. Does its purpose, coverage, order and reading experience serve its reader and skill?',
  structure: 'Do sections and blocks fit together, with sound form choices, spacing, transitions and no lost rule?',
  primitive_what: 'For each mapped Markdown feature, cite its meaning, syntax and valid example.',
  primitive_which: 'For each feature, cite the choice rule and compare the forms that fit this file.',
  primitive_when: 'For each feature, cite when to use or avoid it and the required target support.',
  primitive_how: 'For each feature, cite how to write, nest, escape, render and test it.',
  primitive_why: 'For each feature, explain its use for this reader and why no rule is lost.',
  primitive_who: 'For each feature, name the author, generator, checker, model and required human roles.',
  primitive_coverage: 'Trace the full named standards, variants and target extensions to the bound map; cite gaps and non-use.',
  meaning: 'Does each rule keep its actor, condition, exception and proof?',
  action: 'Can the reader tell what to do, when, why and how to check it?',
  language: 'Are words simple, terms defined and steps clear?',
  rendering: 'Did you inspect the page, links, images, tables and nesting?',
  first_load: 'Are rules needed at first use visible in SKILL.md?',
  integration: 'Does each file fit its source, callers and path to SKILL.md?',
  exclusions: 'Are score exclusions honest, with no lost or hidden rule?',
} as const;
export const stages = {
  'macro-review': ['capability_ownership', 'task_dependencies', 'purpose', 'primitive_which', 'primitive_why', 'primitive_who', 'primitive_coverage', 'action', 'first_load', 'integration'],
  'micro-review': ['structure', 'primitive_what', 'primitive_when', 'primitive_how', 'meaning', 'rendering'],
  'line-review': ['language', 'exclusions'],
} as const;
export const replySchema = z.object({ run_id: text, request_sha256: hash, reviewer: text,
  method: text, files: z.array(binding.extend({ answers: z.record(text, answer) }).strict()).min(1),
}).strict();
const checkedFile = binding.extend({ text: z.string(), failures: z.array(z.record(z.string(), z.unknown())) }).passthrough();
const reportSchema = z.object({ runtime: z.record(z.string(), z.unknown()), files: z.array(checkedFile).min(1),
  execution_acceptance: z.literal('pending') }).strict();
const contextSchema = binding.extend({ role: text, subject: path.optional(), text: z.string().optional() }).strict();
const outputSchema = z.object({ request: requestSchema, report: reportSchema, context: z.array(contextSchema),
  request_sha256: hash, reviews: z.record(text, replySchema).default({}), execution_acceptance: z.literal('pending') }).strict();
export type Request = z.infer<typeof requestSchema>;
type Output = z.infer<typeof outputSchema>;
type Phase = typeof phases[number];
const executeFile = promisify(execFile);
const packages = ['textstat==0.7.8', 'markdown-it-py==4.0.0', 'cmudict==1.1.3', 'pyphen==0.18.1',
  'mdurl==0.1.2', 'importlib_resources==7.1.0', 'importlib_metadata==9.0.1', 'zipp==4.1.0', 'setuptools==84.0.0'];

async function capture(request: Request): Promise<Output> {
  const args = ['run', '--no-project', '--isolated', '--no-python-downloads',
    ...packages.flatMap(value => ['--with', value]),
    fileURLToPath(new URL('./markdown_checks.py', import.meta.url)),
    ...request.roots.flatMap(value => ['--root', value])];
  let stdout: string;
  try { stdout = (await executeFile('uv', args, { maxBuffer: 64 * 1024 * 1024 })).stdout; }
  catch (error) {
    if (!error || typeof error !== 'object' || !('code' in error) || error.code !== 1 || !('stdout' in error)) throw error;
    stdout = String(error.stdout);
  }
  const report = reportSchema.parse(JSON.parse(stdout)), context = [];
  for (const item of request.context) {
    const raw = (await bound(item.path, item.sha256)).raw;
    context.push({ ...item, ...(['ledger', 'render'].includes(item.role) ? {} : { text: new TextDecoder('utf-8', { fatal: true }).decode(raw) }) });
  }
  const roles = new Set<string>(context.map(item => item.role));
  for (const role of ['source', 'body', 'ledger', 'graph', 'policy'])
    if (!roles.has(role)) throw new Error('Missing review context: ' + role);
  report.runtime.validator_files = Object.fromEntries(await Promise.all(
    ['markdown_workflow.ts', 'run_markdown.ts', 'standardization_workflow.ts', 'task_inventory.ts',
      'run_standardization.ts', '../package.json', '../package-lock.json', '../mise.toml'].map(async name =>
      [name, (await bound(fileURLToPath(new URL(name, import.meta.url)))).sha256])));
  report.runtime.task_revision = (await taskSnapshot(dirname(fileURLToPath(new URL('../mise.toml', import.meta.url))))).revision;
  const captured = { request, report, context };
  return { ...captured, reviews: {}, request_sha256: digest(Buffer.from(JSON.stringify(captured))), execution_acceptance: 'pending' };
}

export function validateReview(input: Output, value: unknown, phase: Phase = 'review-check') {
  const review = replySchema.parse(value);
  if (review.run_id !== input.request.run_id + ':' + phase || review.request_sha256 !== input.request_sha256)
    throw new Error('Review belongs to another run or file state');
  const expected = input.report.files.map(file => file.path).sort(), actual = review.files.map(file => file.path).sort();
  if (!isDeepStrictEqual(expected, actual)) throw new Error('Review must cover each file exactly once');
  for (const file of review.files) validateFileReview(input, file, phase);
  return review;
}

function validateFileReview(input: Output, file: z.infer<typeof replySchema>['files'][number], phase: Phase) {
  const keys: readonly string[] = phase in stages ? stages[phase as keyof typeof stages] : Object.keys(questions);
  if (!isDeepStrictEqual([...keys].sort(), Object.keys(file.answers).sort())) throw new Error('Review has wrong stage coverage');
  const current = input.report.files.find(item => item.path === file.path);
  if (!current || current.sha256 !== file.sha256) throw new Error('Review has stale file bytes');
  const render = file.answers.rendering?.citations.some(citation => input.context.some(item =>
    item.role === 'render' && item.subject === file.path && item.path === citation.path && item.sha256 === citation.sha256));
  if (keys.includes('rendering') && !render) throw new Error('Cite a bound render for this file');
  for (const [question, result] of Object.entries(file.answers)) {
    if (result.state !== 'pass') throw new Error('Review needs repair: ' + question + ' in ' + file.path);
    for (const citation of result.citations) validateCitation(input, citation, question);
  }
}

function validateCitation(input: Output, citation: z.infer<typeof answer>['citations'][number], question: string) {
  const source = [...input.report.files, ...input.context].find(item => item.path === citation.path && item.sha256 === citation.sha256);
  if (!source) throw new Error('Citation is not a bound input');
  if (question === 'rendering' && input.context.some(item => item.role === 'render' && item.path === citation.path)) return;
  if (!citation.quote || !source.text?.includes(citation.quote)) throw new Error('Citation must quote its exact source');
}

function checkMechanical(input: Output) {
  if (input.report.files.some(file => file.failures.length)) throw new Error('Fix the reported Markdown checks before acceptance');
}

async function predecessor(mastra: Mastra, phase: Phase, request: Request, current: Output) {
  const index = phases.indexOf(phase);
  if (index === 0) return current;
  const previous = mastra.getWorkflow('markdown-' + phases[index - 1]);
  const snapshot = await previous.getWorkflowRunById(request.run_id + ':' + phases[index - 1]);
  if (!snapshot || snapshot.status !== 'success') throw new Error('Required Markdown task has not passed');
  const prior = outputSchema.parse(snapshot.result);
  if (prior.request_sha256 !== current.request_sha256) throw new Error('Required Markdown proof is stale');
  return { ...current, reviews: prior.reviews };
}

function checkCompleteReviews(input: Output) {
  checkMechanical(input);
  for (const stage of Object.keys(stages) as (keyof typeof stages)[])
    validateReview(input, input.reviews[stage], stage);
}

function buildWorkflow(phase: Phase, owner: () => Mastra) {
  const step = createStep({ id: phase, inputSchema: requestSchema, outputSchema,
    resumeSchema: replySchema, suspendSchema: outputSchema.extend({ task: taskContractSchema }),
    execute: async ({ inputData, resumeData, suspend }) => {
      const index = phases.indexOf(phase), name = 'markdown:' + phase;
      const task = await taskContract(dirname(fileURLToPath(new URL('../mise.toml', import.meta.url))),
        name, 'node scripts/run_markdown.ts ' + phase, [index ? 'markdown:' + phases[index - 1] : 'check-runtime']);
      const input = await predecessor(owner(), phase, inputData, await capture(inputData));
      if (input.report.runtime.task_revision !== task.revision)
        throw new Error('Task body changed during review capture');
      if (phase === 'review-check' || phase === 'accept') {
        checkCompleteReviews(input);
      }
      if (phase in stages && resumeData === undefined) return await suspend({ ...input, task });
      if (phase in stages) return { ...input, reviews: { ...input.reviews, [phase]: validateReview(input, resumeData, phase) } };
      return input;
    } });
  return createWorkflow({ id: 'markdown-' + phase, inputSchema: requestSchema, outputSchema,
    options: { validateInputs: true, autoRestartActiveRuns: false } }).then(step).commit();
}

export function markdownWorkflows(storage: MastraCompositeStore) {
  const workflows = Object.fromEntries(phases.map(phase => ['markdown-' + phase, buildWorkflow(phase, () => mastra)]));
  const mastra: Mastra = new Mastra({ workflows, storage, logger: false });
  return mastra;
}

export async function runPhase(mastra: Mastra, phase: Phase, request: Request, reply?: unknown) {
  const workflow = mastra.getWorkflow('markdown-' + phase), runId = request.run_id + ':' + phase;
  const snapshot = await workflow.getWorkflowRunById(runId);
  if (snapshot?.status === 'success') {
    const saved = outputSchema.parse(snapshot.result), current = await capture(request);
    if (saved.request_sha256 !== current.request_sha256) throw new Error('Completed Markdown proof is stale');
    return { status: 'success', result: saved, reused: true, run_id: runId };
  }
  if (snapshot && snapshot.status !== 'suspended') throw new Error('Retain the failed run; use a new iteration after repair');
  if (snapshot && !isDeepStrictEqual(snapshot.payload, request)) throw new Error('Resume inputs changed');
  const run = await workflow.createRun({ runId });
  const result = snapshot
    ? await run.resume({ step: phase, resumeData: replySchema.parse(reply) })
    : await run.start({ inputData: request });
  return { ...result, run_id: runId };
}
