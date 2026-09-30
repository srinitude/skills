"""A declared native runtime edit may resume; unrelated drift must not."""
import json
import os
import shutil
import subprocess
import unittest

import test_review_ledger_native as native


def setup(case):
    native.setup(case)
    shutil.copytree(native.ROOT / 'scripts', case.root / 'scripts')
    shutil.copytree(native.ROOT / 'runtime', case.root / 'runtime',
                    ignore=shutil.ignore_patterns('node_modules'))
    for name in ['package.json', 'package-lock.json']:
        shutil.copy2(native.ROOT / name, case.root / name)
    for name in ['node_modules', 'runtime/standardization/node_modules']:
        (case.root / name).symlink_to(native.ROOT / name, target_is_directory=True)


def invoke(case, reply=None):
    state = case.folder / 'native-state'
    state.mkdir(mode=0o700, exist_ok=True)
    path = case.folder / 'handoff.json'
    envelope = {'run_id': 'runtime-fixture', 'turn': 'fixture-turn',
                'baseline': 'fixture-baseline', 'iteration': 0,
                'request': {**case.request, 'phase': 'before'}}
    path.write_text(json.dumps(envelope))
    command = ['node', str(case.root / 'scripts/run_review_ledger.ts'),
               '--native-loop', str(path), '--write-root', str(case.root),
               '--state', str(state)]
    if reply is not None:
        response = case.folder / 'response.json'
        response.write_text(json.dumps(reply))
        command += ['--reply', str(response)]
    result = subprocess.run(command, cwd=case.root, text=True,
                            capture_output=True, timeout=60)
    data = json.loads(result.stdout) if result.stdout.strip() else {}
    return result, data


def select_runtime(case, name):
    target = case.root / 'scripts' / name
    before = target.read_bytes()
    case.prepared.write_bytes(before + b'\n// Runtime identity fixture only.\n')
    case.request['change'].update(path='scripts/' + name, operation='update',
        expected_sha256=native.sha(before), mode={'expected': 0o644, 'new': 0o644},
        new_file={'path': str(case.prepared), 'sha256': native.sha(case.prepared.read_bytes())})
    target.chmod(0o644)
    return target


def exercise_declared_update(case, name):
    target = select_runtime(case, name)
    result, waiting = invoke(case)
    case.assertEqual(result.returncode, 3, result.stdout + result.stderr)
    target.write_bytes(case.prepared.read_bytes())
    result, done = invoke(case, native.effect_reply(waiting))
    case.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    case.assertEqual(done['execution_acceptance'], 'pending')
    case.assertEqual(done['request_sha256'], waiting['request_sha256'])
    result, reused = invoke(case)
    case.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    case.assertTrue(reused['reused'])


def test_declared_runner_change_resumes(case):
    exercise_declared_update(case, 'run_review_ledger.ts')


def test_declared_handoff_change_resumes(case):
    exercise_declared_update(case, 'native_file_workflow.ts')


def test_unrelated_runtime_drift_rejects_then_recovers(case):
    target = select_runtime(case, 'run_review_ledger.ts')
    result, waiting = invoke(case)
    case.assertEqual(result.returncode, 3, result.stdout + result.stderr)
    target.write_bytes(case.prepared.read_bytes())
    other = case.root / 'scripts/review_ledger_context.py'
    old = other.read_bytes()
    other.write_bytes(old + b'\n# Unreviewed fixture change.\n')
    result, _ = invoke(case, native.effect_reply(waiting))
    case.assertNotEqual(result.returncode, 0)
    case.assertIn('Saved native inputs changed', result.stderr)
    case.assertEqual(other.read_bytes(), old + b'\n# Unreviewed fixture change.\n')
    other.write_bytes(old)
    result, _ = invoke(case, native.effect_reply(waiting))
    case.assertEqual(result.returncode, 0, result.stdout + result.stderr)


def test_wrong_replacement_rejects_then_recovers(case):
    target = select_runtime(case, 'run_review_ledger.ts')
    result, waiting = invoke(case)
    case.assertEqual(result.returncode, 3, result.stdout + result.stderr)
    target.write_bytes(case.prepared.read_bytes() + b'// Wrong bytes.\n')
    result, _ = invoke(case, native.effect_reply(waiting))
    case.assertNotEqual(result.returncode, 0)
    case.assertIn('Saved native inputs changed', result.stderr)
    target.write_bytes(case.prepared.read_bytes())
    result, _ = invoke(case, native.effect_reply(waiting))
    case.assertEqual(result.returncode, 0, result.stdout + result.stderr)


def test_markdown_requires_own_mise_task(case):
    state = case.folder / 'unused-state'
    env = {**os.environ, 'SKILL_MARKDOWN_REQUEST': str(case.folder / 'missing.json'),
           'SKILL_MARKDOWN_STATE': str(state)}
    for task in [None, 'test', 'markdown:accept']:
        env.pop('MISE_TASK_NAME', None)
        if task is not None:
            env['MISE_TASK_NAME'] = task
        result = subprocess.run(['node', str(native.ROOT / 'scripts/run_markdown.ts'), 'inventory'],
            cwd=native.ROOT, env=env, capture_output=True, text=True, timeout=30)
        case.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        case.assertIn('Start or resume through mise run markdown:inventory', result.stderr)
        case.assertEqual(result.stdout, '')
        case.assertFalse(state.exists())


def probe_mastra(case, body):
    script = "import assert from 'node:assert/strict'; import { createStep, createWorkflow } from '@mastra/core/workflows'; import { z } from 'zod';\n" + body
    result = subprocess.run(['node', '--input-type=module', '-e', script],
        cwd=native.ROOT, capture_output=True, text=True, timeout=30)
    case.assertEqual(result.returncode, 0, result.stdout + result.stderr)


def test_mastra_routes_and_post_test_loops(case):
    probe_mastra(case, """
const schema = z.object({ n: z.number() });
const step = id => createStep({ id, inputSchema: schema, outputSchema: schema,
  execute: async ({ inputData }) => ({ n: inputData.n + 1 }) });
const workflow = id => createWorkflow({ id, inputSchema: schema, outputSchema: z.any() });
const both = workflow('both').branch([[async () => true, step('a')], [async () => true, step('b')]]).commit();
const result = await (await both.createRun()).start({ inputData: { n: 0 } });
assert.equal(result.status, 'success');
assert.deepEqual(result.result, { a: { n: 1 }, b: { n: 1 } });
for (const method of ['dowhile', 'dountil']) {
  const flow = workflow(method)[method](step('body'), async () => method === 'dountil').commit();
  const output = await (await flow.createRun()).start({ inputData: { n: 0 } });
  assert.equal(output.status, 'success'); assert.deepEqual(output.result, { n: 1 });
}
assert.throws(() => workflow('removed').waitForEvent('reply', step('wait')), /removed/);
""")


def test_mastra_bail_denial_is_not_acceptance(case):
    probe_mastra(case, """
const schema = z.object({ decision: z.string() }); let effects = 0;
const review = createStep({ id: 'review', inputSchema: schema, outputSchema: schema,
  execute: async ({ bail }) => bail({ decision: 'denied' }) });
const effect = createStep({ id: 'effect', inputSchema: schema, outputSchema: schema,
  execute: async ({ inputData }) => { effects++; return inputData; } });
const flow = createWorkflow({ id: 'denial', inputSchema: schema, outputSchema: schema })
  .then(review).then(effect).commit();
const result = await (await flow.createRun()).start({ inputData: { decision: 'fixture only' } });
assert.equal(result.status, 'success'); assert.equal(result.result.decision, 'denied');
assert.equal(effects, 0); // Framework fixture, not proof of real human approval.
""")


class TestNativeRuntimeReview(unittest.TestCase):
    test_mastra_routes_and_post_test_loops = test_mastra_routes_and_post_test_loops
    test_mastra_bail_denial_is_not_acceptance = test_mastra_bail_denial_is_not_acceptance
    setUp = setup
    test_markdown_requires_own_mise_task = test_markdown_requires_own_mise_task
    test_wrong_replacement_rejects_then_recovers = test_wrong_replacement_rejects_then_recovers
    test_declared_runner_change_resumes = test_declared_runner_change_resumes
    test_declared_handoff_change_resumes = test_declared_handoff_change_resumes
    test_unrelated_runtime_drift_rejects_then_recovers = test_unrelated_runtime_drift_rejects_then_recovers


if __name__ == '__main__':
    unittest.main()
