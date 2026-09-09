"""Body names and physical input identity reject before protected file changes."""
import unittest
from pathlib import Path

import test_review_ledger_write as write_cases


class TestWriteBoundaries(unittest.TestCase):
    setUp = write_cases.TestLedgerWrite.setUp
    invoke = write_cases.TestLedgerWrite.invoke
    package = write_cases.TestLedgerWrite.package

    def test_body_case_aliases_are_rejected_as_body_paths(self):
        before = self.package()
        for name in ['skill.md', 'Skill.md', 'sKiLl.Md']:
            self.request['change']['path'] = name
            path = self.root / name
            self.request['change']['expected_sha256'] = write_cases.sha(path.read_bytes()) if path.exists() else None
            with self.assertRaisesRegex(ValueError, 'unsupported owned file path'):
                self.invoke()
            self.assertEqual(self.package(), before)
        self.request['change'].update(path='result.bin', expected_sha256=None)
        self.invoke()

    def test_source_alias_uses_actual_file_identity_and_preserves_the_original(self):
        original = Path(self.request['original_source']['path'])
        source = self.root / 'BOUND.txt'
        original.rename(source)
        raw = source.read_bytes()
        self.request['original_source']['path'] = str(source)
        self.request['change']['path'] = 'bound.txt'
        target = self.root / 'bound.txt'
        if target.exists():
            self.assertTrue(target.samefile(source))
            self.request['change']['expected_sha256'] = write_cases.sha(raw)
            with self.assertRaisesRegex(ValueError, 'overlaps a governing or prepared input'):
                self.invoke()
        else:
            self.invoke()
            self.assertEqual(target.read_bytes(), self.prepared.read_bytes())
        self.assertEqual(source.read_bytes(), raw)


if __name__ == '__main__':
    unittest.main()
