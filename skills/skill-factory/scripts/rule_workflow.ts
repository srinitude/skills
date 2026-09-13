/** Model-owned task work, with native task text and persistent bound replies. */
import { realpath } from 'node:fs/promises';
import { isAbsolute, join } from 'node:path';
import { createStep, createWorkflow } from '@mastra/core/workflows';
import { Mastra } from '@mastra/core/mastra';
import type { MastraCompositeStore } from '@mastra/core/storage';
import { z } from 'zod';
import { bound, digest, taskSnapshot, runtimeIdentity } from './task_inventory.ts';
import { taskContract, taskContractSchema } from './standardization_workflow.ts';
import { readThroughOwner } from './review_ledger_workflow.ts';
import { requireRuntimeProof } from './runtime_gate.ts';

const text = z.string().trim().min(1), hash = z.string().regex(/^[a-f0-9]{64}$/);
const binding = z.object({ path: text.refine(isAbsolute), sha256: hash }).strict();
export const ruleRequest = z.object({ run_id: text, turn: text, obligation: text,
  context: z.array(binding.extend({ role: text, format: z.enum(['text', 'bytes']) }).strict()).min(1) }).strict();
const contextSchema = binding.extend({ role: text, format: z.enum(['text', 'bytes']), text: z.string().optional() });
const inputSchema = z.object({ request: ruleRequest, task: taskContractSchema,
  context: z.array(contextSchema), runtime: z.record(text, hash), input_sha256: hash }).strict();
const replySchema = z.object({ task: text, input_sha256: hash, reviewer: text, summary: text,
  evidence: z.array(binding).min(1) }).strict();
const outputSchema = z.object({ input: inputSchema, review: replySchema,
  execution_acceptance: z.literal('pending') }).strict();
type Input = z.infer<typeof inputSchema>;
type Request = z.infer<typeof ruleRequest>;
type Contracts = Record<string, z.infer<typeof taskContractSchema>>;

async function exact(file: string, sha256?: string) {
  if (!isAbsolute(file) || await realpath(file) !== file) throw Error('Use an absolute real input path');
  return bound(file, sha256);
}

export async function strictInput(file: string) {
  const raw = (await exact(file)).raw;
  return readThroughOwner('parse', new TextDecoder('utf-8', { fatal: true }).decode(raw));
}

async function capture(root: string, request: Request, task: Contracts[string]): Promise<Input> {
  const bodies = request.context.filter(item => item.role === 'body');
  if (bodies.length !== 1 || bodies[0]!.path !== join(root, 'SKILL.md') || bodies[0]!.format !== 'text')
    throw Error('Bind exactly one canonical SKILL.md body as text');
  const context = [];
  for (const item of request.context) {
    const raw = (await exact(item.path, item.sha256)).raw;
    context.push({ ...item, ...(item.format === 'text'
      ? { text: new TextDecoder('utf-8', { fatal: true }).decode(raw) } : {}) });
  }
  const input = { request, task, context, runtime: await runtimeIdentity(root) };
  return { ...input, input_sha256: digest(Buffer.from(JSON.stringify(input))) };
}

async function review(input: Input, value: unknown) {
  const result = replySchema.parse(value);
  if (result.task !== input.task.name || result.input_sha256 !== input.input_sha256)
    throw Error('Reply belongs to another task or stale input');
  for (const item of result.evidence) await exact(item.path, item.sha256);
  return result;
}

function workflow(name: string) {
  const step = createStep({ id: 'judgment', inputSchema, outputSchema,
    resumeSchema: replySchema, suspendSchema: inputSchema,
    execute: async ({ inputData, resumeData, suspend }) => {
      if (resumeData === undefined) return suspend(inputData);
      return { input: inputData, review: await review(inputData, resumeData), execution_acceptance: 'pending' as const };
    } });
  return createWorkflow({ id: name, inputSchema, outputSchema,
    options: { validateInputs: true, autoRestartActiveRuns: false } }).then(step).commit();
}

async function contracts(root: string): Promise<Contracts> {
  const snapshot = await taskSnapshot(root), result: Contracts = {};
  for (const task of snapshot.tasks.filter(task => task.name.startsWith('rule:'))) {
    const dependencies = z.array(text).parse(task.depends);
    const contract = await taskContract(root, task.name, 'node scripts/run_rule.ts ' + task.name, dependencies);
    if (contract.revision !== snapshot.revision) throw Error('Task definitions changed during capture');
    result[task.name] = contract;
  }
  return result;
}

const runId = (request: Request, name: string) => digest(Buffer.from(JSON.stringify([request.run_id, name])));

async function prerequisites(mastra: Mastra, root: string, request: Request, tasks: Contracts,
  name: string, storage: MastraCompositeStore, visiting = new Set<string>(), checked = new Set<string>()): Promise<void> {
  if (visiting.has(name)) throw Error('Cyclic task prerequisite: ' + name);
  if (checked.has(name)) return;
  const task = tasks[name];
  if (!task) throw Error('No verified model-task prerequisite owner: ' + name);
  visiting.add(name);
  for (const prior of task.depends) {
    if (prior === 'check-runtime') { await requireRuntimeProof(root, storage, request); continue; }
    await prerequisites(mastra, root, request, tasks, prior, storage, visiting, checked);
    const saved = await mastra.getWorkflow(prior).getWorkflowRunById(runId(request, prior));
    if (saved?.status !== 'success') throw Error('Missing prerequisite proof: ' + prior);
    const proof = outputSchema.parse(saved.result), current = await capture(root, request, tasks[prior]!);
    if (proof.input.input_sha256 !== current.input_sha256) throw Error('Stale prerequisite proof: ' + prior);
    await review(current, proof.review);
  }
  visiting.delete(name);
  checked.add(name);
}

export async function runRule(root: string, storage: MastraCompositeStore, name: string, value: unknown, reply?: unknown) {
  const request = ruleRequest.parse(value), tasks = await contracts(root), task = tasks[name];
  if (!task) throw Error('Unknown rule task: ' + name);
  const workflows = Object.fromEntries(Object.keys(tasks).map(key => [key, workflow(key)]));
  const mastra = new Mastra({ workflows, storage, logger: false });
  await prerequisites(mastra, root, request, tasks, name, storage);
  const input = await capture(root, request, task), selected = mastra.getWorkflow(name), id = runId(request, name);
  const saved = await selected.getWorkflowRunById(id);
  if (saved?.status === 'success') {
    const proof = outputSchema.parse(saved.result);
    if (proof.input.input_sha256 !== input.input_sha256) throw Error('Completed rule proof is stale');
    await review(input, proof.review);
    return { status: 'success', result: proof, reused: true, run_id: id };
  }
  if (saved && saved.status !== 'suspended') throw Error('Retain failed work; use a new run after authorized repair');
  if (saved && inputSchema.parse(saved.payload).input_sha256 !== input.input_sha256) throw Error('Suspended rule inputs changed');
  if (saved && reply !== undefined) await review(input, reply);
  const run = await selected.createRun({ runId: id });
  const result = saved && reply !== undefined ? await run.resume({ step: 'judgment', resumeData: replySchema.parse(reply) })
    : saved ? { status: 'suspended', suspended: [['judgment']], suspendPayload: { judgment: input } } : await run.start({ inputData: input });
  return { ...result, run_id: id };
}
