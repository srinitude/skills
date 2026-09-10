"""Real initial-review rejection, capture and recovery; declarations are not acceptance."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import test_review_ledger_write as writes
from test_review_ledger_write_recovery import INTERFERENCE


class TestInitialReview(unittest.TestCase):
    setUp = writes.TestLedgerWrite.setUp
    invoke = writes.TestLedgerWrite.invoke
    native = writes.TestLedgerWrite.native
    package = writes.TestLedgerWrite.package

    def test_missing_review_rejects_before_effect_and_valid_review_recovers(self):
        request = copy.deepcopy(self.request)
        del request['initial_body_review']
        before = self.package()
        with self.assertRaises(ValueError):
            self.invoke(request)
        self.assertEqual(self.package(), before)
        result = self.invoke()
        review = json.loads(Path(self.request['initial_body_review']['path']).read_text())
        for phase in ['before', 'after']:
            self.assertEqual(result[phase]['initial_body_review'], review)
            self.assertIn(self.request['initial_body_review']['path'], result[phase]['input_bytes'])
        self.assertEqual(result['execution_acceptance'], 'pending')

    def test_explicit_null_modes_reject_before_effect_then_valid_review_recovers(self):
        before = self.package()
        for mode in ['bootstrap_body', 'body_revision']:
            request = copy.deepcopy(self.request); request[mode] = None
            with self.assertRaises(ValueError):
                self.invoke(request)
            self.assertEqual(self.package(), before)
        self.invoke()

    def test_stale_and_unfinished_review_cannot_authorize_a_write(self):
        path = Path(self.request['initial_body_review']['path'])
        original = path.read_bytes(); value = json.loads(original); before = self.package()
        changes = [lambda r: r.update(candidate_sha256='0'*64),
                   lambda r: r.update(ledger_sha256='0'*64),
                   lambda r: r.update(source_sha256='0'*64),
                   lambda r: r.update(execution_acceptance='passed'),
                   lambda r: r['initial_contract_validation'].update(state='pending'),
                   lambda r: r['initial_contract_validation'].update(reviewer=''),
                   lambda r: r['initial_contract_validation'].update(method=' '),
                   lambda r: r['initial_contract_validation'].update(limit='')]
        for change in changes:
            review = copy.deepcopy(value); change(review); path.write_text(json.dumps(review))
            self.request['initial_body_review']['sha256'] = writes.sha(path.read_bytes())
            with self.assertRaises(ValueError):
                self.invoke()
            self.assertEqual(self.package(), before)
        path.write_bytes(original)
        self.request['initial_body_review']['sha256'] = writes.sha(original)
        self.invoke()

    def test_native_missing_review_rejects_then_public_reviewed_route_succeeds(self):
        request = copy.deepcopy(self.request); del request['initial_body_review']
        before = self.package()
        rejected = self.native(request)
        self.assertEqual(rejected.returncode, 1, rejected.stdout + rejected.stderr)
        self.assertEqual(self.package(), before)
        accepted = self.native(public=True)
        self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
        result = json.loads(json.loads(accepted.stdout)['result']['view_text'])
        self.assertIn('initial_body_review', result['before'])
        self.assertIn('initial_body_review', result['after'])

    def test_review_drift_after_write_restores_previous_bytes_then_recovers(self):
        target = self.root / 'result.bin'; target.write_bytes(b'previous'); target.chmod(0o640)
        self.request['change']['expected_sha256'] = writes.sha(target.read_bytes())
        path = Path(self.request['initial_body_review']['path']); original = path.read_bytes()
        before = self.package(); request_path = self.folder / 'request.json'
        request_path.write_text(json.dumps(self.request))
        script = INTERFERENCE.replace("Path(request['original_source']['path'])",
                                      "Path(request['initial_body_review']['path'])")
        result = subprocess.run([sys.executable, '-c', script, str(request_path), str(self.root), 'source-only'],
            cwd=writes.ROOT / 'scripts', capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('current write input digest mismatch', result.stderr)
        self.assertEqual(path.read_bytes(), original + b'changed')
        self.assertEqual(self.package(), before)
        path.write_bytes(original)
        self.invoke()
        self.assertEqual((target.read_bytes(), target.stat().st_mode & 0o777), (self.prepared.read_bytes(), 0o640))

    def test_review_cannot_be_the_written_target(self):
        binding = self.request['initial_body_review']; path = Path(binding['path'])
        target = self.root / 'result.bin'; path.rename(target); original = binding['path']
        binding['path'] = str(target)
        self.request['change']['expected_sha256'] = writes.sha(target.read_bytes())
        before = self.package()
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(self.package(), before)
        target.rename(path); binding['path'] = original
        self.request['change']['expected_sha256'] = None
        self.invoke()


if __name__ == '__main__':
    unittest.main()
