"""Real per-file effects and rejected bindings; no semantic acceptance claim."""
import copy
import hashlib
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

import test_review_ledger_source as source_cases

ROOT = Path(__file__).resolve().parents[2]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def initial_body_review(case):
    path = case.folder / 'initial-body-review.json'
    value = dict(candidate_sha256=sha((case.root / 'SKILL.md').read_bytes()),
        ledger_sha256=case.request['ledger_sha256'], source_sha256=case.data['source']['sha256'],
        execution_acceptance='pending', initial_contract_validation=dict(state='PASS',
            reviewer='Fixture author; non-independent', method='Review the sole fixture write rule.',
            limit='Mechanical fixture declaration; no semantic or human acceptance.'))
    path.write_text(json.dumps(value))
    return {'path': str(path), 'sha256': sha(path.read_bytes())}


class TestLedgerWrite(unittest.TestCase):
    def setUp(self):
        source_cases.TestLiveSource.setUp(self)
        self.folder = self.root.resolve()
        self.root = self.folder / 'skill'
        self.root.mkdir()
        (self.root / 'SKILL.md').write_bytes(b'Use the declared ledger before every file write.\n')
        self.data['dependency_traversal'] = {'workflow': [
            {'step': 1, 'action': 'Read', 'rule': 'Read every governing input.'}]}
        self.data['reusable_review_protocol'] = [
            {'field': 'Contribution', 'review': 'Explain the actual change.'},
            {'field': 'Body decision', 'review': 'Keep core rules in the body.'}]
        self.data['semantic_model'] = {'body_hub': {'core': 'SKILL.md'},
                                       'mechanism_map': {'write': 'The declared file owner.'}}
        self.ledger = self.folder / 'ledger.json'
        self.ledger.write_text(json.dumps(self.data))
        self.prepared = self.folder / 'prepared.bin'
        self.prepared.write_bytes(b'new\x00\xff\r\n')
        self.request.update(action='write-file', ledger=str(self.ledger), ledger_sha256=sha(self.ledger.read_bytes()),
            change={'path': 'result.bin', 'expected_sha256': None,
                    'new_file': {'path': str(self.prepared), 'sha256': sha(self.prepared.read_bytes())},
                    'body_sha256': sha((self.root / 'SKILL.md').read_bytes()),
                    'reviewer': 'Test author; mechanical fixture only',
                    'review': {'Contribution': 'Exercise exact binary file creation.',
                               'Body decision': 'The fixture body already declares the write condition.'}})
        self.request['initial_body_review'] = initial_body_review(self)

    def invoke(self, request=None):
        from review_ledger_write import write_file
        return write_file(request or self.request, self.root)

    def package(self):
        return {p.relative_to(self.root).as_posix(): (p.read_bytes(), p.stat().st_mode)
                for p in self.root.rglob('*') if p.is_file()}

    def native(self, request=None, root=True, public=False):
        path = self.folder / 'request.json'
        path.write_text(json.dumps(request or self.request))
        command = (['mise', 'run', '--force', '--task-cache', 'off', 'ledger', '--']
                   if public else ['node', str(ROOT / 'scripts/run_review_ledger.ts')])
        command.append(str(path))
        if root:
            command += ['--write-root', str(self.root)]
        return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)

    def test_creation_replacement_and_repeated_stale_request_rejection(self):
        result = self.invoke()
        target = self.root / 'result.bin'
        self.assertEqual(target.read_bytes(), self.prepared.read_bytes())
        self.assertEqual(result['execution_acceptance'], 'pending')
        self.assertEqual(result['review'], self.request['change']['review'])
        for phase in ['before', 'after']:
            self.assertEqual(result[phase]['ledger_bytes'], len(self.ledger.read_bytes()))
            self.assertEqual(result[phase]['documents'], 3)
            self.assertEqual(result[phase]['body']['text'].encode(), (self.root / 'SKILL.md').read_bytes())
        with self.assertRaises(ValueError):
            self.invoke()
        target.chmod(0o755)
        self.request['change']['expected_sha256'] = sha(target.read_bytes())
        self.prepared.write_bytes(b'replacement')
        self.request['change']['new_file']['sha256'] = sha(self.prepared.read_bytes())
        self.invoke()
        self.assertEqual((target.read_bytes(), target.stat().st_mode & 0o777), (b'replacement', 0o755))

    def test_stale_missing_and_incomplete_reviews_reject_without_mutation(self):
        changes = [lambda r: r.update(ledger_sha256='0'*64),
                   lambda r: r['change'].update(body_sha256='0'*64),
                   lambda r: r['change']['new_file'].update(sha256='0'*64),
                   lambda r: r['expected_documents'].pop(),
                   lambda r: r['original_source'].update(sha256='0'*64),
                   lambda r: r['change']['review'].pop('Body decision'),
                   lambda r: r['change']['review'].update(Contribution=''),
                   lambda r: r['change'].update(reviewer=''),
                   lambda r: r['change'].update(expected_sha256='0'*64)]
        before = self.package()
        for change in changes:
            request = copy.deepcopy(self.request)
            change(request)
            with self.assertRaises((OSError, ValueError)):
                self.invoke(request)
            self.assertEqual(self.package(), before)
        original = Path(self.request['original_source']['path'])
        raw = original.read_bytes()
        original.write_bytes(raw + b'changed')
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(self.package(), before)
        original.write_bytes(raw)
        self.invoke()

    def test_missing_or_empty_body_rejects_before_effect_and_recovers(self):
        body = self.root / 'SKILL.md'
        original = body.read_bytes()
        for raw in [None, b'', b'  \n', '\u2003'.encode(), b'\xff']:
            body.unlink(missing_ok=True)
            if raw is not None:
                body.write_bytes(raw)
                self.request['change']['body_sha256'] = sha(raw)
            before = self.package()
            with self.assertRaises((OSError, ValueError)):
                self.invoke()
            self.assertEqual(self.package(), before)
        body.write_bytes(original)
        self.request['change']['body_sha256'] = sha(original)
        self.invoke()

    def test_paths_links_and_source_overlap_reject_and_valid_input_recovers(self):
        before = self.package()
        for name in ['', '.', '../escape', '/absolute', 'SKILL.md', 'missing/child', '.git/owned']:
            request = copy.deepcopy(self.request)
            request['change']['path'] = name
            with self.assertRaises((OSError, ValueError)):
                self.invoke(request)
            self.assertEqual(self.package(), before)
        target = self.root / 'result.bin'
        for link in ['symbolic', 'hard']:
            os.symlink(self.prepared, target) if link == 'symbolic' else os.link(self.prepared, target)
            request = copy.deepcopy(self.request)
            request['change']['expected_sha256'] = sha(self.prepared.read_bytes())
            with self.assertRaises(ValueError):
                self.invoke(request)
            target.unlink()
        self.prepared.rename(target)
        self.request['change']['new_file']['path'] = str(target)
        self.request['change']['expected_sha256'] = sha(target.read_bytes())
        with self.assertRaises(ValueError):
            self.invoke()
        target.rename(self.prepared)
        self.request['change'].update(expected_sha256=None)
        self.request['change']['new_file']['path'] = str(self.prepared)
        self.invoke()

    def test_package_lock_rejects_before_writing_and_recovers(self):
        lock = self.root.parent / ('.' + self.root.name + '.skill-lock')
        lock.write_bytes(b'another cooperating writer')
        before = self.package()
        with self.assertRaises(FileExistsError):
            self.invoke()
        self.assertEqual((self.package(), lock.read_bytes()), (before, b'another cooperating writer'))
        lock.unlink()
        self.invoke()
        self.assertFalse(lock.exists())

    def test_native_root_is_external_to_request_and_read_actions_cannot_write(self):
        before = self.package()
        self.assertEqual(self.native(root=False).returncode, 1)
        for operation in ['parse', 'view']:
            process = subprocess.run([sys.executable, str(ROOT / 'scripts/review_ledger.py'),
                operation, '--write-root', ''], input='{}', capture_output=True, text=True)
            self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
        request = copy.deepcopy(self.request)
        request['write_root'] = str(self.root)
        self.assertEqual(self.native(request).returncode, 1)
        request = {k: self.request[k] for k in ['ledger', 'ledger_sha256']}
        request['action'] = 'check-capture'
        self.assertEqual(self.native(request).returncode, 1)
        self.assertEqual(self.package(), before)
        process = self.native(public=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        report = json.loads(process.stdout)
        self.assertEqual(report['status'], 'success')
        self.assertEqual(set(report['steps']), {'capture-write-body', 'apply-bound-file-change'})
        result = json.loads(report['result']['view_text'])
        self.assertEqual(result['execution_acceptance'], 'pending')
        self.assertEqual((self.root / 'result.bin').read_bytes(), self.prepared.read_bytes())


if __name__ == '__main__':
    unittest.main()
