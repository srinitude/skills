"""Recorded graph identity, omission, budget and native-entry checks."""
import copy
from fnmatch import fnmatchcase
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from review_ledger_file_graph import file_graph
from review_ledger_graph import subjects, validate_graph

ROOT = Path(__file__).resolve().parents[2]


def fixture():
    files = {name: {'sha256': '1' * 64} for name in ['SKILL.md', 'mise#x.toml']}
    definition = dict(family='ownership', meaning='Recorded owner.', transitivity='not implied', review_state='reviewed')
    edge = dict(id='one', type='part-of', **{'from': ['file:mise#x.toml'] * 2, 'to': 'file:SKILL.md'},
                meaning='Each occurrence is retained.', condition='Within this fixture.',
                basis=['file:SKILL.md'], review_state='candidate', extra={'exact': 'λ\r\n'})
    return {'source': {'sha256': '2' * 64}, 'package_snapshot': {'files': files},
            'semantic_model': {'relationship_types': {'part-of': definition}, 'relationships': [edge]}}


def project(data, budget=20, index=None):
    index = subjects(data) if index is None else index
    validate_graph(data, index)
    return file_graph(data, index, {'ledger_sha256': '3' * 64, 'budget': budget})


def test_parallel_incidences_and_determinism():
    data = fixture()
    original = copy.deepcopy(data)
    graph = project(data, 2)
    assert len(graph['nodes']) == 2 and len(graph['edges']) == 2
    assert len({edge['id'] for edge in graph['edges']}) == 2
    assert [edge['from_endpoint']['ordinal'] for edge in graph['edges']] == [0, 1]
    assert graph['records'] == original['semantic_model']['relationships'] and data == original
    data['package_snapshot']['files'] = dict(reversed(list(data['package_snapshot']['files'].items())))
    assert project(data) == graph
    assert graph['mermaid'].count('@-->') == 2 and 'subgraph' not in graph['mermaid']


def test_history_and_non_file_rules_remain_explicit():
    data = fixture()
    data['functional_file_map'] = [{'path': 'retired.py'}]
    edge = data['semantic_model']['relationships'][0]
    edge['from'] = ['file:retired.py', 'file:mise#x.toml']
    graph = project(data)
    assert 'file:retired.py' not in graph['nodes'] and len(graph['edges']) == 1
    gap = graph['projection_gaps'][0]['from'][0]
    assert gap['file'] == 'file:retired.py' and 'absent' in gap['reason']
    edge['from'] = 'file:retired.py'
    assert project(data)['unprojected_records'] == ['one']
    assert project(data)['records'][0] == edge


def test_task_owner_is_explicit_and_unknown_endpoint_rejects():
    data = fixture()
    index = subjects(data)
    index['task:fixture'] = {'file': 'mise#x.toml'}
    data['semantic_model']['relationships'][0]['from'] = 'task:fixture'
    graph = project(data, index=index)
    assert graph['edges'][0]['from'] == 'file:mise#x.toml'
    data['semantic_model']['relationships'][0]['from'] = 'file:unknown'
    with unittest.TestCase().assertRaisesRegex(ValueError, 'unknown relationship'):
        project(data)


def test_budget_rejection_is_nonmutating_and_recovers():
    data = fixture()
    original = copy.deepcopy(data)
    for budget in [0, True, 1]:
        with unittest.TestCase().assertRaisesRegex(ValueError, 'budget'):
            project(data, budget)
        assert data == original
    assert len(project(data, 2)['edges']) == 2
    data['functional_file_map'] = [{'path': name} for name in data['package_snapshot']['files']]
    del data['package_snapshot']
    with unittest.TestCase().assertRaisesRegex(ValueError, 'snapshot'):
        project(data)


def test_self_loops_and_non_file_meaning_are_not_collapsed():
    data = fixture()
    data['source_records'] = [{'id': 'rule', 'text': 'Retain conditions.'}]
    edge = data['semantic_model']['relationships'][0]
    edge['from'], edge['to'] = ['file:SKILL.md'] * 3, ['file:SKILL.md'] * 2
    other = {**edge, 'id': 'rule-edge', 'from': 'source:rule'}
    data['semantic_model']['relationships'].append(other)
    graph = project(data, 6)
    assert len(graph['edges']) == len({e['id'] for e in graph['edges']}) == 6
    assert graph['unprojected_records'] == ['rule-edge']
    assert graph['records'][1] == other and graph['projection_gaps'][0]['from'][0]['reason'] == 'non-file subject'
    assert graph['relationship_types'] == data['semantic_model']['relationship_types']


def test_mermaid_labels_escape_structure():
    data = fixture()
    name = 'quote"\\<br>\nfile.py'
    data['package_snapshot']['files'][name] = {'sha256': '4' * 64}
    graph = project(data)
    assert name not in graph['mermaid']
    assert '#34;' in graph['mermaid'] and '#92;' in graph['mermaid'] and '#10;' in graph['mermaid']


def test_native_action_returns_bound_graph_and_rejects_irrelevant_fields():
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        ledger, request = folder / 'ledger.json', folder / 'request.json'
        ledger.write_text(json.dumps(fixture()))
        payload = {'action': 'file-graph', 'ledger': str(ledger),
                   'ledger_sha256': hashlib.sha256(ledger.read_bytes()).hexdigest(), 'budget': 2}
        request.write_text(json.dumps(payload))
        command = ['node', str(ROOT / 'scripts/run_review_ledger.ts'), str(request)]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, result.stdout + result.stderr
        output = json.loads(result.stdout)['result']
        assert output['body']['text'].encode() == (ROOT / 'SKILL.md').read_bytes()
        assert json.loads(output['view_text'])['execution_acceptance'] == 'pending'
        request.write_text(json.dumps({**payload, 'selector': 'file:SKILL.md'}))
        rejected = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
        assert rejected.returncode == 1 and 'does not apply' in rejected.stdout + rejected.stderr


def load_tests(loader, tests, pattern):
    patterns = loader.testNamePatterns or ['*']
    functions = [(name, value) for name, value in globals().items() if name.startswith('test_') and callable(value)]
    return unittest.TestSuite(unittest.FunctionTestCase(value) for name, value in functions
                              if any(fnmatchcase(__name__ + '.' + name, pattern) for pattern in patterns))


if __name__ == '__main__':
    unittest.main()
