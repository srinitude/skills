"""Counterexamples for preserving existing CI work during standardization."""
import sys
import tomllib
import unittest
from cli import SCRIPTS

sys.path.insert(0, str(SCRIPTS))
from standardization_mise import normalize_mise


def _TestCICommandPreservation_source(self, command):
    return ('[tasks.anchor]\ndescription = "Read a clock anchor"\ndepends = []\nrun = "true"\n'
            '[tasks.ci]\ndescription = "Check the clock"\ndepends = ["anchor"]\nrun = ' + command + '\n')

def _TestCICommandPreservation_test_custom_ci_command_is_not_deleted(self):
    source = self.source('"python3 scripts/check_domain_output.py --strict"')
    expected = tomllib.loads(source)['tasks']['ci']['run']
    normalized = normalize_mise(source)
    self.assertEqual(tomllib.loads(normalized)['tasks']['ci'].get('run'), expected)
    self.assertEqual(normalize_mise(normalized), normalized)

def _TestCICommandPreservation_test_ci_array_keeps_custom_command_order(self):
    source = self.source('["python3 scripts/first_check.py", "python3 scripts/second_check.py"]')
    self.assertEqual(tomllib.loads(normalize_mise(source))['tasks']['ci'].get('run'),
                     tomllib.loads(source)['tasks']['ci']['run'])

def _TestCICommandPreservation_test_compound_nested_mise_is_not_silently_truncated(self):
    source = self.source('"mise run anchor && python3 scripts/check_domain_output.py --strict"')
    with self.assertRaisesRegex(ValueError, 'explicit reconciliation'):
        normalize_mise(source)

def _TestCICommandPreservation_test_nested_mise_arguments_are_not_silently_lost(self):
    source = self.source('"mise run anchor -- --format json"')
    with self.assertRaisesRegex(ValueError, 'explicit reconciliation'):
        normalize_mise(source)

def _assert_task_context(self, before, after):
    for key in ['env', 'sources', 'outputs', 'hide', 'depends']:
        self.assertEqual(after.get(key), before[key], key)

def _TestCICommandPreservation_test_all_profile_overrides_keep_existing_task_context(self):
    source = '[tasks.prepare]\ndescription = "Prepare the clock"\nrun = "true"\ndepends = []\n'
    source += self.source('"python3 scripts/check_domain_output.py"').replace(
        'depends = []', 'depends = ["prepare"]', 1).replace(
        'run = "true"', 'run = "python3 scripts/anchor.py"\nenv = { TZ = "UTC" }\n'
        'sources = ["zone.json"]\noutputs = ["clock.txt"]\nhide = true')
    base = {'main_task': 'anchor', 'main_run': 'python3 scripts/anchor.py', 'primary_term': 'clock anchor'}
    script = {'anchor': {'script': 'anchor.py', 'description': 'Read the clock'}}
    command = {'anchor': {'run': 'python3 scripts/anchor.py', 'description': 'Read the clock'}}
    before = tomllib.loads(source)['tasks']['anchor']
    for profile in [base, dict(base, script_tasks=script), dict(base, command_tasks=command)]:
        with self.subTest(profile=profile):
            normalized = normalize_mise(source, profile)
            after = tomllib.loads(normalized)['tasks']['anchor']
            _assert_task_context(self, before, after)
            self.assertEqual(normalize_mise(normalized, profile), normalized)


class TestCICommandPreservation(unittest.TestCase):
    source = _TestCICommandPreservation_source
    test_custom_ci_command_is_not_deleted = _TestCICommandPreservation_test_custom_ci_command_is_not_deleted
    test_ci_array_keeps_custom_command_order = _TestCICommandPreservation_test_ci_array_keeps_custom_command_order
    test_compound_nested_mise_is_not_silently_truncated = _TestCICommandPreservation_test_compound_nested_mise_is_not_silently_truncated
    test_nested_mise_arguments_are_not_silently_lost = _TestCICommandPreservation_test_nested_mise_arguments_are_not_silently_lost
    test_all_profile_overrides_keep_existing_task_context = _TestCICommandPreservation_test_all_profile_overrides_keep_existing_task_context


if __name__ == '__main__':
    unittest.main()
