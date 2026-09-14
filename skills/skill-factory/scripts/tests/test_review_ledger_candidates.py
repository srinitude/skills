"""Finite candidate views preserve identity and never imply accepted relationships."""
import copy
import itertools
import json
import sys
import unittest
from pathlib import Path

import test_review_ledger_derived as derived_cases
import test_review_ledger_runtime as runtime_cases

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_ledger_graph import view


def ledger():
    data = derived_cases.captured_ledger()
    for row, kind in zip(data['source_records'], ['heading', 'obligation', 'reference']):
        row['kind'] = kind
    return data


def _TestCandidateViews_setUp(self):
    self.data = ledger()
    self.members = ['source:1', 'source:2', 'source:3']

def _TestCandidateViews_select(self, **changes):
    selection = dict(members=self.members, size=2, order='ordered', repeats=False, budget=1000)
    selection.update(changes.pop('selection', {}))
    return view(self.data, dict(action='selections', selection=selection, offset='0', limit=20, **changes))

def _TestCandidateViews_test_complete_small_spaces_match_independent_standard_iterators(self):
    modes = [('ordered', False, itertools.permutations), ('ordered', True, itertools.product),
             ('unordered', False, itertools.combinations), ('unordered', True, itertools.combinations_with_replacement)]
    for count, size, (order, repeats, iterator) in itertools.product(range(4), range(6), modes):
        members = self.members[:count]
        expected = list(iterator(members, repeat=size) if iterator is itertools.product else iterator(members, size))
        request = dict(action='selections', selection=dict(members=members, size=size, order=order,
                       repeats=repeats, budget=10000), offset='0', limit=1000)
        actual = view(self.data, request)
        self.assertEqual(actual['total'], str(len(expected)))
        self.assertEqual([tuple(row['members']) for row in actual['items']], expected)
        self.assertIsNone(actual['next_offset'])

def _TestCandidateViews_test_large_exact_rank_uses_its_declared_budget_without_prefix_rescanning(self):
    request = dict(action='selections', selection=dict(members=self.members, size=80,
        order='ordered', repeats=True, budget=500), offset=str(3**80-1), limit=1)
    result = view(self.data, request)
    self.assertEqual(result['total'], str(3**80))
    self.assertEqual(result['items'][0]['index'], request['offset'])
    self.assertEqual(result['items'][0]['members'], ['source:3']*80)
    self.assertLessEqual(result['work_slots'], 500)
    self.assertIsNone(result['next_offset'])

def _TestCandidateViews_test_pair_pages_cover_every_subject_and_rule_only_space_without_acceptance(self):
    request = dict(action='pairs', scope='all', offset='0', limit=17, budget=1000)
    result, items = view(self.data, request), []
    self.assertEqual((result['node_count'], result['total']), (15, '225'))
    while True:
        items.extend(result['items'])
        if result['next_offset'] is None:
            break
        request['offset'] = result['next_offset']
        result = view(self.data, request)
    self.assertEqual(len(items), 225)
    self.assertEqual(len({(item['from'],item['to']) for item in items}), 225)
    self.assertTrue(all(item['state']=='unreviewed-candidate' for item in items))
    self.assertTrue(any(item['from']==item['to']=='file-set:governed' for item in items))
    rules = view(self.data, dict(action='pairs', scope='rules', offset='0', limit=10, budget=100))
    self.assertEqual((rules['node_count'],rules['total']), (2,'4'))
    self.assertEqual({item['from'] for item in rules['items']}, {'source:2','clause:rule'})

def _TestCandidateViews_test_all_four_modes_match_known_complete_two_position_spaces(self):
    expected = {('ordered', False): ['12','13','21','23','31','32'],
                ('ordered', True): ['11','12','13','21','22','23','31','32','33'],
                ('unordered', False): ['12','13','23'],
                ('unordered', True): ['11','12','13','22','23','33']}
    before = copy.deepcopy(self.data)
    for (order, repeats), words in expected.items():
        result = self.select(selection=dict(order=order, repeats=repeats))
        self.assertEqual([[self.members[int(c)-1] for c in word] for word in words],
                         [item['members'] for item in result['items']])
        self.assertEqual(result['total'], str(len(words)))
        self.assertIsNone(result['next_offset'])
        self.assertTrue(all(item['state']=='unreviewed-candidate' for item in result['items']))
    self.assertEqual(self.data, before)

def _TestCandidateViews_test_unordered_pool_reordering_is_stable_but_meaningful_order_and_repeats_survive(self):
    forward = self.select(selection=dict(order='unordered'))
    backward = self.select(selection=dict(order='unordered', members=list(reversed(self.members))))
    self.assertEqual(forward, backward)
    self.assertNotEqual(self.select()['items'], self.select(selection=dict(members=list(reversed(self.members))))['items'])
    self.assertNotEqual(self.select()['items'], self.select(selection=dict(repeats=True))['items'])

def _TestCandidateViews_test_empty_and_zero_length_spaces_and_out_of_range_pages_are_truthful(self):
    for order in ['ordered', 'unordered']:
        for repeats in [False, True]:
            result = self.select(selection=dict(members=[], size=0, order=order, repeats=repeats))
            self.assertEqual((result['total'], result['items'][0]['members']), ('1', []))
            result = self.select(selection=dict(members=[], size=1, order=order, repeats=repeats))
            self.assertEqual((result['total'], result['items'], result['next_offset']), ('0', [], None))
    self.assertEqual(self.select(selection=dict(size=4))['total'], '0')
    request = dict(action='selections', selection=dict(members=self.members, size=2, order='ordered', repeats=False, budget=1000), offset='99', limit=2)
    self.assertEqual(view(self.data, request)['items'], [])

def _TestCandidateViews_test_selection_pages_join_exactly_and_reject_bad_bounds_members_and_budgets(self):
    request = dict(action='selections', selection=dict(members=self.members, size=2, order='unordered', repeats=True, budget=1000), offset='0', limit=2)
    first = view(self.data, request)
    request['offset'] = first['next_offset']
    second = view(self.data, request)
    request['offset'] = second['next_offset']
    last = view(self.data, request)
    self.assertEqual(first['items']+second['items']+last['items'], self.select(selection=dict(order='unordered',repeats=True))['items'])
    invalid = [dict(offset='-1'),dict(offset='01'),dict(offset=1),dict(limit=0),dict(limit=True),
               dict(selection={**request['selection'],'budget':1}),dict(selection={**request['selection'],'size':True}),
               dict(selection={**request['selection'],'members':['source:1','source:1']}),
               dict(selection={**request['selection'],'members':['missing']}),dict(selection={**request['selection'],'repeats':'yes'})]
    for change in invalid:
        with self.assertRaises(ValueError):
            view(self.data, {**request, **change})
    self.assertTrue(self.select()['items'])


class TestCandidateViews(unittest.TestCase):
    setUp = _TestCandidateViews_setUp
    select = _TestCandidateViews_select
    test_all_four_modes_match_known_complete_two_position_spaces = _TestCandidateViews_test_all_four_modes_match_known_complete_two_position_spaces
    test_complete_small_spaces_match_independent_standard_iterators = _TestCandidateViews_test_complete_small_spaces_match_independent_standard_iterators
    test_large_exact_rank_uses_its_declared_budget_without_prefix_rescanning = _TestCandidateViews_test_large_exact_rank_uses_its_declared_budget_without_prefix_rescanning
    test_unordered_pool_reordering_is_stable_but_meaningful_order_and_repeats_survive = _TestCandidateViews_test_unordered_pool_reordering_is_stable_but_meaningful_order_and_repeats_survive
    test_empty_and_zero_length_spaces_and_out_of_range_pages_are_truthful = _TestCandidateViews_test_empty_and_zero_length_spaces_and_out_of_range_pages_are_truthful
    test_pair_pages_cover_every_subject_and_rule_only_space_without_acceptance = _TestCandidateViews_test_pair_pages_cover_every_subject_and_rule_only_space_without_acceptance
    test_selection_pages_join_exactly_and_reject_bad_bounds_members_and_budgets = _TestCandidateViews_test_selection_pages_join_exactly_and_reject_bad_bounds_members_and_budgets


class TestNativeCandidates(unittest.TestCase):
    setUp = runtime_cases.TestLedgerRuntime.setUp
    invoke = runtime_cases.TestLedgerRuntime.invoke
    result = runtime_cases.TestLedgerRuntime.result

    def test_native_selection_preserves_exact_rank_rejects_invalid_budget_and_recovers(self):
        self.data = ledger()
        self.ledger.write_text(json.dumps(self.data))
        options = dict(action='selections', offset=str(2**60-1), limit=1,
            selection=dict(members=['source:1','source:2'], size=60, order='ordered', repeats=True, budget=300))
        result = json.loads(self.result(self.invoke(**options))['view_text'])
        self.assertEqual(result['items'][0]['members'], ['source:2']*60)
        original = self.ledger.read_bytes()
        invalid = {**options, 'selection':{**options['selection'],'budget':1}}
        self.assertEqual(self.invoke(**invalid).returncode, 1)
        self.assertEqual(self.ledger.read_bytes(), original)
        self.result(self.invoke(**options))


    def test_native_candidate_option_ownership_and_required_fields_are_enforced(self):
        self.data = ledger()
        self.ledger.write_text(json.dumps(self.data))
        valid = dict(action='pairs', scope='rules', offset='0', limit=4, budget=100)
        self.assertEqual(json.loads(self.result(self.invoke(**valid))['view_text'])['total'], '4')
        for extra in [dict(selector='source:1'), dict(depth=1), dict(selection={}), dict(offset=0)]:
            self.assertEqual(self.invoke(**{**valid, **extra}).returncode, 1)
        for field in ['scope', 'offset', 'limit', 'budget']:
            self.assertEqual(self.invoke(**{key:value for key,value in valid.items() if key!=field}).returncode, 1)
        self.assertEqual(self.invoke(action='catalog', offset='0').returncode, 1)
        self.result(self.invoke(**valid))


if __name__ == '__main__':
    unittest.main()
