"""Actual related-owner file effects retain the skill's current review context."""
import copy
import unittest
from pathlib import Path

from review_ledger_write import write_file
import test_review_ledger_write as ledger_cases
from test_review_ledger_write import sha


class TestRelatedOwnerWrite(unittest.TestCase):
    def setUp(self):
        ledger_cases.TestLedgerWrite.setUp(self)
        self.target = self.folder / 'evidence/manifest.json'
        self.target.parent.mkdir()
        self.target.write_bytes(b'old manifest')
        self.target.chmod(0o640)
        self.request['change'].update(path='evidence/manifest.json', expected_sha256=sha(self.target.read_bytes()))

    def invoke(self, request=None, **kwargs):
        return write_file(request or self.request, self.root, target_root=self.folder, **kwargs)

    def test_related_target_uses_installed_body_and_preserves_mode(self):
        result = self.invoke()
        self.assertEqual(self.target.read_bytes(), self.prepared.read_bytes())
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o640)
        self.assertEqual(result['body_root'], str(self.root))
        self.assertEqual(result['target_root'], str(self.folder))
        for phase in ['before', 'after']:
            self.assertEqual(result[phase]['body']['path'], str(self.root / 'SKILL.md'))
            self.assertEqual(result[phase]['documents'], 3)

    def test_related_target_rejects_body_modes_paths_and_overlapping_inputs(self):
        for mode in ['bootstrap_body', 'body_revision']:
            request = copy.deepcopy(self.request)
            request.pop('initial_body_review')
            request[mode] = {}
            with self.assertRaises(ValueError):
                self.invoke(request)
            self.assertEqual(self.target.read_bytes(), b'old manifest')
        for name in ['../escape', 'skill/SKILL.md', 'ledger.json', 'prepared.bin']:
            request = copy.deepcopy(self.request); request['change']['path'] = name
            with self.assertRaises(ValueError):
                self.invoke(request)
        self.assertEqual(self.target.read_bytes(), b'old manifest')

    def test_related_root_must_be_a_canonical_ancestor_and_is_not_request_authority(self):
        other = self.folder / 'unrelated'; other.mkdir()
        with self.assertRaises(ValueError):
            write_file(self.request, self.root, target_root=other)
        request = copy.deepcopy(self.request); request['target_root'] = str(self.folder)
        with self.assertRaises(ValueError):
            write_file(request, self.root)
        self.assertEqual(self.target.read_bytes(), b'old manifest')

    def test_post_failure_restores_only_current_related_effect_and_recovers(self):
        def predicate():
            return self.target.read_bytes() == b'old manifest'
        with self.assertRaisesRegex(ValueError, 'after writing'):
            self.invoke(effect_check=predicate)
        self.assertEqual((self.target.read_bytes(), self.target.stat().st_mode & 0o777), (b'old manifest', 0o640))
        self.invoke()
        self.assertEqual(self.target.read_bytes(), self.prepared.read_bytes())

    def test_stale_body_review_and_related_link_reject_before_effect(self):
        review = Path(self.request['initial_body_review']['path'])
        raw = review.read_bytes(); review.write_bytes(raw + b' ')
        with self.assertRaises(ValueError):
            self.invoke()
        review.write_bytes(raw)
        self.target.unlink(); self.target.symlink_to(self.prepared)
        with self.assertRaises(ValueError):
            self.invoke()
        self.assertEqual(self.prepared.read_bytes(), b'new\x00\xff\r\n')


if __name__ == '__main__':
    unittest.main()
