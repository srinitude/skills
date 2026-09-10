/** Public domain command. Native argument and effect owners remain authoritative. */
import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { isDeepStrictEqual } from 'node:util';
import { lstat, mkdtemp, rm, realpath } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { isAbsolute, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import type { MastraCompositeStore } from '@mastra/core/storage';
import { z } from 'zod';
import { bound, createStandardizationWorkflow, inputSchema, preparedSchema, workflowRoots, type NativeResult } from './standardization_workflow.ts';

const parsedSchema = z.object({ skill_root: z.string(), profile: z.string(), apply: z.boolean(),
  plan_file: z.string().nullable(), review: z.string().nullable(), rebase_tracked_text: z.boolean(),
  scope: z.enum(['user', 'project']).nullable(), placement_receipt: z.string().nullable() }).strict();
type Parsed = z.infer<typeof parsedSchema>;
type Selected = { state?: string; run?: string; reject?: boolean };
type Workflow = Awaited<ReturnType<typeof createStandardizationWorkflow>>['workflow'];

function parse(factory: string, args: string[]) {
  const script = join(factory, 'scripts/standardize_registry_skill.py');
  const code = "import contextlib,io,json,sys\nsys.path.insert(0,sys.argv.pop(1));sys.argv[0]=sys.argv.pop(1)\nfrom standardization_cli import parse_args\nfrom standardize_registry_skill import prepare_inputs\ncapture=io.StringIO()\ntry:\n    with contextlib.redirect_stdout(capture):\n        args,selected=parse_args(sys.argv[1:])\n        prepare_inputs(args)\nexcept SystemExit as error:\n    if error.code:\n        raise\n    print(json.dumps({'help':capture.getvalue()}))\n    sys.exit(0)\nexcept ValueError as error:\n    print(f'error: {error}',file=sys.stderr)\n    sys.exit(2)\nprint(json.dumps({'parsed':vars(args),'selected':selected}))\n";
  const result = spawnSync('uv', ['run', '--no-project', '--isolated', '--no-python-downloads',
    '--with', 'PyYAML==6.0.3', '--with', 'argparse-usage==0.1.1', 'python', '-c', code,
    join(factory, 'scripts'), script, ...args], { encoding: 'utf8' });
  if (result.error) throw result.error;
  if (result.status !== 0) {
    process.stdout.write(result.stdout);
    process.stderr.write(result.stderr); process.exitCode = result.status ?? 1;
    return;
  }
  const selectedSchema = z.object({ state: z.string().optional(), run: z.string().optional(), reject: z.boolean().optional() }).strict();
  const reply = z.union([z.object({ help: z.string() }).strict(),
    z.object({ parsed: parsedSchema, selected: selectedSchema }).strict()]).parse(JSON.parse(result.stdout));
  if ('help' in reply) { process.stdout.write(reply.help); return; }
  return reply;
}

async function openStorage(state: string): Promise<MastraCompositeStore> {
  const metadata = await lstat(state);
  if ((metadata.mode & 0o077) !== 0 || metadata.uid !== process.getuid?.())
    throw new Error('Persistent state requires a private directory owned by this caller on POSIX');
  const database = join(await realpath(state), 'standardization.db');
  for (const suffix of ['', '-wal', '-shm', '-journal']) {
    try {
      const file = await lstat(database + suffix);
      if (!file.isFile() || file.isSymbolicLink() || file.nlink !== 1) throw new Error('Unsafe workflow database file');
    } catch (error) { if (!(error instanceof Error && 'code' in error && error.code === 'ENOENT')) throw error; }
  }
  const require = createRequire(new URL('../runtime/standardization/package.json', import.meta.url));
  const { LibSQLStore } = await import(pathToFileURL(require.resolve('@mastra/libsql')).href);
  return new LibSQLStore({ id: 'standardization-public-state', url: 'file:' + database });
}

function inputFor(parsed: Parsed) {
  return inputSchema.parse({ target: resolve(parsed.skill_root), profile: resolve(parsed.profile),
    ...(parsed.scope === null ? {} : { scope: parsed.scope }),
    ...(parsed.rebase_tracked_text ? { rebase_tracked_text: true } : {}),
    ...(parsed.placement_receipt === null ? {} : { placement_receipt: resolve(parsed.placement_receipt) }) });
}

async function suspendedPlan(workflow: Workflow, runId: string, input: z.infer<typeof inputSchema>, saved?: Buffer) {
  const snapshot = await workflow.getWorkflowRunById(runId);
  if (!snapshot || snapshot.status !== 'suspended') throw new Error('Selected workflow is not suspended');
  if (!isDeepStrictEqual(snapshot.payload, input)) throw new Error('CLI inputs differ from the selected suspended run');
  const step = snapshot.steps?.['prepare-standardization'];
  if (!step || Array.isArray(step)) throw new Error('Selected run has no single prepared result');
  const prepared = preparedSchema.parse(step.output);
  const actual = await bound(prepared.plan_path, prepared.plan_sha256);
  if (saved && !isDeepStrictEqual(JSON.parse(actual.raw.toString()).plan, JSON.parse(saved.toString()).plan))
    throw new Error('Saved plan differs from the selected suspended run');
  return prepared;
}

async function execute(workflow: Workflow, reviewStep: Awaited<ReturnType<typeof createStandardizationWorkflow>>['reviewStep'], parsed: Parsed, selected: Selected) {
  const input = inputFor(parsed), run = await workflow.createRun(selected.run ? { runId: selected.run } : undefined);
  let prepared: { plan_path: string; plan_sha256: string };
  if (selected.run) prepared = await suspendedPlan(workflow, run.runId, input, parsed.plan_file ? (await bound(resolve(parsed.plan_file))).raw : undefined);
  else {
    const result = await run.start({ inputData: input });
    if (result.status !== 'suspended') throw result.status === 'failed' ? result.error : new Error('Workflow failed before review');
    const step = result.steps['prepare-standardization'];
    if (!step || step.status !== 'success') throw new Error('Workflow has no prepared plan');
    prepared = preparedSchema.parse(step.output);
  }
  if (selected.reject) {
    const rejected = await run.resume({ step: reviewStep, resumeData: { decision: 'reject' } });
    if (rejected.status !== 'failed') throw new Error('Workflow did not record the rejected review');
    throw rejected.error;
  }
  let report: unknown = JSON.parse((await bound(prepared.plan_path)).raw.toString());
  if (parsed.apply) {
    const review = await bound(resolve(parsed.review!));
    const result = await run.resume({ step: reviewStep, resumeData: { decision: 'continue',
      plan_sha256: prepared.plan_sha256, review_path: resolve(parsed.review!), review_sha256: review.sha256 } });
    if (result.status !== 'success') throw result.status === 'failed' ? result.error : new Error('Workflow did not apply the reviewed package');
    report = result.result;
  }
  return { ...z.record(z.string(), z.unknown()).parse(report), workflow: { run_id: run.runId,
    status: parsed.apply ? 'success' : 'suspended', persistent: Boolean(selected.state), review_step: reviewStep.id } };
}

export async function runStandardization(args = process.argv.slice(2), factory = fileURLToPath(new URL('../', import.meta.url))) {
  let temporary: string | undefined, storage: MastraCompositeStore | undefined, lastNative: NativeResult | undefined;
  try {
    let context;
    try { context = parse(factory, args); } catch (error) { process.exitCode = 2; throw error; }
    if (!context) return;
    const { parsed, selected } = context;
    if (selected.run && !parsed.apply && !selected.reject) throw new Error('Resuming requires --apply and current review');
    if (parsed.apply && (!parsed.plan_file || !parsed.review)) throw new Error('standardization requires --plan-file and --review before applying');
    const python = process.env.UV_PYTHON;
    if (!python || !isAbsolute(python)) throw new Error('Use the Mise-resolved Python path');
    const state = selected.state ?? (temporary = await mkdtemp(join(tmpdir(), 'skill-standardization-')));
    const runtime = { factory, state, environment: { UV_PYTHON: python } };
    await workflowRoots(runtime, resolve(parsed.skill_root));
    if (selected.state) storage = await openStorage(state);
    const saved = parsed.apply ? await bound(resolve(parsed.plan_file!)) : undefined;
    const preparedPlan = saved && !selected.run ? { plan_path: resolve(parsed.plan_file!), plan_sha256: saved.sha256 } : undefined;
    const { workflow, reviewStep } = await createStandardizationWorkflow(runtime, { storage, preparedPlan,
      onNativeResult: value => { lastNative = value; } });
    process.stdout.write(JSON.stringify(await execute(workflow, reviewStep, parsed, selected)) + '\n');
  } catch (error) {
    const message = error && typeof error === 'object' && 'message' in error ? String(error.message) : String(error);
    process.stderr.write((lastNative?.code !== 0 && lastNative?.stderr || message) + '\n');
    process.exitCode = process.exitCode || lastNative?.code || 1;
  } finally {
    await storage?.close();
    if (temporary) await rm(temporary, { recursive: true });
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await runStandardization();
