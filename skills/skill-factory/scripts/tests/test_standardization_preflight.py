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


def _TestStandardizationPreflight_setUp(self):
    temporary = tempfile.TemporaryDirectory()
    self.addCleanup(temporary.cleanup)
    self.folder = Path(temporary.name)
    self.root = self.folder / 'clock-anchor'
    write_target(self.root)
    self.profile = self.folder / 'profile.json'
    self.profile.write_text(json.dumps(profile()))

def _TestStandardizationPreflight_capture(self):
    return {p.relative_to(self.folder).as_posix(): p.read_bytes()
            for p in self.folder.rglob('*') if p.is_file() and not p.is_symlink()}

def _TestStandardizationPreflight_prepare(self, target=None, *options):
    args = standardize.parse_args([str(target or self.root), '--profile', str(self.profile), *options])
    return standardize.prepare_inputs(args)

def _TestStandardizationPreflight_test_exportable_parser_preserves_the_native_argument_contract_without_effects(self):
    before = self.capture()
    parser = standardize.build_parser()
    values = [str(self.root), '--pro', 'profile café 日本語.json', '--profile=',
              '--scope=project', '--rebase-tracked-text', '--rebase-tracked-text']
    parsed = parser.parse_args(values)
    self.assertEqual(vars(parsed), vars(standardize.parse_args(values)))
    self.assertEqual(parsed.profile, '')
    self.assertEqual(parsed.scope, 'project')
    self.assertTrue(parsed.rebase_tracked_text)
    literal = parser.parse_args(['--profile', '$(touch SHOULD_NOT_EXIST)', '--', '--help'])
    self.assertEqual(literal.skill_root, '--help')
    self.assertEqual(literal.profile, '$(touch SHOULD_NOT_EXIST)')
    self.assertEqual(parser.parse_args(['--profile', 'cfg', '--', '-leading']).skill_root, '-leading')
    self.assertEqual(self.capture(), before)

def _TestStandardizationPreflight_test_valid_profile_and_explicit_scope_are_returned_without_effects(self):
    before = self.capture()
    root, selected, choice = self.prepare(None, '--scope', 'user')
    self.assertEqual(root, self.root)
    self.assertEqual(selected, profile())
    self.assertEqual(choice['scope'], 'user')
    self.assertEqual(self.capture(), before)

def _TestStandardizationPreflight_test_legacy_planning_keeps_unresolved_scope(self):
    before = self.capture()
    self.assertIsNone(self.prepare()[2])
    self.assertEqual(self.capture(), before)

def _TestStandardizationPreflight_test_missing_and_linked_roots_reject_before_any_other_owner_runs(self):
    link = self.folder / 'alias'
    link.symlink_to(self.root, target_is_directory=True)
    before = self.capture()
    for target in [self.folder / 'absent', link]:
        with self.subTest(target=target), self.assertRaisesRegex(ValueError, 'target must be a real skill directory'):
            self.prepare(target)
    self.assertEqual(self.capture(), before)

def _TestStandardizationPreflight_test_invalid_profile_rejects_without_changing_the_target(self):
    self.profile.write_text('{}')
    before = self.capture()
    with self.assertRaisesRegex(ValueError, 'skill must match'):
        self.prepare()
    self.assertEqual(self.capture(), before)


class TestStandardizationPreflight(unittest.TestCase):
    setUp = _TestStandardizationPreflight_setUp
    capture = _TestStandardizationPreflight_capture
    prepare = _TestStandardizationPreflight_prepare
    test_valid_profile_and_explicit_scope_are_returned_without_effects = _TestStandardizationPreflight_test_valid_profile_and_explicit_scope_are_returned_without_effects
    test_exportable_parser_preserves_the_native_argument_contract_without_effects = _TestStandardizationPreflight_test_exportable_parser_preserves_the_native_argument_contract_without_effects
    test_legacy_planning_keeps_unresolved_scope = _TestStandardizationPreflight_test_legacy_planning_keeps_unresolved_scope
    test_missing_and_linked_roots_reject_before_any_other_owner_runs = _TestStandardizationPreflight_test_missing_and_linked_roots_reject_before_any_other_owner_runs
    test_invalid_profile_rejects_without_changing_the_target = _TestStandardizationPreflight_test_invalid_profile_rejects_without_changing_the_target


if __name__ == '__main__':
    unittest.main()
