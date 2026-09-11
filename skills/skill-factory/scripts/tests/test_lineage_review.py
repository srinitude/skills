"""Actual lineage planning, protected effects, interference and reviewed recovery."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

from cli import run
import test_review_ledger_write as writes
from check_lineage import current_document
from skill_package import package_lock

INTERFERENCE = '''import json, sys
from pathlib import Path
from check_lineage import report
root, request = Path(sys.argv[1]), Path(sys.argv[2])
target = root / 'evals/source-lineage.json'
subject = root / 'note.bin' if sys.argv[3] == 'package' else request
original, armed = subject.read_bytes(), False
def interfere(event, args):
    global armed
    if event in {'os.rename', 'os.link'} and args[1] == str(target):
        armed = True
    elif event == 'open' and args[0] == str(subject) and armed:
        armed = False
        subject.write_bytes(original + b' ')
sys.addaudithook(interfere)
try:
    report(root, write=True, review=request)
except ValueError as error:
    print(str(error), file=sys.stderr)
    sys.exit(1)
'''


def _TestLineageReview_prepare(self):
    self.prepared.write_text(json.dumps(current_document(self.root), indent=2) + '\n')
    self.request['change']['new_file']['sha256'] = writes.sha(self.prepared.read_bytes())
    self.request['change']['expected_sha256'] = writes.sha(self.target.read_bytes()) if self.target.exists() else None
    self.request_path.write_text(json.dumps(self.request))

def _TestLineageReview_invoke(self):
    return run('check_lineage.py', self.root, '--write', '--review', self.request_path)

def _TestLineageReview_test_missing_review_rejects_without_file_effect(self):
    before = self.package()
    result = run('check_lineage.py', self.root, '--write')
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.assertIn('review', result.stdout.lower())
    self.assertEqual(self.package(), before)

def _TestLineageReview_test_plan_is_complete_and_read_only(self):
    before = self.package()
    result = run('check_lineage.py', self.root, '--plan')
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    plan = json.loads(result.stdout)
    self.assertEqual(plan['content_utf8'].encode(), self.prepared.read_bytes())
    self.assertEqual(json.loads(plan['content_utf8']), current_document(self.root))
    self.assertEqual(self.package(), before)
    rejected = run('check_lineage.py', self.root, '--review', self.request_path)
    self.assertEqual(rejected.returncode, 2, rejected.stdout + rejected.stderr)
    self.assertEqual(self.package(), before)
    from check_lineage import report
    for options in [{'review': self.request_path}, {'write': True, 'plan': True}]:
        with self.assertRaises(ValueError):
            report(self.root, **options)
    self.assertEqual(self.package(), before)

def _TestLineageReview_test_false_or_null_effect_checks_cannot_succeed(self):
    from review_ledger_write import write_file
    before = self.package()
    for value in [False, None]:
        with self.assertRaises(ValueError):
            write_file(self.request, self.root, effect_check=lambda: value)
        self.assertEqual(self.package(), before)
        results = iter([True, value])
        with self.assertRaises(ValueError):
            write_file(self.request, self.root, effect_check=lambda: next(results))
        self.assertEqual(self.package(), before)
    result = write_file(self.request, self.root, effect_check=lambda: True)
    self.assertEqual(result['execution_acceptance'], 'pending')

def _TestLineageReview_setUp(self):
    writes.TestLedgerWrite.setUp(self)
    body = self.root / 'SKILL.md'
    body.write_text('---\nname: sample\ndescription: "Use when testing."\n'
                    'metadata:\n  version: "1.0.0"\n---\nRead every governing input.\n')
    (self.root / 'evals').mkdir()
    (self.root / 'evals/cases.json').write_text(json.dumps({'cases': [{'source_id': 'CASE-1'}]}))
    (self.root / 'note.bin').write_bytes(b'owned data')
    self.target = self.root / 'evals/source-lineage.json'
    self.request['change']['path'] = 'evals/source-lineage.json'
    self.request['change']['body_sha256'] = writes.sha(body.read_bytes())
    self.request['initial_body_review'] = writes.initial_body_review(self)
    self.request_path = self.folder / 'lineage-request.json'
    self.prepare()

def _TestLineageReview_test_reviewed_creation_replacement_modes_and_stale_rejection(self):
    result = self.invoke()
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertEqual(json.loads(self.target.read_bytes()), current_document(self.root))
    self.target.chmod(0o640)
    (self.root / 'note.bin').write_bytes(b'new owned data')
    before = self.package(); rejected = self.invoke()
    self.assertEqual(rejected.returncode, 1, rejected.stdout + rejected.stderr)
    self.assertEqual(self.package(), before)
    self.prepare(); result = self.invoke()
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.assertEqual(self.target.stat().st_mode & 0o777, 0o640)
    self.assertEqual(json.loads(self.target.read_bytes()), current_document(self.root))
    self.assertEqual(run('check_lineage.py', self.root).returncode, 0)

def _TestLineageReview_test_wrong_target_tampered_metadata_and_stale_review_reject_then_recover(self):
    before = self.package(); original = copy.deepcopy(self.request)
    changes = [lambda r: r.update(change=[]),
               lambda r: r.update(expected_documents=None),
               lambda r: r['change'].update(path='other.json'),
               lambda r: r.pop('initial_body_review'),
               lambda r: r['initial_body_review'].update(sha256='0'*64)]
    for change in changes:
        request = copy.deepcopy(original); change(request)
        self.request_path.write_text(json.dumps(request)); rejected = self.invoke()
        self.assertEqual(rejected.returncode, 1, rejected.stdout + rejected.stderr)
        self.assertEqual(self.package(), before)
    self.prepared.write_text('{}\n')
    self.request['change']['new_file']['sha256'] = writes.sha(self.prepared.read_bytes())
    self.request_path.write_text(json.dumps(self.request)); rejected = self.invoke()
    self.assertEqual(rejected.returncode, 1, rejected.stdout + rejected.stderr)
    self.assertEqual(self.package(), before)
    self.prepare(); result = self.invoke()
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

def _TestLineageReview_test_package_and_request_drift_restore_lineage_then_current_inputs_recover(self):
    result = self.invoke(); self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    self.target.chmod(0o640)
    for kind in ['package', 'request']:
        (self.root / 'note.bin').write_bytes(b'changed ' + kind.encode()); self.prepare()
        previous = self.target.read_bytes()
        subject = self.root / 'note.bin' if kind == 'package' else self.request_path
        original = subject.read_bytes()
        result = subprocess.run([sys.executable, '-c', INTERFERENCE, str(self.root), str(self.request_path), kind],
                                cwd=writes.ROOT / 'scripts', capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(subject.read_bytes(), original + b' ')
        self.assertEqual((self.target.read_bytes(), self.target.stat().st_mode & 0o777), (previous, 0o640))
        self.prepare(); result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

def _TestLineageReview_test_cooperating_lock_blocks_effect_then_release_recovers(self):
    before = self.package()
    with package_lock(self.root):
        result = self.invoke()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.assertEqual(self.package(), before)
    result = self.invoke(); self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class TestLineageReview(unittest.TestCase):
    package = writes.TestLedgerWrite.package
    setUp = _TestLineageReview_setUp
    prepare = _TestLineageReview_prepare
    invoke = _TestLineageReview_invoke
    test_missing_review_rejects_without_file_effect = _TestLineageReview_test_missing_review_rejects_without_file_effect
    test_plan_is_complete_and_read_only = _TestLineageReview_test_plan_is_complete_and_read_only
    test_reviewed_creation_replacement_modes_and_stale_rejection = _TestLineageReview_test_reviewed_creation_replacement_modes_and_stale_rejection
    test_wrong_target_tampered_metadata_and_stale_review_reject_then_recover = _TestLineageReview_test_wrong_target_tampered_metadata_and_stale_review_reject_then_recover
    test_package_and_request_drift_restore_lineage_then_current_inputs_recover = _TestLineageReview_test_package_and_request_drift_restore_lineage_then_current_inputs_recover
    test_cooperating_lock_blocks_effect_then_release_recovers = _TestLineageReview_test_cooperating_lock_blocks_effect_then_release_recovers
    test_false_or_null_effect_checks_cannot_succeed = _TestLineageReview_test_false_or_null_effect_checks_cannot_succeed


if __name__ == '__main__':
    unittest.main()
