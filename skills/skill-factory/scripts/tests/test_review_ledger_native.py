"""Native preflight/readback checks must not write or grant acceptance."""
import copy
import json
import subprocess
import sys
import unittest

import test_review_ledger_write as fixtures

ROOT, sha = fixtures.ROOT, fixtures.sha


def setup(case):
    fixtures.TestLedgerWrite.setUp(case)
    case.prepared.write_bytes(b'new\r\n')
    case.request['action'] = 'native-file'
    case.request['change'].update(operation='add', mode={'expected': None, 'new': 0o644})
    case.request['change']['new_file']['sha256'] = sha(case.prepared.read_bytes())


def invoke(case, phase, request=None):
    return subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/review_ledger.py'),
        'native-' + phase, '--write-root', str(case.root)],
        input=json.dumps(request or case.request), capture_output=True, text=True, timeout=20)


def succeeded(case, phase):
    result = invoke(case, phase)
    case.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    data = json.loads(json.loads(result.stdout)['view_text'])
    case.assertEqual(data['execution_acceptance'], 'pending')
    case.assertEqual(data['phase'], phase)
    return data


def test_add_update_delete_without_owned_effect(case):
    target = case.root / 'result.bin'
    before = fixtures.TestLedgerWrite.package(case)
    succeeded(case, 'before')
    case.assertEqual(fixtures.TestLedgerWrite.package(case), before)
    case.assertNotEqual(invoke(case, 'after').returncode, 0)
    target.write_bytes(case.prepared.read_bytes())
    target.chmod(0o644)
    succeeded(case, 'after')
    case.request['change'].update(operation='update', expected_sha256=sha(target.read_bytes()),
        mode={'expected': 0o644, 'new': 0o644})
    case.prepared.write_bytes(b'revised\n')
    case.request['change']['new_file']['sha256'] = sha(case.prepared.read_bytes())
    succeeded(case, 'before')
    target.write_bytes(case.prepared.read_bytes())
    succeeded(case, 'after')
    case.request['change'].update(operation='delete', new_file=None,
        expected_sha256=sha(target.read_bytes()), mode={'expected': 0o644, 'new': None})
    succeeded(case, 'before')
    target.unlink()
    succeeded(case, 'after')


def test_reject_stale_incomplete_unsafe_and_noop_then_recover(case):
    mutations = [lambda r: r.update(ledger_sha256='0' * 64),
        lambda r: r.update(phase='after'),
        lambda r: r['change'].update(path='../escape'),
        lambda r: r['change'].update(operation='delete'),
        lambda r: r['change'].update(expected_sha256='0' * 64),
        lambda r: r['change'].update(mode={'expected': False, 'new': 0o644}),
        lambda r: r['expected_documents'].pop(),
        lambda r: r['change']['review'].pop('Body decision'),
        lambda r: r['change'].update(extra='unreviewed')]
    before = fixtures.TestLedgerWrite.package(case)
    for mutation in mutations:
        request = copy.deepcopy(case.request)
        mutation(request)
        case.assertNotEqual(invoke(case, 'before', request).returncode, 0)
        case.assertEqual(fixtures.TestLedgerWrite.package(case), before)
    succeeded(case, 'before')
    target = case.root / 'result.bin'
    target.write_bytes(case.prepared.read_bytes())
    case.assertNotEqual(invoke(case, 'before').returncode, 0)
    case.request['change'].update(operation='update', expected_sha256=sha(target.read_bytes()),
        mode={'expected': target.stat().st_mode & 0o777, 'new': target.stat().st_mode & 0o777})
    case.assertNotEqual(invoke(case, 'before').returncode, 0)


def test_failed_postcheck_preserves_foreign_bytes_and_source_drift(case):
    succeeded(case, 'before')
    target = case.root / 'result.bin'
    target.write_bytes(b'independent work')
    case.assertNotEqual(invoke(case, 'after').returncode, 0)
    case.assertEqual(target.read_bytes(), b'independent work')
    target.write_bytes(case.prepared.read_bytes())
    target.chmod(0o644)
    case.prepared.write_bytes(b'changed input')
    case.assertNotEqual(invoke(case, 'after').returncode, 0)
    case.assertEqual(target.read_bytes(), b'new\r\n')
    case.prepared.write_bytes(b'new\r\n')
    succeeded(case, 'after')


def test_public_workflow_returns_checks_without_effects(case):
    case.request['phase'] = 'before'
    result = fixtures.TestLedgerWrite.native(case, public=True)
    case.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    report = json.loads(result.stdout)
    case.assertEqual(report['status'], 'success')
    case.assertIn('check-bound-native-file', report['steps'])
    case.assertFalse((case.root / 'result.bin').exists())
    case.assertEqual(report['result']['coverage'], 'bound native file check only')
    (case.root / 'result.bin').write_bytes(case.prepared.read_bytes())
    (case.root / 'result.bin').chmod(0o644)
    case.request['phase'] = 'after'
    result = fixtures.TestLedgerWrite.native(case)
    case.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    case.assertEqual(json.loads(json.loads(result.stdout)['result']['view_text'])['phase'], 'after')
    case.request.pop('phase')
    case.assertNotEqual(fixtures.TestLedgerWrite.native(case).returncode, 0)


class TestNativeChecks(unittest.TestCase):
    setUp = setup
    test_add_update_delete_without_owned_effect = test_add_update_delete_without_owned_effect
    test_reject_stale_incomplete_unsafe_and_noop_then_recover = test_reject_stale_incomplete_unsafe_and_noop_then_recover
    test_failed_postcheck_preserves_foreign_bytes_and_source_drift = test_failed_postcheck_preserves_foreign_bytes_and_source_drift
    test_public_workflow_returns_checks_without_effects = test_public_workflow_returns_checks_without_effects

def handoff(case, reply=None, name='native-fixture'):
    state = case.folder / 'native-state'
    state.mkdir(mode=0o700, exist_ok=True)
    envelope = {'run_id': name, 'turn': 'fixture-turn', 'baseline': 'fixture-baseline',
                'iteration': 0, 'request': {**case.request, 'phase': 'before'}}
    path = case.folder / 'handoff.json'
    path.write_text(json.dumps(envelope))
    command = ['node', str(ROOT / 'scripts/run_review_ledger.ts'), '--native-loop',
               str(path), '--write-root', str(case.root), '--state', str(state)]
    if reply is not None:
        response = case.folder / 'response.json'
        response.write_text(json.dumps(reply))
        command += ['--reply', str(response)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
    data = json.loads(result.stdout) if result.stdout.strip() else {}
    return result, data


def effect_reply(data):
    return {'run_id': data['run_id'], 'request_sha256': data['request_sha256'],
            'tool': 'synthetic fixture writer', 'status': 'success',
            'result': 'Fixture only; no live model or human proof.'}


def test_persistent_native_handoff_and_readback(case):
    result, waiting = handoff(case)
    case.assertEqual(result.returncode, 3, result.stderr + result.stdout)
    case.assertEqual(waiting['status'], 'suspended')
    target = case.root / 'result.bin'
    case.assertFalse(target.exists())
    target.write_bytes(case.prepared.read_bytes())
    target.chmod(0o644)
    result, accepted = handoff(case, effect_reply(waiting))
    case.assertEqual(result.returncode, 0, result.stderr + result.stdout)
    case.assertEqual(accepted['execution_acceptance'], 'pending')
    result, reused = handoff(case)
    case.assertEqual(result.returncode, 0, result.stderr + result.stdout)
    case.assertTrue(reused['reused'])
    target.write_bytes(b'foreign change')
    result, rejected = handoff(case)
    case.assertNotEqual(result.returncode, 0)
    case.assertEqual(target.read_bytes(), b'foreign change')


def test_native_handoff_rejects_false_receipt_and_recovers(case):
    result, waiting = handoff(case)
    case.assertEqual(result.returncode, 3, result.stderr + result.stdout)
    bad = effect_reply(waiting)
    bad['request_sha256'] = '0' * 64
    result, _ = handoff(case, bad)
    case.assertNotEqual(result.returncode, 0)
    result, _ = handoff(case, effect_reply(waiting))
    case.assertNotEqual(result.returncode, 0)
    case.assertFalse((case.root / 'result.bin').exists())
    result, _ = handoff(case)
    case.assertNotEqual(result.returncode, 0)
    result, fresh = handoff(case, name='repaired-fixture')
    case.assertEqual(result.returncode, 3, result.stderr + result.stdout)
    (case.root / 'result.bin').write_bytes(case.prepared.read_bytes())
    (case.root / 'result.bin').chmod(0o644)
    result, _ = handoff(case, effect_reply(fresh), name='repaired-fixture')
    case.assertEqual(result.returncode, 0, result.stderr + result.stdout)


class TestNativeHandoff(unittest.TestCase):
    setUp = setup
    test_persistent_native_handoff_and_readback = test_persistent_native_handoff_and_readback
    test_native_handoff_rejects_false_receipt_and_recovers = test_native_handoff_rejects_false_receipt_and_recovers


if __name__ == '__main__':
    unittest.main()
