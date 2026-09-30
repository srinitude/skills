"""Actual reviewed body transitions; review declarations remain unaccepted."""
import copy
import json
import unittest
from pathlib import Path

import test_review_ledger_write as writes
import test_review_ledger_write_recovery as recovery


def _TestBodyRevision_revision(self, replacing):
    self.ordinary_body_review = self.request.pop('initial_body_review')
    body = self.root / 'SKILL.md'
    previous = self.folder / 'previous-body.md'
    previous.write_bytes(body.read_bytes())
    old = writes.sha(previous.read_bytes()) if replacing else None
    self.prepared.write_bytes(b'Read the entire current ledger before and after every file change.\n')
    new = writes.sha(self.prepared.read_bytes())
    self.review_path = self.folder / 'body-review.json'
    self.review = dict(candidate_sha256=new, previous_sha256=old,
        ledger_sha256=self.request['ledger_sha256'], source_sha256=self.data['source']['sha256'],
        execution_acceptance='pending', initial_contract_validation=dict(state='PASS',
            reviewer='Fixture author; non-independent', method='Review the sole fixture rule.',
            limit='Synthetic declared review; no semantic or human acceptance.'))
    self.review_path.write_text(json.dumps(self.review))
    self.request['body_revision'] = dict(previous={'path':str(previous),'sha256':old} if replacing else None,
        review={'path':str(self.review_path),'sha256':writes.sha(self.review_path.read_bytes())})
    self.request['change'].update(path='SKILL.md', expected_sha256=old, body_sha256=old or new,
        new_file={'path':str(self.prepared),'sha256':new})
    if not replacing:
        body.unlink()
    return previous

def _TestBodyRevision_test_public_creation_installs_only_the_reviewed_body(self):
    self.revision(False)
    before = self.package()
    for value in [self.ordinary_body_review, None]:
        mixed = copy.deepcopy(self.request); mixed['initial_body_review'] = value
        with self.assertRaises(ValueError):
            self.invoke(mixed)
        self.assertEqual(self.package(), before)
    process = self.native(public=True)
    self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
    result = json.loads(json.loads(process.stdout)['result']['view_text'])
    body = self.root / 'SKILL.md'
    self.assertEqual(body.read_bytes(), self.prepared.read_bytes())
    self.assertIsNone(result['old_sha256'])
    self.assertEqual(result['after']['body']['path'], str(body))
    for phase in ['before', 'after']:
        self.assertEqual(result[phase]['body']['text'].encode(), self.prepared.read_bytes())
        self.assertEqual(result[phase]['body_revision_review'], self.review)
    self.assertEqual(result['execution_acceptance'], 'pending')

def _TestBodyRevision_test_public_replacement_reads_old_and_new_bodies_and_preserves_mode(self):
    previous = self.revision(True)
    body = self.root / 'SKILL.md'; body.chmod(0o640)
    process = self.native(public=True)
    self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
    result = json.loads(json.loads(process.stdout)['result']['view_text'])
    self.assertEqual(result['before']['body']['text'].encode(), previous.read_bytes())
    self.assertEqual(result['after']['body']['text'].encode(), self.prepared.read_bytes())
    self.assertEqual(body.stat().st_mode & 0o777, 0o640)
    for phase in ['before', 'after']:
        self.assertIn(str(previous), result[phase]['input_bytes'])
        self.assertIn(str(self.review_path), result[phase]['input_bytes'])
    before = self.package()
    with self.assertRaises((OSError, ValueError)):
        self.invoke()
    self.assertEqual(self.package(), before)

def _TestBodyRevision_test_wrong_previous_and_unfinished_review_reject_then_recover(self):
    self.revision(True); before = self.package()
    changes = [lambda v:v.update(previous_sha256='0'*64),
        lambda v:v.update(candidate_sha256='0'*64), lambda v:v.update(ledger_sha256='0'*64),
        lambda v:v.update(source_sha256='0'*64), lambda v:v.update(execution_acceptance='passed'),
        lambda v:v['initial_contract_validation'].update(state='pending')]
    for alter in changes:
        value = copy.deepcopy(self.review); alter(value)
        self.review_path.write_text(json.dumps(value))
        self.request['body_revision']['review']['sha256'] = writes.sha(self.review_path.read_bytes())
        with self.assertRaises((OSError, ValueError)):
            self.invoke()
        self.assertEqual(self.package(), before)
    self.review_path.write_text(json.dumps(self.review))
    self.request['body_revision']['review']['sha256'] = writes.sha(self.review_path.read_bytes())
    try:
        self.invoke()
    except (OSError, ValueError) as error:
        self.fail(f'A current reviewed body replacement must succeed: {error}')

def _TestBodyRevision_test_source_or_previous_snapshot_overlap_cannot_hide_behind_body_authority(self):
    self.revision(True); original = copy.deepcopy(self.request); before = self.package()
    body = self.root / 'SKILL.md'
    for kind in ['previous', 'source']:
        self.request = copy.deepcopy(original)
        binding = self.request['body_revision']['previous'] if kind == 'previous' else self.request['original_source']
        binding['path'] = str(body)
        with self.assertRaises((OSError, ValueError)):
            self.invoke()
        self.assertEqual(self.package(), before)
    self.request = original
    try:
        self.invoke()
    except (OSError, ValueError) as error:
        self.fail(f'Distinct reviewed body inputs must recover: {error}')

def _TestBodyRevision_test_blank_invalid_or_missing_candidate_rejects_before_replacement(self):
    self.revision(True); before = self.package(); original = self.prepared.read_bytes()
    for raw in [None, b'', b' \n', '\u2003'.encode(), b'\xff']:
        self.prepared.unlink(missing_ok=True)
        if raw is not None:
            self.prepared.write_bytes(raw)
            self.request['change']['new_file']['sha256'] = writes.sha(raw)
            self.review['candidate_sha256'] = writes.sha(raw)
            self.review_path.write_text(json.dumps(self.review))
            self.request['body_revision']['review']['sha256'] = writes.sha(self.review_path.read_bytes())
        with self.assertRaises((OSError, ValueError)):
            self.invoke()
        self.assertEqual(self.package(), before)
    self.prepared.write_bytes(original)
    self.request['change']['new_file']['sha256'] = writes.sha(original)
    self.review['candidate_sha256'] = writes.sha(original)
    self.review_path.write_text(json.dumps(self.review))
    self.request['body_revision']['review']['sha256'] = writes.sha(self.review_path.read_bytes())
    try:
        self.invoke()
    except (OSError, ValueError) as error:
        self.fail(f'Valid body bytes must recover: {error}')

def _TestBodyRevision_test_revision_cannot_authorize_nonbody_or_case_alias_paths(self):
    self.revision(True); before = self.package()
    for name in ['skill.md', 'Skill.md', 'result.bin']:
        self.request['change']['path'] = name
        with self.assertRaises((OSError, ValueError)):
            self.invoke()
        self.assertEqual(self.package(), before)
    self.request['change']['path'] = 'SKILL.md'
    try:
        self.invoke()
    except (OSError, ValueError) as error:
        self.fail(f'Canonical body path must recover: {error}')

def _TestBodyRevision_assert_restores(self, replacing):
    self.revision(replacing); before = self.package()
    source = Path(self.request['original_source']['path']); original = source.read_bytes()
    process = self.interrupted()
    self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
    self.assertIn('current write input digest mismatch', process.stderr)
    self.assertEqual(source.read_bytes(), original + b'changed')
    self.assertEqual(self.package(), before)
    source.write_bytes(original)
    self.invoke()
    self.assertEqual((self.root / 'SKILL.md').read_bytes(), self.prepared.read_bytes())

def _TestBodyRevision_test_creation_restores_absence_after_post_write_source_drift(self):
    self.assert_restores(False)

def _TestBodyRevision_test_replacement_restores_previous_body_after_post_write_source_drift(self):
    self.assert_restores(True)


class TestBodyRevision(unittest.TestCase):
    setUp = writes.TestLedgerWrite.setUp
    invoke = writes.TestLedgerWrite.invoke
    native = writes.TestLedgerWrite.native
    package = writes.TestLedgerWrite.package
    interrupted = recovery.TestFileRestoration.interrupted
    revision = _TestBodyRevision_revision
    test_public_creation_installs_only_the_reviewed_body = _TestBodyRevision_test_public_creation_installs_only_the_reviewed_body
    test_public_replacement_reads_old_and_new_bodies_and_preserves_mode = _TestBodyRevision_test_public_replacement_reads_old_and_new_bodies_and_preserves_mode
    test_wrong_previous_and_unfinished_review_reject_then_recover = _TestBodyRevision_test_wrong_previous_and_unfinished_review_reject_then_recover
    test_source_or_previous_snapshot_overlap_cannot_hide_behind_body_authority = _TestBodyRevision_test_source_or_previous_snapshot_overlap_cannot_hide_behind_body_authority
    test_blank_invalid_or_missing_candidate_rejects_before_replacement = _TestBodyRevision_test_blank_invalid_or_missing_candidate_rejects_before_replacement
    test_revision_cannot_authorize_nonbody_or_case_alias_paths = _TestBodyRevision_test_revision_cannot_authorize_nonbody_or_case_alias_paths
    assert_restores = _TestBodyRevision_assert_restores
    test_creation_restores_absence_after_post_write_source_drift = _TestBodyRevision_test_creation_restores_absence_after_post_write_source_drift
    test_replacement_restores_previous_body_after_post_write_source_drift = _TestBodyRevision_test_replacement_restores_previous_body_after_post_write_source_drift


if __name__ == '__main__':
    unittest.main()
