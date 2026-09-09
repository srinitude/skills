"""Recorded work context stays distinct from performing or accepting a change."""
import copy
import json
import sys
import unittest
from pathlib import Path

import test_review_ledger_runtime as runtime_cases

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_ledger_graph import view


class TestWorkViews(unittest.TestCase):
    invoke = runtime_cases.TestLedgerRuntime.invoke
    result = runtime_cases.TestLedgerRuntime.result

    def setUp(self):
        runtime_cases.TestLedgerRuntime.setUp(self)
        self.data['dependency_traversal'] = {'workflow': [
            {'step': 1, 'action': 'Read', 'rule': 'Read the full current ledger.', 'extension': ['λ', None]},
            {'step': 2, 'action': 'Review', 'rule': 'Review the change before acting.'}]}
        self.data['reusable_review_protocol'] = [
            {'field': 'Core body decision', 'review': 'Keep core behavior in the body.', 'condition': 'Every change.'}]
        self.data['semantic_model'].update(
            body_hub={'core': 'SKILL.md', 'state': 'review pending', 'extension': {'exact': 'λ\r\n'}},
            mechanism_map={'mise': {'owner': 'mise.toml', 'state': 'historical observation'}})
        self.ledger.write_text(json.dumps(self.data))

    def test_work_preserves_entire_method_context_and_unaccepted_relationships(self):
        self.data['source_records'][0]['clauses'] = [{'id': 'part', 'quote': 'current evidence'}]
        self.data['semantic_model']['entry_reviews'] = {
            'source:review': {'facets': {'meaning': 'Review actual evidence.'}, 'state': 'partial'},
            'source:read': {'inherits': ['source:review'], 'facets': {}, 'state': 'stale'}}
        before = copy.deepcopy(self.data)
        result = view(self.data, {'action': 'work', 'selector': 'clause:part'})
        self.assertEqual(result['method'], self.data['dependency_traversal']['workflow'])
        self.assertEqual(result['review_fields'], self.data['reusable_review_protocol'])
        self.assertEqual(result['body_hub'], self.data['semantic_model']['body_hub'])
        self.assertEqual(result['mechanism_map'], self.data['semantic_model']['mechanism_map'])
        self.assertEqual(result['context']['subjects'], ['source:review', 'source:read', 'clause:part'])
        self.assertEqual(result['context']['effective_facets'], {'meaning': 'Review actual evidence.'})
        self.assertEqual(result['context']['relationships'], self.data['semantic_model']['relationships'])
        self.assertEqual(result['execution_acceptance'], 'pending')
        self.assertEqual(result['scope'], 'recorded work context only')
        self.assertEqual(self.data, before)

    def test_file_impact_preserves_old_current_and_missing_owners_without_live_claims(self):
        self.data['functional_file_map'] = [{'path': 'old.py', 'sha256': '1'*64, 'role': 'Original owner.'}]
        self.data['package_snapshot'] = {'files': {'new.py': {'sha256': '2'*64}}}
        for name, state in [('old.py', 'missing'), ('new.py', 'present')]:
            result = view(self.data, {'action': 'impact', 'selector': 'file:'+name})
            self.assertEqual(result['entry']['recorded_package_state'], state)
            self.assertEqual(result['body_hub'], self.data['semantic_model']['body_hub'])
            self.assertEqual(result['scope'], 'recorded file impact only')
            self.assertEqual(result['execution_acceptance'], 'pending')
        for selector in ['source:read', 'file-set:governed', 'file:absent.py']:
            with self.assertRaises(ValueError):
                view(self.data, {'action': 'impact', 'selector': selector})

    def test_missing_or_invalid_review_contract_rejects_without_mutation_and_recovers(self):
        invalid = []
        for key in ['dependency_traversal', 'reusable_review_protocol']:
            candidate = copy.deepcopy(self.data)
            del candidate[key]
            invalid.append(candidate)
        for key in ['body_hub', 'mechanism_map']:
            candidate = copy.deepcopy(self.data)
            candidate['semantic_model'][key] = {}
            invalid.append(candidate)
        for workflow in [[], [{'step': 2, 'action': 'Read', 'rule': 'Read.'}],
                         [{'step': True, 'action': 'Read', 'rule': 'Read.'}],
                         [{'step': 1, 'action': 'Read', 'rule': ''}]]:
            candidate = copy.deepcopy(self.data)
            candidate['dependency_traversal']['workflow'] = workflow
            invalid.append(candidate)
        candidate = copy.deepcopy(self.data)
        candidate['reusable_review_protocol'] = [{'field': 'Review', 'review': ''}]
        invalid.append(candidate)
        for candidate in invalid:
            before = copy.deepcopy(candidate)
            with self.assertRaises(ValueError):
                view(candidate, {'action': 'work', 'selector': 'source:read'})
            self.assertEqual(candidate, before)
        self.assertEqual(view(self.data, {'action': 'work', 'selector': 'source:read'})['execution_acceptance'], 'pending')

    def test_native_work_and_impact_reject_wrong_options_and_recover(self):
        original = self.ledger.read_bytes()
        valid = {'action': 'work', 'selector': 'source:read'}
        result = json.loads(self.result(self.invoke(**valid))['view_text'])
        self.assertEqual(result['method'], self.data['dependency_traversal']['workflow'])
        for options in [{'action': 'work'}, {**valid, 'depth': 1}, {**valid, 'budget': 10},
                        {**valid, 'direction': 'out'}, {'action': 'impact', 'selector': 'source:read'}]:
            self.assertEqual(self.invoke(**options).returncode, 1)
            self.assertEqual(self.ledger.read_bytes(), original)
        self.result(self.invoke(**valid))

    def test_public_work_reads_the_whole_current_body_and_does_not_execute_the_method(self):
        original = self.ledger.read_bytes()
        result = self.result(self.invoke(public=True, action='work', selector='source:read'))
        self.assertEqual(result['body']['text'].encode(), (runtime_cases.ROOT/'SKILL.md').read_bytes())
        self.assertEqual(json.loads(result['view_text'])['execution_acceptance'], 'pending')
        self.assertEqual(self.ledger.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
