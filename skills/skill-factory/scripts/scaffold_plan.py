"""Render complete scaffold bytes without creating a candidate package."""
import ast
import base64
import json
from graphlib import TopologicalSorter
from pathlib import Path

from review_ledger_context import require
from review_ledger_source import read_file
from skill_package import inventory, sha


def plan_digest(plan):
    return sha(json.dumps(plan, sort_keys=True, separators=(',', ':')).encode())


def phase(path):
    if path == 'mise.toml':
        return 0
    if path in {'package.json', 'package-lock.json', 'tsconfig.json', '.github/workflows/ci.yml'}:
        return 1
    if path == 'scripts/tests/test_ci_contract.py':
        return 2
    if path.startswith('scripts/tests/'):
        return 3
    if path.startswith('scripts/'):
        return 4
    return 6 if path.startswith('evals/') else 5


def local_imports(item, modules):
    if not item['path'].endswith('.py'):
        return []
    tree = ast.parse(base64.b64decode(item['content_base64']))
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return sorted({modules[name] for name in names if name in modules and modules[name] != item['path']})


def ordered(files):
    modules = {Path(item['path']).stem: item['path'] for item in files if item['path'].endswith('.py')}
    records = {item['path']: {**item, 'construction_phase': phase(item['path']),
                             'observed_python_imports': local_imports(item, modules)} for item in files}
    require(len(records) == len(files), 'duplicate scaffold destination')
    result = []
    for stage in range(7):
        group = {name: item for name, item in records.items() if item['construction_phase'] == stage}
        if 'SKILL.md' in group:
            group = {'SKILL.md': group['SKILL.md'], **group}
        graph = {name: [provider for provider in item['observed_python_imports'] if provider in group]
                 for name, item in group.items()}
        result.extend(records[name] for name in TopologicalSorter(graph).static_order())
    return result


def render_plan(root, tokens, sources):
    body = read_file({"path": str(root / "SKILL.md")})
    require(body.decode("utf-8").strip(), "factory body must be nonempty regular UTF-8")
    baseline = inventory(root)
    files = []
    for destination, source, rendered in sources:
        path = root / source
        require(path.is_file() and not path.is_symlink(), 'scaffold source must be a regular file')
        original = path.read_bytes()
        raw = original
        if rendered:
            text = original.decode('utf-8')
            for key, value in tokens.items():
                text = text.replace('{{%s}}' % key, value)
            raw = text.encode('utf-8')
        files.append({'path': destination, 'source': {'path': source, 'sha256': sha(original)},
                      'sha256': sha(raw), 'content_base64': base64.b64encode(raw).decode('ascii')})
    require(inventory(root) == baseline, 'factory changed while rendering scaffold plan')
    return {'version': 1, 'tokens': tokens, 'factory_files': baseline,
            'factory_body': {'sha256': sha(body), 'text': body.decode('utf-8')},
            'files': ordered(files), 'execution_acceptance': 'pending',
            'limit': 'Complete rendered/copy bytes and fixed construction phases. Python imports are syntax '
                     'observations, including conditional imports, not complete semantic dependencies. '
                     'Construction order differs from runtime and required reading order. Initial body '
                     'and per-file semantic review remain with the caller; seeds are not accepted skills.'}
