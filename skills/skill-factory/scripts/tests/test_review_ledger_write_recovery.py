"""Actual filesystem interference at the write boundary using CPython audit events."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

import test_review_ledger_write as write_cases

INTERFERENCE = '''import json, sys
from pathlib import Path
from review_ledger_write import write_file
request = json.loads(Path(sys.argv[1]).read_text())
root, independent = Path(sys.argv[2]), sys.argv[3] == 'independent'
target, source = root / request['change']['path'], Path(request['original_source']['path'])
original, armed = source.read_bytes(), False
def interfere(event, args):
    global armed
    if event in {'os.rename', 'os.link'} and args[1] == str(target):
        armed = True
    elif event == 'open' and args[0] == str(source) and armed:
        armed = False
        source.write_bytes(original + b'changed')
        if independent:
            target.write_bytes(b'independent edit')
sys.addaudithook(interfere)
try:
    write_file(request, root)
except ValueError as error:
    print(str(error), file=sys.stderr)
    sys.exit(1)
'''


def _TestFileRestoration_interrupted(self, independent=False):
    request = self.folder / 'request.json'
    request.write_text(json.dumps(self.request))
    return subprocess.run([sys.executable, '-c', INTERFERENCE, str(request), str(self.root),
                           'independent' if independent else 'source-only'],
                          cwd=write_cases.ROOT / 'scripts', capture_output=True, text=True, timeout=30)

def _TestFileRestoration_test_readable_source_drift_restores_create_and_replacement_then_recovers(self):
    source = Path(self.request['original_source']['path'])
    original = source.read_bytes()
    target = self.root / 'result.bin'
    for prior in [None, b'accepted contents']:
        if prior is not None:
            target.write_bytes(prior)
            self.request['change']['expected_sha256'] = write_cases.sha(prior)
        process = self.interrupted()
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        self.assertIn('current write input digest mismatch', process.stderr)
        self.assertEqual(source.read_bytes(), original + b'changed')
        self.assertEqual(target.read_bytes() if target.exists() else None, prior)
        source.write_bytes(original)
    self.invoke()
    self.assertEqual(target.read_bytes(), self.prepared.read_bytes())

def _TestFileRestoration_test_independent_edit_is_preserved_and_recovery_requires_rebinding(self):
    source = Path(self.request['original_source']['path'])
    original = source.read_bytes()
    process = self.interrupted(independent=True)
    self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
    self.assertIn('independently changed target was not overwritten', process.stderr)
    target = self.root / 'result.bin'
    self.assertEqual(target.read_bytes(), b'independent edit')
    source.write_bytes(original)
    with self.assertRaises(ValueError):
        self.invoke()
    self.assertEqual(target.read_bytes(), b'independent edit')
    self.request['change']['expected_sha256'] = write_cases.sha(target.read_bytes())
    self.invoke()
    self.assertEqual(target.read_bytes(), self.prepared.read_bytes())


def pending_review(case):
    path = Path(case.request['initial_body_review']['path'])
    review = json.loads(path.read_text())
    review['initial_contract_validation']['state'] = 'pending'
    change = case.request['change']
    review['prerequisite'] = dict(change_sha256=write_cases.sha(json.dumps(
        change, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()),
        reason='Required writer repair precedes integrated body proof.',
        pending_validation=['Whole body and dependent output integration remain unaccepted.'])
    path.write_text(json.dumps(review))
    case.request['initial_body_review']['sha256'] = write_cases.sha(path.read_bytes())
    return case.request['initial_body_review']['sha256']



def _TestFileRestoration_test_pending_review_drift_restores_and_requires_rebinding(self):
    from review_ledger_write import write_file
    digest = pending_review(self)
    source = Path(self.request['initial_body_review']['path']); original = source.read_bytes()
    request = self.folder / 'pending-request.json'; request.write_text(json.dumps(self.request))
    script = INTERFERENCE.replace("Path(request['original_source']['path'])",
                                  "Path(request['initial_body_review']['path'])")
    script = script.replace('write_file(request, root)',
                            "write_file(request, root, pending_body_review=request['initial_body_review']['sha256'])")
    before = self.package()
    result = subprocess.run([sys.executable, '-c', script, str(request), str(self.root), 'source-only'],
                            cwd=write_cases.ROOT / 'scripts', capture_output=True, text=True, timeout=30)
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.assertIn('current write input digest mismatch', result.stderr)
    self.assertEqual(source.read_bytes(), original + b'changed')
    self.assertEqual(self.package(), before)
    source.write_bytes(original)
    effect = write_file(self.request, self.root, pending_body_review=digest)
    self.assertEqual(effect['execution_acceptance'], 'pending')


def _TestFileRestoration_test_pending_permission_change_requires_a_new_review(self):
    from review_ledger_write import write_file
    digest = pending_review(self); before = self.package()
    self.request['change']['mode'] = {'expected': None, 'new': 0o755}
    with self.assertRaises(ValueError):
        write_file(self.request, self.root, pending_body_review=digest)
    self.assertEqual(self.package(), before)
    digest = pending_review(self)
    write_file(self.request, self.root, pending_body_review=digest)
    self.assertEqual((self.root / 'result.bin').stat().st_mode & 0o777, 0o755)


class TestFileRestoration(unittest.TestCase):
    test_pending_review_drift_restores_and_requires_rebinding = _TestFileRestoration_test_pending_review_drift_restores_and_requires_rebinding
    test_pending_permission_change_requires_a_new_review = _TestFileRestoration_test_pending_permission_change_requires_a_new_review
    package = write_cases.TestLedgerWrite.package
    setUp = write_cases.TestLedgerWrite.setUp
    invoke = write_cases.TestLedgerWrite.invoke
    interrupted = _TestFileRestoration_interrupted
    test_readable_source_drift_restores_create_and_replacement_then_recovers = _TestFileRestoration_test_readable_source_drift_restores_create_and_replacement_then_recovers
    test_independent_edit_is_preserved_and_recovery_requires_rebinding = _TestFileRestoration_test_independent_edit_is_preserved_and_recovery_requires_rebinding


if __name__ == '__main__':
    unittest.main()
