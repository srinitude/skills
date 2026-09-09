"""Initial-body declarations guard real disposable bootstrap writes, not semantic acceptance."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import test_review_ledger_write as write_cases
from test_review_ledger_write_recovery import INTERFERENCE

sha = write_cases.sha


class TestLedgerBootstrap(unittest.TestCase):
    setUp = write_cases.TestLedgerWrite.setUp
    invoke = write_cases.TestLedgerWrite.invoke
    package = write_cases.TestLedgerWrite.package
    native = write_cases.TestLedgerWrite.native

    def bootstrap(self):
        candidate = self.folder / 'candidate.md'
        body = self.root / 'SKILL.md'
        candidate.write_bytes(body.read_bytes())
        review = self.folder / 'body-review.json'
        value = {'candidate_sha256': sha(candidate.read_bytes()),
                 'ledger_sha256': self.request['ledger_sha256'],
                 'source_sha256': self.data['source']['sha256'],
                 'execution_acceptance': 'pending',
                 'initial_contract_validation': {'state': 'PASS',
                     'reviewer': 'Fixture author; non-independent synthetic declaration',
                     'method': 'The fixture body states its sole write condition.',
                     'limit': 'Mechanical fixture only; no real goal or human acceptance.'}}
        review.write_text(json.dumps(value))
        self.request['bootstrap_body'] = {
            'body': {'path': str(candidate), 'sha256': sha(candidate.read_bytes())},
            'review': {'path': str(review), 'sha256': sha(review.read_bytes())}}
        body.unlink()
        return candidate, review, value

    def test_public_bootstrap_reads_reviewed_body_without_installing_it(self):
        candidate, review, value = self.bootstrap()
        process = self.native(public=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        result = json.loads(json.loads(process.stdout)['result']['view_text'])
        self.assertFalse((self.root / 'SKILL.md').exists())
        self.assertEqual((self.root / 'result.bin').read_bytes(), self.prepared.read_bytes())
        for phase in ['before', 'after']:
            self.assertEqual(result[phase]['body']['path'], str(candidate))
            self.assertEqual(result[phase]['body']['text'].encode(), candidate.read_bytes())
            self.assertEqual(result[phase]['bootstrap_review'], value)
            self.assertIn(str(review), result[phase]['input_bytes'])
        self.assertEqual(result['execution_acceptance'], 'pending')

    def test_stale_or_unfinished_body_review_rejects_without_writes_then_recovers(self):
        candidate, review, value = self.bootstrap()
        before = self.package()
        changes = [lambda v: v.update(candidate_sha256='0'*64),
                   lambda v: v.update(ledger_sha256='0'*64),
                   lambda v: v.update(source_sha256='0'*64),
                   lambda v: v.update(execution_acceptance='passed'),
                   lambda v: v['initial_contract_validation'].update(state='pending'),
                   lambda v: v['initial_contract_validation'].update(reviewer=''),
                   lambda v: v['initial_contract_validation'].update(method=' '),
                   lambda v: v['initial_contract_validation'].update(limit='')]
        for change in changes:
            altered = copy.deepcopy(value); change(altered)
            review.write_text(json.dumps(altered))
            self.request['bootstrap_body']['review']['sha256'] = sha(review.read_bytes())
            with self.assertRaises((OSError, ValueError)):
                self.invoke()
            self.assertEqual(self.package(), before)
        review.write_text(json.dumps(value))
        self.request['bootstrap_body']['review']['sha256'] = sha(review.read_bytes())
        try:
            self.invoke()
        except (OSError, ValueError) as error:
            self.fail(f'Reviewed bootstrap must recover: {error}')

    def test_bootstrap_cannot_replace_or_hide_an_installed_body(self):
        candidate, _, _ = self.bootstrap()
        (self.root / 'SKILL.md').write_bytes(candidate.read_bytes())
        before = self.package()
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(self.package(), before)
        del self.request['bootstrap_body']
        self.invoke()

    def test_bootstrap_body_or_review_cannot_be_the_written_file(self):
        candidate, review, _ = self.bootstrap()
        before = self.package()
        for source in [candidate, review]:
            target = self.root / 'result.bin'
            source.rename(target)
            key = 'body' if source == candidate else 'review'
            original = self.request['bootstrap_body'][key]['path']
            self.request['bootstrap_body'][key]['path'] = str(target)
            self.request['change']['expected_sha256'] = sha(target.read_bytes())
            with self.assertRaises(ValueError):
                self.invoke()
            target.rename(source)
            self.request['bootstrap_body'][key]['path'] = original
            self.assertEqual(self.package(), before)
        self.request['change']['expected_sha256'] = None
        try:
            self.invoke()
        except (OSError, ValueError) as error:
            self.fail(f'Distinct bootstrap inputs must recover: {error}')


    def test_missing_blank_or_invalid_candidate_rejects_then_recovers(self):
        candidate, review, value = self.bootstrap()
        original = candidate.read_bytes()
        before = self.package()
        for raw in [None, b'', b'  \n', '\u2003'.encode(), b'\xff']:
            candidate.unlink(missing_ok=True)
            if raw is not None:
                candidate.write_bytes(raw)
                digest = sha(raw)
                self.request['bootstrap_body']['body']['sha256'] = digest
                self.request['change']['body_sha256'] = digest
                value['candidate_sha256'] = digest
                review.write_text(json.dumps(value))
                self.request['bootstrap_body']['review']['sha256'] = sha(review.read_bytes())
            with self.assertRaises((OSError, ValueError)):
                self.invoke()
            self.assertEqual(self.package(), before)
        candidate.write_bytes(original)
        digest = sha(original)
        self.request['bootstrap_body']['body']['sha256'] = digest
        self.request['change']['body_sha256'] = digest
        value['candidate_sha256'] = digest
        review.write_text(json.dumps(value))
        self.request['bootstrap_body']['review']['sha256'] = sha(review.read_bytes())
        self.invoke()

    def test_review_drift_after_creation_restores_the_file_then_recovers(self):
        _, review, _ = self.bootstrap()
        original = review.read_bytes()
        request = self.folder / 'request.json'
        request.write_text(json.dumps(self.request))
        script = INTERFERENCE.replace("Path(request['original_source']['path'])",
                                     "Path(request['bootstrap_body']['review']['path'])")
        process = subprocess.run([sys.executable, '-c', script, str(request), str(self.root), 'source-only'],
            cwd=write_cases.ROOT / 'scripts', capture_output=True, text=True, timeout=30)
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        self.assertIn('current write input digest mismatch', process.stderr)
        self.assertEqual(review.read_bytes(), original + b'changed')
        self.assertFalse((self.root / 'result.bin').exists())
        review.write_bytes(original)
        self.invoke()

if __name__ == '__main__':
    unittest.main()
