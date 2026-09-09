"""Declared source and reading relations retain their captured scope."""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

import test_review_ledger_runtime as runtime_cases

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_ledger_graph import view


def document(name, contents):
    encoded = contents.encode()
    return dict(name=name, text=contents, sha256=hashlib.sha256(encoded).hexdigest(),
                bytes=len(encoded), lines=len(encoded.splitlines()))


def captured_ledger():
    text = "# Context\nRule [ref] and [ref].\n[ref]: https://example.test/definition\n"
    raw = text.encode()
    source = dict(sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw), lines=3)
    rows, start = [], 0
    for number, line in enumerate(raw.splitlines(True), 1):
        rows.append(dict(id=str(number), source_sha256=source['sha256'], byte_start=start,
                         byte_end_exclusive=start + len(line), line_start=number, line_end=number,
                         quote=line.decode(), owner_group='consumer', section={'line': 1},
                         clauses=[], source_references=['ref', 'ref'] if number == 2 else []))
        start += len(line)
    rows[1]['clauses'] = [dict(id='rule', byte_start=10, byte_end_exclusive=14, quote='Rule')]
    links = json.dumps({'definitions': {'ref': {'source_line': 3}}})
    documents = [document(name, contents) for name, contents in [('source.md', text), ('source-links.json', links)]]
    definitions = {name: dict(family='structure', meaning='The stated fixture relation.',
                             transitivity='not implied', review_state='reviewed')
                   for name in ['part-of', 'contextualizes', 'references', 'read-before', 'motivates']}
    asserted = dict(id='original', type='motivates', **{'from': ['source:1', 'source:2'], 'to': 'source:3'},
                    basis=['source:1'], condition='Only for the stated purpose.', meaning='An unaccepted interpretation.',
                    review_state='candidate', extension={'keep': 'λ\r\n'})
    return dict(source=source, source_records=rows, packet_documents=documents,
                source_owner_groups=[dict(id='foundation', reading_prerequisites=[]),
                                     dict(id='consumer', reading_prerequisites=['foundation'])],
                functional_file_map=[dict(path='SKILL.md', reading_prerequisites=[]),
                                     dict(path='consumer.py', reading_prerequisites=['SKILL.md'])],
                semantic_model=dict(relationship_types=definitions, relationships=[asserted],
                                    derived_relationships={'version': 1, 'rules': {
                                        name: 'Preserve declared source structure.' for name in
                                        ['clause-parent', 'row-group', 'section-context', 'reference-definition']}}))


class TestDerivedLedger(unittest.TestCase):
    def setUp(self):
        self.data = captured_ledger()

    def edges(self, selector, **options):
        return view(self.data, dict(action='relations', selector=selector, **options))

    def test_source_structure_and_assertions_keep_identity_and_repetition(self):
        before = copy.deepcopy(self.data)
        edges = self.edges('source:2')
        self.assertIn(self.data['semantic_model']['relationships'][0], edges)
        references = [edge for edge in edges if edge['type'] == 'references']
        self.assertEqual(len(references), 2)
        self.assertEqual(len({edge['id'] for edge in references}), 2)
        self.assertTrue(all(edge['to'] == 'source:3' for edge in references))
        self.assertTrue(any(edge['from'] == 'clause:rule' and edge['to'] == 'source:2' for edge in edges))
        self.assertTrue(any(edge['from'] == 'source:1' and edge['type'] == 'contextualizes' for edge in edges))
        self.assertEqual(self.data, before)

    def test_declared_reading_is_distinct_from_execution(self):
        basis = 'Use the declared provider under its retained source conditions.'
        self.data['source_owner_groups'][1]['reading_order_basis'] = basis
        group = self.edges('group:consumer', relation_type='read-before')
        self.assertEqual([(x['from'], x['to']) for x in group], [('group:foundation', 'group:consumer')])
        self.assertEqual(group[0]['declared_context']['reading_order_basis'], basis)
        files = self.edges('file:consumer.py', relation_type='read-before')
        self.assertEqual([(x['from'], x['to']) for x in files], [('file:SKILL.md', 'file:consumer.py')])
        self.assertEqual(files[0]['basis_kind'], 'historical-file-reading-declaration')
        self.assertIn('No execution', files[0]['condition'])

    def test_trace_and_detail_include_derived_edges_without_transitive_truth(self):
        traced = view(self.data, dict(action='trace', selector='clause:rule', depth=2, direction='out', relation_type='part-of'))
        self.assertEqual(set(traced['nodes']), {'clause:rule', 'source:2', 'group:consumer'})
        detail = view(self.data, dict(action='show', selector='clause:rule'))
        self.assertTrue(any(edge['type'] == 'references' for edge in detail['context']['relationships']))
        self.assertIn('derived_relationships', view(self.data, dict(action='catalog')))

    def test_missing_bindings_unknown_rules_and_reading_cycles_reject_then_recover(self):
        valid = copy.deepcopy(self.data)
        for change in [lambda d: d['source_records'][1]['section'].update(line=99),
                       lambda d: d['source_records'][1].update(owner_group='absent'),
                       lambda d: d['source_records'][1].update(source_references=['absent']),
                       lambda d: d['semantic_model']['derived_relationships']['rules'].update(unknown='Unimplemented'),
                       lambda d: d['source_owner_groups'][0].update(reading_prerequisites=['consumer']),
                       lambda d: d['functional_file_map'][0].update(reading_prerequisites=['consumer.py']),
                       lambda d: d['functional_file_map'][1].update(reading_prerequisites=['missing.py'])]:
            self.data = copy.deepcopy(valid)
            change(self.data)
            with self.assertRaises(ValueError):
                self.edges('source:2')
        self.data = valid
        self.assertTrue(self.edges('source:2'))

    def test_current_import_observations_replace_old_imports_and_reject_staleness(self):
        self.data['functional_file_map'].append(dict(path='old.py', reading_prerequisites=['SKILL.md']))
        baseline = self.data['functional_file_map'][1]
        baseline['reading_prerequisites'].append('old.py')
        baseline['syntax_imports'] = [{'resolved_local_files': ['old.py']}]
        self.data['package_snapshot'] = {'files': {name: {'sha256': '1' * 64} for name in ['SKILL.md', 'consumer.py', 'new.py']}}
        self.data['dependency_snapshot'] = {'files': {'consumer.py': {'sha256': '1' * 64,
            'syntax_imports': [{'resolved_local_files': ['new.py']}], 'mise_tasks': None}}}
        detail = view(self.data, dict(action='show', selector='file:consumer.py'))
        self.assertEqual(detail['entry']['dependency_observation'], self.data['dependency_snapshot']['files']['consumer.py'])
        edges = self.edges('file:consumer.py', relation_type='read-before')
        self.assertEqual({edge['from'] for edge in edges}, {'file:SKILL.md', 'file:new.py'})
        self.assertTrue(all(edge['basis_kind'] == 'recorded-current-import-reading' for edge in edges))
        self.data['dependency_snapshot']['files']['consumer.py']['sha256'] = '2' * 64
        with self.assertRaises(ValueError):
            self.edges('file:consumer.py')
        self.data['dependency_snapshot']['files']['consumer.py']['sha256'] = '1' * 64
        self.assertTrue(self.edges('file:consumer.py'))


class TestNativeDerivedLedger(unittest.TestCase):
    setUp = runtime_cases.TestLedgerRuntime.setUp
    invoke = runtime_cases.TestLedgerRuntime.invoke
    result = runtime_cases.TestLedgerRuntime.result

    def test_native_derived_source_relations_reject_missing_context_and_recover(self):
        self.data = captured_ledger()
        self.ledger.write_text(json.dumps(self.data))
        options = dict(action="relations", selector="source:2", relation_type="references", direction="out")
        result = self.result(self.invoke(**options))
        edges = json.loads(result["view_text"])
        self.assertEqual([edge["reference_ordinal"] for edge in edges], [0, 1])
        self.assertTrue(all(edge["to"] == "source:3" for edge in edges))
        valid = self.ledger.read_bytes()
        self.data["source_records"][1]["section"]["line"] = 99
        self.ledger.write_text(json.dumps(self.data))
        invalid = self.ledger.read_bytes()
        self.assertEqual(self.invoke(**options).returncode, 1)
        self.assertEqual(self.ledger.read_bytes(), invalid)
        self.ledger.write_bytes(valid)
        self.result(self.invoke(**options))


if __name__ == '__main__':
    unittest.main()
