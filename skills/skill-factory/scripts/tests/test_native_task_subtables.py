"""Focused counterexamples for preserving native task subtables during normalization."""
import json
import sys
import tomllib
import unittest

from cli import SCRIPTS
sys.path.insert(0, str(SCRIPTS))
from standardization_mise import normalize_mise
from standardization_seed import base_mise

NATIVE_SOURCE = '[tasks.anchor]\ndescription = "Observe configured clock context"\ndepends = []\nrun = "printf %s \\"$CLOCK_CONTEXT\\""\n\n[tasks.anchor.env]\nCLOCK_CONTEXT = "preserved"\n'

def _TestNativeTaskSubtables_test_native_domain_environment_subtable_is_preserved(self):
    source = NATIVE_SOURCE
    normalized = normalize_mise(source)
    self.assertEqual(tomllib.loads(normalized)['tasks']['anchor'], tomllib.loads(source)['tasks']['anchor'])
    self.assertEqual(normalize_mise(normalized), normalized)

def _TestNativeTaskSubtables_test_quoted_task_names_keep_their_subtable_owner(self):
    for name in ['clock.anchor', 'clock:anchor']:
        with self.subTest(name=name):
            source = NATIVE_SOURCE.replace('[tasks.anchor', '[tasks.' + json.dumps(name))
            normalized = normalize_mise(source)
            self.assertEqual(tomllib.loads(normalized)['tasks'][name], tomllib.loads(source)['tasks'][name])
            self.assertEqual(normalize_mise(normalized), normalized)

def _TestNativeTaskSubtables_test_helper_subtable_environment_is_checked_before_replacement(self):
    source = base_mise({'primary_term': 'clock'})
    boundary = source.index('\n[tasks.', source.index('[tasks.validate]') + 1)
    source = source[:boundary] + '\n[tasks.validate.env]\nUV_PYTHON = "{{tools.python.path}}"\n' + source[boundary:]
    normalized = normalize_mise(source)
    self.assertEqual(tomllib.loads(normalized)['tasks']['validate']['env'], {'UV_PYTHON': '{{tools.python.path}}'})
    self.assertEqual(normalize_mise(normalized), normalized)
    with self.assertRaisesRegex(ValueError, 'Python helper environment'):
        normalize_mise(source.replace('{{tools.python.path}}', 'custom'))

def _TestNativeTaskSubtables_test_dependency_rewrite_does_not_write_into_ci_environment(self):
    source = '[tasks.anchor]\ndescription = "Read configured clock"\nrun = "true"\ndepends = []\n'
    source += '[tasks.ci]\ndescription = "Check clock"\ndepends = ["anchor"]\n'
    source += '[tasks.ci.env]\nCLOCK_CONTEXT = "preserved"\n'
    normalized = normalize_mise(source)
    tasks = tomllib.loads(normalized)['tasks']
    self.assertEqual(tasks['ci']['env'], {'CLOCK_CONTEXT': 'preserved'})
    self.assertIn('test', tasks['ci']['depends'])
    self.assertEqual(normalize_mise(normalized), normalized)



def _TestNativeTaskSubtables_test_full_task_bodies_survive_profile_updates(self):
    description = "# `anchor`\n\n## Work\n\nKeep [links] and \"quotes\".\nrun = 'text only'\n"
    source = NATIVE_SOURCE.replace('description = "Observe configured clock context"',
                                  "description = '''\n" + description + "''' # keep the task note")
    profile = {"primary_term": "clock", "main_task": "anchor",
               "command_tasks": {"anchor": {"description": description + "\nKeep time.",
                                           "run": "printf clock"}}}
    normalized = normalize_mise(source, profile)
    task = tomllib.loads(normalized)["tasks"]["anchor"]
    self.assertEqual(task["description"], profile["command_tasks"]["anchor"]["description"])
    self.assertEqual(task["run"], "printf clock")
    self.assertEqual(task["env"], {"CLOCK_CONTEXT": "preserved"})
    self.assertIn("# keep the task note", normalized)
    self.assertEqual(normalize_mise(normalized, profile), normalized)

class TestNativeTaskSubtables(unittest.TestCase):
    test_full_task_bodies_survive_profile_updates = _TestNativeTaskSubtables_test_full_task_bodies_survive_profile_updates
    test_native_domain_environment_subtable_is_preserved = _TestNativeTaskSubtables_test_native_domain_environment_subtable_is_preserved
    test_quoted_task_names_keep_their_subtable_owner = _TestNativeTaskSubtables_test_quoted_task_names_keep_their_subtable_owner
    test_helper_subtable_environment_is_checked_before_replacement = _TestNativeTaskSubtables_test_helper_subtable_environment_is_checked_before_replacement
    test_dependency_rewrite_does_not_write_into_ci_environment = _TestNativeTaskSubtables_test_dependency_rewrite_does_not_write_into_ci_environment


if __name__ == '__main__':
    unittest.main(verbosity=2)
