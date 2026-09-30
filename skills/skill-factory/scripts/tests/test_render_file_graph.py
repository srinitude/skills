"""Bound graph, omitted topology, failure recovery and real mmdc checks."""
import copy
from fnmatch import fnmatchcase
import json
from pathlib import Path
import tempfile
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))

import render_file_graph as renderer
from test_review_ledger_file_graph import fixture, project


def source(folder, graph):
    path = folder / 'native.json'
    path.write_text(json.dumps({'status': 'success', 'result': {'view_text': json.dumps(graph)}}))
    return path, renderer.digest(path.read_bytes())


def svg_fixture(graph):
    svg = ET.Element('{http://www.w3.org/2000/svg}svg', viewBox='0 0 100 100')
    for number, node in enumerate(graph['nodes'].values()):
        ET.SubElement(svg, 'g', {'class': 'node default', 'id': f'my-svg-flowchart-{node}-{number}'})
    for edge in graph['edges']:
        ET.SubElement(svg, 'path', {'class': 'flowchart-link', 'data-id': edge['id'], 'd': 'M0 0L1 1'})
    return svg


def test_bound_input_and_nonmutating_rejection():
    graph = project(fixture())
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        path, sha = source(folder, graph)
        original = path.read_bytes()
        assert renderer.read_graph(path, sha)[1] == graph
        with unittest.TestCase().assertRaisesRegex(ValueError, 'digest'):
            renderer.read_graph(path, '0' * 64)
        assert path.read_bytes() == original
        graph['edges'][0]['type'] = 'invented'
        path, sha = source(folder, graph)
        with unittest.TestCase().assertRaisesRegex(ValueError, 'relationship mismatch'):
            renderer.read_graph(path, sha)


def test_mermaid_and_node_tampering_reject():
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        for field in ['nodes', 'mermaid']:
            graph = project(fixture())
            graph[field] = {} if field == 'nodes' else 'flowchart LR\na-->b\n'
            path, sha = source(folder, graph)
            unittest.TestCase().assertRaises(ValueError, renderer.read_graph, path, sha)


def test_omitted_duplicate_and_invalid_render_elements():
    graph = project(fixture())
    svg = svg_fixture(graph)
    assert renderer.svg_topology(ET.tostring(svg), graph)['connectors'] == 2
    for index in [0, len(svg) - 1]:
        broken = copy.deepcopy(svg)
        broken.remove(broken[index])
        with unittest.TestCase().assertRaisesRegex(ValueError, 'omission'):
            renderer.svg_topology(ET.tostring(broken), graph)
        broken = copy.deepcopy(svg)
        broken.append(copy.deepcopy(broken[index]))
        with unittest.TestCase().assertRaisesRegex(ValueError, 'duplication'):
            renderer.svg_topology(ET.tostring(broken), graph)
    svg[-1].set('d', 'MNaN 0')
    with unittest.TestCase().assertRaisesRegex(ValueError, 'path'):
        renderer.svg_topology(ET.tostring(svg), graph)


def test_invalid_viewbox_and_xml_reject():
    graph = project(fixture())
    for box in ['0 0 0 1', '0 0 nan 1', '0 0 inf 1', '0 0 1']:
        svg = svg_fixture(graph)
        svg.set('viewBox', box)
        with unittest.TestCase().assertRaises(ValueError):
            renderer.svg_topology(ET.tostring(svg), graph)
    with unittest.TestCase().assertRaisesRegex(ValueError, 'XML'):
        renderer.svg_topology(b'<!DOCTYPE svg><svg/>', graph)


def test_output_collision_and_timeout_reject_before_effects():
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        path, sha = source(folder, project(fixture()))
        unittest.TestCase().assertRaisesRegex(ValueError, 'outside the skill', renderer.render, path, sha, renderer.ROOT / 'forbidden-artifact', 60)
        for timeout in [0, -1, float('inf'), float('nan')]:
            unittest.TestCase().assertRaisesRegex(ValueError, 'timeout', renderer.render, path, sha, folder / 'new', timeout)
            assert not (folder / 'new').exists()
        unittest.TestCase().assertRaises(FileExistsError, renderer.render, path, sha, folder, 60)
        assert set(p.name for p in folder.iterdir()) == {'native.json'}


def test_real_renderer_reproduces_parallel_edges_and_self_loops():
    data = fixture()
    data['semantic_model']['relationships'][0]['from'] = ['file:SKILL.md'] * 2
    graph = project(data)
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        path, sha = source(folder, graph)
        first = renderer.render(path, sha, folder / 'first', 60)
        second = renderer.render(path, sha, folder / 'second', 60)
        assert first == second and first['topology']['connectors'] == 2
        assert (folder / 'first/graph.svg').read_bytes() == (folder / 'second/graph.svg').read_bytes()
        assert (folder / 'first/native-result.json').read_bytes() == path.read_bytes()


def test_projection_omission_and_wrong_multiplicity_reject():
    graphs = [project(fixture()) for _ in range(3)]
    graphs[0]['edges'].pop()
    graphs[1]['edges'][0]['multi_endpoint'] = False
    graphs[2]['unprojected_records'] = ['one']
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        for graph in graphs:
            graph['mermaid'] = renderer.emit(graph)
            path, sha = source(folder, graph)
            unittest.TestCase().assertRaisesRegex(ValueError, 'projection', renderer.read_graph, path, sha)


def test_nonobject_native_result_rejects_cleanly_then_valid_input_recovers():
    from cli import run
    graph = project(fixture())
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        path = folder / 'native.json'
        for raw in [b'[]', b'null', b'false', b'0', b'"text"']:
            path.write_bytes(raw)
            result = run('render_file_graph.py', path, folder / 'output',
                         '--sha256', renderer.digest(raw), '--timeout', '60')
            assert result.returncode == 1, result.stdout + result.stderr
            assert 'native file-graph result did not succeed' in result.stderr
            assert 'Traceback' not in result.stderr
            assert path.read_bytes() == raw and not (folder / 'output').exists()
        path, sha = source(folder, graph)
        assert renderer.read_graph(path, sha)[1] == graph


def test_renderer_failure_keeps_its_reason_after_output_cleanup():
    from unittest.mock import patch
    with tempfile.TemporaryDirectory() as temporary:
        folder = Path(temporary)
        path, sha = source(folder, project(fixture()))
        failed = renderer.subprocess.CompletedProcess([], 7, b'output', b'renderer failure detail')
        with patch.object(renderer.subprocess, 'run', return_value=failed), unittest.TestCase().assertRaises(ValueError) as caught:
            renderer.render(path, sha, folder / 'failed', 60)
        message = str(caught.exception)
        assert (folder / 'failed/renderer.stderr').read_bytes() == failed.stderr
        assert (folder / 'failed/renderer.stdout').read_bytes() == failed.stdout
        assert not (folder / 'failed/render-proof.json').exists()
    assert '7' in message and 'renderer failure detail' in message, message


def load_tests(loader, tests, pattern):
    patterns = loader.testNamePatterns or ['*']
    functions = [(name, value) for name, value in globals().items() if name.startswith('test_') and callable(value)]
    return unittest.TestSuite(unittest.FunctionTestCase(value) for name, value in functions
                              if any(fnmatchcase(__name__ + '.' + name, pattern) for pattern in patterns))


if __name__ == '__main__':
    unittest.main()
