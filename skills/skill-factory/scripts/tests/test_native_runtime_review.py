"""A declared native runtime edit may resume; unrelated drift must not."""
import json
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


class TestNativeRuntimeReview(unittest.TestCase):
    setUp = setup
    test_wrong_replacement_rejects_then_recovers = test_wrong_replacement_rejects_then_recovers
    test_declared_runner_change_resumes = test_declared_runner_change_resumes
    test_declared_handoff_change_resumes = test_declared_handoff_change_resumes
    test_unrelated_runtime_drift_rejects_then_recovers = test_unrelated_runtime_drift_rejects_then_recovers


if __name__ == '__main__':
    unittest.main()
