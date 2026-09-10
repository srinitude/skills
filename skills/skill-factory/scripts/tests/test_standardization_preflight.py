"""Shared no-write input validation for native and workflow standardization callers."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from cli import SCRIPTS
from standardization_fixtures import profile, write_target

sys.path.insert(0, str(SCRIPTS))
import standardize_registry_skill as standardize


class TestStandardizationPreflight(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.root = self.folder / 'clock-anchor'
        write_target(self.root)
        self.profile = self.folder / 'profile.json'
        self.profile.write_text(json.dumps(profile()))

    def capture(self):
        return {p.relative_to(self.folder).as_posix(): p.read_bytes()
                for p in self.folder.rglob('*') if p.is_file() and not p.is_symlink()}

    def prepare(self, target=None, *options):
        args = standardize.parse_args([str(target or self.root), '--profile', str(self.profile), *options])
        return standardize.prepare_inputs(args)

    def test_valid_profile_and_explicit_scope_are_returned_without_effects(self):
        before = self.capture()
        root, selected, choice = self.prepare(None, '--scope', 'user')
        self.assertEqual(root, self.root)
        self.assertEqual(selected, profile())
        self.assertEqual(choice['scope'], 'user')
        self.assertEqual(self.capture(), before)

    def test_legacy_planning_keeps_unresolved_scope(self):
        before = self.capture()
        self.assertIsNone(self.prepare()[2])
        self.assertEqual(self.capture(), before)

    def test_missing_and_linked_roots_reject_before_any_other_owner_runs(self):
        link = self.folder / 'alias'
        link.symlink_to(self.root, target_is_directory=True)
        before = self.capture()
        for target in [self.folder / 'absent', link]:
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, 'target must be a real skill directory'):
                self.prepare(target)
        self.assertEqual(self.capture(), before)

    def test_invalid_profile_rejects_without_changing_the_target(self):
        self.profile.write_text('{}')
        before = self.capture()
        with self.assertRaisesRegex(ValueError, 'skill must match'):
            self.prepare()
        self.assertEqual(self.capture(), before)


if __name__ == '__main__':
    unittest.main()
