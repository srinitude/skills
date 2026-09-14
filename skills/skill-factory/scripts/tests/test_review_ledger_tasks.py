"""Captured task references retain native field distinctions and unresolved inputs."""
import copy
import json
import sys
import unittest
from pathlib import Path

import test_review_ledger_derived as derived_cases
import test_review_ledger_runtime as runtime_cases

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_ledger_graph import view


def task_ledger():
    data = derived_cases.captured_ledger()
    tasks = {name: 'echo task' for name in ['prepare', 'scheduled', 'cleanup', 'first', 'left', 'right', 'last', 'windows']}
    tasks['build'] = {
        'depends': ['prepare', ['prepare', '--literal', 'λ'],
                    {'task': 'prepare', 'args': ['a b'], 'env': {'MODE': 'x'}, 'optional': True}],
        'wait_for': ['scheduled'], 'depends_post': ['cleanup'],
        'run': ['echo prepare', {'task': 'first', 'args': ['a b'], 'env': {'MODE': 'λ'}},
                {'tasks': ['left', 'right', 'left']}, {'task': 'last'}],
        'run_windows': [{'task': 'windows'}], 'env': {'PARENT': 'keep'},
        'condition': '{{vars.ready}}', 'extension': {'opaque': 'λ\r\n'}}
    data['semantic_model']['relationship_types']['executes-before'] = {
        'family': 'order', 'meaning': 'A conditional declaration of execution order.',
        'transitivity': 'not implied', 'review_state': 'reviewed'}
    data['package_snapshot'] = {'files': {name: {'sha256': '1' * 64} for name in ['SKILL.md', 'mise.toml']}}
    data['dependency_snapshot'] = {'version': 2, 'method': 'python-imports-and-toml-tasks-v2',
        'files': {'mise.toml': {'sha256': '1' * 64, 'syntax_imports': [], 'mise_tasks': tasks}}}
    return data


def _TestTaskRelationships_setUp(self):
    self.data = task_ledger()

def _TestTaskRelationships_show(self):
    return view(self.data, {'action': 'show', 'selector': 'task:mise.toml#build'})

def _TestTaskRelationships_test_detail_retains_all_reference_forms_parent_and_opaque_fields(self):
    before = copy.deepcopy(self.data)
    shown = self.show()
    entry = shown['entry']
    self.assertEqual(entry['declaration'], before['dependency_snapshot']['files']['mise.toml']['mise_tasks']['build'])
    self.assertEqual(len(entry['references']), 11)
    self.assertEqual(entry['unresolved_references'], [])
    self.assertEqual(entry['sha256'], '1' * 64)
    order = shown['context']['subjects']
    self.assertLess(order.index('file:mise.toml'), order.index('task:mise.toml#build'))
    self.assertEqual(self.data, before)

def _TestTaskRelationships_test_declared_edges_keep_native_direction_condition_grouping_and_repetition(self):
    edges = self.show()['context']['relationships']
    selected = [edge for edge in edges if edge.get('task_field')]
    self.assertEqual(len(selected), 11)
    self.assertEqual(len({edge['id'] for edge in selected}), 11)
    for edge in selected:
        self.assertEqual(edge['subject_sha256'], '1' * 64)
        self.assertEqual(edge['basis_kind'], 'recorded-current-task-declaration')
        self.assertIn('No native resolution', edge['condition'])
        if edge['task_field'] == 'depends':
            self.assertEqual((edge['from'], edge['to']), ('task:mise.toml#prepare', 'task:mise.toml#build'))
        if edge['task_field'] == 'depends_post':
            self.assertEqual(edge['from'], 'task:mise.toml#build')
            self.assertIn('started', edge['condition'])
        if edge['task_field'] == 'wait_for':
            self.assertIn('already scheduled', edge['condition'])
    parallel = [edge for edge in selected if edge.get('grouping') == 'parallel-run-entry']
    self.assertEqual([edge['to'] for edge in parallel], ['task:mise.toml#left', 'task:mise.toml#right', 'task:mise.toml#left'])
    self.assertEqual([edge['locator'][-1] for edge in parallel], [0, 1, 2])
    self.assertTrue(all(edge['run_entry'] == 2 for edge in parallel))

def _TestTaskRelationships_test_unknown_alias_pattern_argument_and_future_forms_stay_unresolved(self):
    tasks = self.data['dependency_snapshot']['files']['mise.toml']['mise_tasks']
    tasks['prepare'] = {'alias': 'alias', 'run': 'echo task'}
    tasks['build'] = {'depends': ['prepare --flag', 'build:*', 'alias', ['missing', 'x'],
                                 {'task': '{{vars.target}}'}],
                      'run': [{'future_reference': 'prepare'}, 'prepare']}
    entry = self.show()['entry']
    self.assertEqual(len(entry['unresolved_references']), 6)
    self.assertTrue(all(row['target'] is None for row in entry['references']))
    self.assertEqual(entry['declaration'], tasks['build'])

def _TestTaskRelationships_test_stale_or_invalid_task_observations_fail_and_restoration_recovers(self):
    valid = copy.deepcopy(self.data)
    for change in [lambda d: d['dependency_snapshot'].update(version=True),
                   lambda d: d['dependency_snapshot'].update(method='unknown'),
                   lambda d: d['dependency_snapshot']['files']['mise.toml'].update(sha256='2' * 64),
                   lambda d: d['dependency_snapshot']['files']['mise.toml'].update(mise_tasks=[]),
                   lambda d: d['dependency_snapshot']['files']['mise.toml']['mise_tasks'].update(build=False),
                   lambda d: d['package_snapshot']['files'].pop('mise.toml')]:
        self.data = copy.deepcopy(valid)
        change(self.data)
        with self.assertRaises(ValueError):
            self.show()
    self.data = valid
    self.assertEqual(len(self.show()['entry']['references']), 11)

def _TestTaskRelationships_test_unprofiled_views_keep_assertions_without_derived_task_edges(self):
    del self.data['semantic_model']['derived_relationships']
    shown = self.show()
    self.assertEqual(shown['context']['relationships'], [])
    self.assertEqual(len(shown['entry']['references']), 11)


class TestTaskRelationships(unittest.TestCase):
    setUp = _TestTaskRelationships_setUp
    show = _TestTaskRelationships_show
    test_detail_retains_all_reference_forms_parent_and_opaque_fields = _TestTaskRelationships_test_detail_retains_all_reference_forms_parent_and_opaque_fields
    test_declared_edges_keep_native_direction_condition_grouping_and_repetition = _TestTaskRelationships_test_declared_edges_keep_native_direction_condition_grouping_and_repetition
    test_unknown_alias_pattern_argument_and_future_forms_stay_unresolved = _TestTaskRelationships_test_unknown_alias_pattern_argument_and_future_forms_stay_unresolved
    test_stale_or_invalid_task_observations_fail_and_restoration_recovers = _TestTaskRelationships_test_stale_or_invalid_task_observations_fail_and_restoration_recovers
    test_unprofiled_views_keep_assertions_without_derived_task_edges = _TestTaskRelationships_test_unprofiled_views_keep_assertions_without_derived_task_edges


class TestNativeTaskRelationships(unittest.TestCase):
    setUp = runtime_cases.TestLedgerRuntime.setUp
    invoke = runtime_cases.TestLedgerRuntime.invoke
    result = runtime_cases.TestLedgerRuntime.result

    def test_native_task_view_rejects_stale_declarations_without_mutation_and_recovers(self):
        self.data = task_ledger()
        self.ledger.write_text(json.dumps(self.data))
        options = {'action': 'show', 'selector': 'task:mise.toml#build'}
        output = json.loads(self.result(self.invoke(**options))['view_text'])
        self.assertEqual(len(output['entry']['references']), 11)
        valid = self.ledger.read_bytes()
        self.data['dependency_snapshot']['files']['mise.toml']['sha256'] = '2' * 64
        self.ledger.write_text(json.dumps(self.data))
        invalid = self.ledger.read_bytes()
        self.assertEqual(self.invoke(**options).returncode, 1)
        self.assertEqual(self.ledger.read_bytes(), invalid)
        self.ledger.write_bytes(valid)
        self.result(self.invoke(**options))


if __name__ == '__main__':
    unittest.main()
