"""Lossless recorded file incidences; rendering and live inventory proof are separate."""
import json
from hashlib import sha256
from itertools import product

from review_ledger_context import require


def identity(prefix, value):
    return prefix + sha256(value.encode()).hexdigest()[:16]


def escaped(value):
    return ''.join(f'#{ord(c)};' if c in '\"<>%&#`|' or c == chr(92) or ord(c) < 32 else c for c in value)


def endpoints(edge, side, index):
    value = edge[side]
    declared = value if isinstance(value, list) else [value]
    result = []
    for ordinal, subject in enumerate(declared):
        members = index[subject]['members'] if subject == 'file-set:governed' else [subject]
        result.extend((ordinal, number, subject, member) for number, member in enumerate(members))
    return result


def file_owner(subject, index):
    if subject.startswith('file:'):
        return subject
    if subject.startswith('task:'):
        return 'file:' + index[subject]['file']
    return None


def mapped_ends(edge, side, index, nodes):
    mapped, omitted = [], []
    for ordinal, number, subject, member in endpoints(edge, side, index):
        owner = file_owner(member, index)
        incidence = {'subject': subject, 'member': member, 'ordinal': ordinal,
                     'member_ordinal': number, 'file': owner}
        if owner in nodes:
            mapped.append(incidence)
        else:
            omitted.append({**incidence, 'reason': 'non-file subject' if owner is None else 'file absent from recorded current snapshot'})
    return mapped, omitted


def incidence(record, left, right, multiple):
    key = [record['id'], left['ordinal'], left['member_ordinal'], right['ordinal'], right['member_ordinal']]
    return {'id': identity('e', json.dumps(key, separators=(',', ':'))),
            'from': left['file'], 'to': right['file'], 'record': record['id'],
            'from_endpoint': left, 'to_endpoint': right, 'multi_endpoint': multiple,
            'type': record['type'], 'review_state': record['review_state']}


def projection_plan(records, index, nodes, budget):
    plan, omitted, count = [], [], 0
    for record in records:
        left, missing_left = mapped_ends(record, 'from', index, nodes)
        right, missing_right = mapped_ends(record, 'to', index, nodes)
        count += len(left) * len(right)
        require(count <= budget, f'file graph needs more than {budget} incidences; increase the explicit budget')
        plan.append((record, left, right))
        if missing_left or missing_right:
            omitted.append({'record': record['id'], 'from': missing_left, 'to': missing_right})
    return plan, omitted


def emit(graph):
    nodes = graph['nodes']
    order = ['file:SKILL.md'] + [file for file in nodes if file != 'file:SKILL.md']
    lines = ['flowchart LR', 'accTitle: Recorded skill file graph',
             'accDescr: One file per node and one incidence per connector. Original records and projection gaps remain in the companion result.']
    lines += [f'{nodes[file]}["{escaped(file.removeprefix("file:"))}"]' for file in order]
    numbers = {row['id']: number + 1 for number, row in enumerate(graph['records'])}
    for edge in graph['edges']:
        text = escaped(f'{edge["type"]} R{numbers[edge["record"]]} {edge["review_state"]}')
        lines.append(f'{nodes[edge["from"]]} {edge["id"]}@-->|{text}| {nodes[edge["to"]]}')
    lines += ['classDef hub fill:#dcecff,stroke:#123d73,stroke-width:4px;',
              f'class {nodes["file:SKILL.md"]} hub;']
    return '\n'.join(lines) + '\n'


def file_graph(data, index, request):
    budget = request.get('budget')
    require(type(budget) is int and budget > 0, 'file-graph requires a positive incidence budget')
    snapshot = data.get('package_snapshot')
    require(isinstance(snapshot, dict) and isinstance(snapshot.get('files'), dict), 'file graph requires a recorded package snapshot')
    files = sorted('file:' + name for name in snapshot['files'])
    require('file:SKILL.md' in files, 'file graph requires a recorded SKILL.md')
    nodes = {file: identity('n', file) for file in files}
    records = sorted(data['semantic_model']['relationships'], key=lambda row: row['id'])
    plan, omitted = projection_plan(records, index, nodes, budget)
    edges = [incidence(record, left, right, len(before) * len(after) > 1)
             for record, before, after in plan for left, right in product(before, after)]
    require(len({*nodes.values(), *(edge['id'] for edge in edges)}) == len(nodes) + len(edges),
            'file graph has duplicate or colliding identities')
    used = {edge['record'] for edge in edges}
    graph = {'nodes': nodes, 'edges': edges, 'records': records, 'projection_gaps': omitted,
             'unprojected_records': [row['id'] for row in records if row['id'] not in used],
             'relationship_types': data['semantic_model']['relationship_types'],
             'package_snapshot': snapshot, 'ledger_sha256': request['ledger_sha256'],
             'scope': 'recorded current file incidences only', 'execution_acceptance': 'pending',
             'limit': 'No live inventory, render, readability, semantic or execution proof. Original records retain conditions, endpoint order, repetition and non-file meaning. Cartesian incidences do not determine conjunction or transitivity. Historical files remain in original records and explicit projection gaps; they are not current file nodes. Candidate, rejected and stale edges remain labeled and cannot establish an accepted path. The captured body is supplied separately by the native workflow.'}
    return {**graph, 'mermaid': emit(graph)}
