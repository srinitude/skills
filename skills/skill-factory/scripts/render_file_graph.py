"""Render a bound native file-graph result and check exact SVG topology."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

from review_ledger_context import require
from review_ledger_file_graph import emit, identity, projection_payload

ROOT = Path(__file__).resolve().parents[1]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_graph(path, expected):
    raw = path.read_bytes()
    require(digest(raw) == expected, 'native result digest mismatch')
    result = json.loads(raw)
    require(isinstance(result, dict) and result.get('status') == 'success', 'native file-graph result did not succeed')
    graph = json.loads(result['result']['view_text'])
    nodes = graph['nodes']
    expected_nodes = {'file:' + name: identity('n', 'file:' + name)
                      for name in sorted(graph['package_snapshot']['files'])}
    require(nodes == expected_nodes and 'file:SKILL.md' in nodes, 'file node identity mismatch')
    records = {record['id']: record for record in graph['records']}
    require(len(records) == len(graph['records']), 'duplicate relationship record')
    require(isinstance(graph.get('projection_index'), dict), 'missing projection index; recapture the native file graph')
    try:
        projected = projection_payload(graph['records'], graph['projection_index'], nodes,
                                       max(1, len(graph['edges'])))
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError('graph projection or relationship mismatch') from error
    require(all(graph.get(key) == value for key, value in projected.items()),
            'graph projection or relationship mismatch')
    ids = [*nodes.values(), *(edge['id'] for edge in graph['edges'])]
    require(len(ids) == len(set(ids)), 'duplicate graph identity')
    require(graph['mermaid'] == emit(graph), 'Mermaid projection mismatch')
    return raw, graph


def render_config(graph):
    return {'deterministicIds': True, 'deterministicIDSeed': 'skill-file-map-v1',
            'securityLevel': 'strict', 'layout': 'elk', 'flowchart': {'htmlLabels': False},
            'elk': {'considerModelOrder': 'NONE', 'forceNodeModelOrder': False,
                    'mergeEdges': False, 'nodePlacementStrategy': 'BRANDES_KOEPF',
                    'cycleBreakingStrategy': 'GREEDY'},
            'maxEdges': len(graph['edges']) + 1,
            'maxTextSize': len(graph['mermaid'].encode()) + 1}


def svg_topology(raw, graph):
    require(b'<!DOCTYPE' not in raw and b'<!ENTITY' not in raw, 'unexpected XML declaration')
    svg = ET.fromstring(raw)
    require(svg.tag == '{http://www.w3.org/2000/svg}svg', 'renderer did not produce SVG')
    box = [float(value) for value in svg.attrib.get('viewBox', '').split()]
    require(len(box) == 4 and all(math.isfinite(v) for v in box)
            and min(box[2:]) > 0, 'invalid SVG viewBox')
    nodes, edges = [], []
    for element in svg.iter():
        classes = element.attrib.get('class', '').split()
        if 'node' in classes:
            match = re.fullmatch(r'my-svg-flowchart-(n[0-9a-f]{16})-\d+', element.get('id', ''))
            require(match is not None, 'unexpected SVG node identity')
            nodes.append(match[1])
        if 'flowchart-link' in classes:
            edges.append(element.get('data-id'))
            require(element.get('d', '').strip() and not re.search(r'NaN|Infinity', element.get('d', '')),
                    'invalid SVG connector path')
    require(len(nodes) == len(set(nodes)) == len(graph['nodes'])
            and set(nodes) == set(graph['nodes'].values()), 'rendered node omission or duplication')
    expected_edges = {edge['id'] for edge in graph['edges']}
    require(len(edges) == len(set(edges)) == len(expected_edges)
            and set(edges) == expected_edges, 'rendered connector omission or duplication')
    return {'nodes': len(nodes), 'connectors': len(edges), 'viewBox': box}


def renderer_version():
    package = ROOT / 'node_modules/@mermaid-js/mermaid-cli'
    version = json.loads((package / 'package.json').read_text())['version']
    declared = json.loads((ROOT / 'package.json').read_text())['devDependencies']['@mermaid-js/mermaid-cli']
    require(version == declared, 'installed mmdc does not match the exact declared version')
    return package / 'src/cli.js', version


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def render(source, expected, output, timeout):
    require(math.isfinite(timeout) and timeout > 0, 'timeout must be positive and finite')
    require(not output.resolve().is_relative_to(ROOT.resolve()), 'render outside the skill; promote owned artifacts through reviewed file writes')
    raw, graph = read_graph(source, expected)
    cli, version = renderer_version()
    output.mkdir(parents=False, exist_ok=False)
    (output / 'native-result.json').write_bytes(raw)
    (output / 'graph.mmd').write_text(graph['mermaid'], encoding='utf-8')
    write_json(output / 'mermaid.json', render_config(graph))
    write_json(output / 'puppeteer.json', {'protocolTimeout': math.ceil(timeout * 1000)})
    command = ['node', str(cli), '-i', str(output / 'graph.mmd'), '-o', str(output / 'graph.svg'),
               '-c', str(output / 'mermaid.json'), '-p', str(output / 'puppeteer.json')]
    completed = subprocess.run(command, capture_output=True, timeout=timeout, check=False)
    (output / 'renderer.stdout').write_bytes(completed.stdout)
    (output / 'renderer.stderr').write_bytes(completed.stderr)
    require(completed.returncode == 0, 'mmdc failed; inspect retained renderer output')
    svg = (output / 'graph.svg').read_bytes()
    proof = {'topology': svg_topology(svg, graph), 'native_result_sha256': expected,
             'svg_sha256': digest(svg), 'mmdc_version': version,
             'package_lock_sha256': digest((ROOT / 'package-lock.json').read_bytes()),
             'configuration_sha256': digest((output / 'mermaid.json').read_bytes()),
             'limit': 'Exact recorded topology only. Live inventory, readability, relationship meaning and execution acceptance require separate review.'}
    write_json(output / 'render-proof.json', proof)
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('native_result', type=Path)
    parser.add_argument('output', type=Path, help='new output directory; its parent must exist')
    parser.add_argument('--sha256', required=True, help='expected native result SHA-256')
    parser.add_argument('--timeout', required=True, type=float, help='positive wall-clock seconds')
    args = parser.parse_args()
    try:
        proof = render(args.native_result.resolve(), args.sha256, args.output.resolve(), args.timeout)
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired, ET.ParseError) as error:
        parser.exit(1, str(error) + '\n')
    print(json.dumps(proof, sort_keys=True))


if __name__ == '__main__':
    main()
