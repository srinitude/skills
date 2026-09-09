import { lstat, mkdir, realpath } from 'node:fs/promises';
import { isAbsolute, relative, resolve, sep } from 'node:path';
import { parseArgs } from 'node:util';
import { z } from 'zod';
import { baseline, factory, preparedSchema, requestSchema, savedInput,
  standardizationWorkflow } from './standardization-workflow.ts';

process.env.MASTRA_TELEMETRY_DISABLED = '1';
const help = `Usage: mise run workflow -- start|resume|reject [options]
Standardize an existing skill, pause with its actual candidate, then consume
host-bound evidence before replacing the original. Scope and audience are explicit.
Required: --source PATH --profile FILE --candidate NEW_PATH --scope user|project
          --audience human|agent --state-dir PRIVATE_PATH --run-id STABLE_ID
Resume requires: --acceptance-context FILE --context-sha256 SHA256
                 --receipt FILE --receipt-sha256 SHA256
The host supplies these bindings outside untrusted request and resume data.
This pause does not authenticate a human. Existing human evidence requirements apply.
Exit codes: 0 bound claims accepted; 1 rejected/failed; 2 invalid usage; 3 pending.
Example: mise run workflow -- start --source /skills/example --profile /work/profile.json
  --candidate /work/review/example --scope user --audience agent
  --state-dir /work/private-state --run-id example-update
`;
const flags = ['source', 'profile', 'candidate', 'scope', 'audience', 'state-dir', 'run-id',
  'acceptance-context', 'context-sha256', 'receipt', 'receipt-sha256'];
const bindingFlags = ['acceptance-context', 'context-sha256', 'receipt', 'receipt-sha256'];

function options() {
  const options = Object.fromEntries(flags.map(name => [name, { type: 'string' as const }]));
  const parsed = parseArgs({ options: { ...options, help: { type: 'boolean' } }, allowPositionals: true });
  if (parsed.values.help) { console.log(help); return null; }
  const action = z.enum(['start', 'resume', 'reject']).parse(parsed.positionals[0]);
  if (parsed.positionals.length !== 1) throw new Error('One action is required');
  const values = z.record(z.string(), z.string()).parse(parsed.values);
  for (const key of flags.slice(0, 7)) if (!values[key]) throw new Error('Missing --' + key);
  if (action === 'resume' && bindingFlags.some(key => !values[key])) {
    throw new Error('Resume requires all external acceptance bindings');
  }
  const runId = z.string().regex(/^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$/).parse(values['run-id']);
  return { action, values, runId,
    bindings: bindingFlags.flatMap(key => values[key] ? ['--' + key, values[key]] : []) };
}

function inside(path: string, root: string) {
  const difference = relative(root, path);
  return !difference || (!difference.startsWith('..' + sep) && difference !== '..' && !isAbsolute(difference));
}

async function privateDirectory(path: string, source: string, candidate: string) {
  if ([source, candidate].some(root => inside(path, root) || inside(root, path))) {
    throw new Error('Workflow state must be separate from the original and candidate skills');
  }
  await mkdir(path, { recursive: true, mode: 0o700 });
  const entry = await lstat(path);
  if (!entry.isDirectory() || entry.isSymbolicLink() || (entry.mode & 0o077)) {
    throw new Error('Workflow state must be a private directory with mode 0700');
  }
  return realpath(path);
}

async function execute(config: NonNullable<ReturnType<typeof options>>) {
  const { values, action, runId, bindings } = config;
  const input = requestSchema.parse({ source: resolve(values.source!), profile: resolve(values.profile!),
    candidate: resolve(values.candidate!), scope: values.scope, audience: values.audience,
    implementation: await baseline(factory) });
  const state = await privateDirectory(resolve(values['state-dir']!), input.source, input.candidate);
  const { Mastra } = await import('@mastra/core/mastra');
  const { LibSQLStore } = await import('@mastra/libsql');
  const storage = new LibSQLStore({ id: 'skill-factory-local', url: 'file:' + state + '/workflows.db' });
  await storage.init();
  const workflow = standardizationWorkflow(bindings);
  new Mastra({ logger: false, storage, workflows: { [workflow.id]: workflow } });
  try {
    const store = await storage.getStore('workflows');
    const snapshot = await store!.loadWorkflowSnapshot({ workflowName: workflow.id, runId });
    if (action === 'start' ? snapshot !== null : snapshot?.status !== 'suspended') {
      throw new Error('Start requires a new run; resume and reject require the existing suspended run');
    }
    if (snapshot) await savedInput(snapshot.context, input, action === 'resume' ? bindings : undefined);
    const run = await workflow.createRun({ runId });
    const result = action === 'start' ? await run.start({ inputData: input })
      : await run.resume({ step: 'review-candidate', resumeData: { decision: action === 'reject' ? 'reject' : 'continue' } });
    return report(result, action);
  } finally { await storage.close(); }
}

function report(result: Awaited<ReturnType<Awaited<ReturnType<ReturnType<typeof standardizationWorkflow>['createRun']>>['start']>>, action: string) {
  if (result.status === 'suspended') {
    const step = result.steps['prepare-candidate'];
    if (step?.status !== 'success') throw new Error('Prepared candidate output is missing');
    const prepared = preparedSchema.parse(step.output);
    console.log(JSON.stringify({ domain_status: 'pending', engine_status: result.status,
      target: prepared.source, candidate: prepared.candidate, sha256: prepared.candidate_digest,
      consumer_inputs: prepared.consumer_inputs, review: result.suspendPayload }));
    return 3;
  }
  if (result.status === 'success') {
    console.log(JSON.stringify(result.result));
    return result.result.domain_status === 'accepted' ? 0 : 1;
  }
  console.log(JSON.stringify({ domain_status: action === 'reject' ? 'rejected' : 'failed',
    engine_status: result.status }));
  return 1;
}

try {
  const config = options();
  if (config) process.exitCode = await execute(config);
} catch (error) {
  console.error(error instanceof Error ? error.message : 'Workflow failed');
  process.exitCode = 1;
}
