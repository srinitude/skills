"""Prepare exact future variant bytes before any staging or lineage write."""
import base64
import json
from pathlib import Path

from review_ledger_context import require
from review_ledger_source import read_file
from scaffold_plan import ordered
from standardization_plan import capture_files, directory_modes
from skill_package import inventory, real_path, sha, tree_digest


def bound_inputs(paths):
    bindings = []
    for path in paths:
        path = Path(path).absolute()
        raw = read_file({'path': str(path)})
        bindings.append({'path': str(path), 'sha256': sha(raw),
                         'content_base64': base64.b64encode(raw).decode('ascii')})
    return bindings


def check_bindings(bindings):
    for binding in bindings:
        require(read_file(binding) == base64.b64decode(binding['content_base64']),
                'variant operation input changed')


def package_state(root):
    root = real_path(root)
    return {'files': capture_files(root), 'directories': directory_modes(root)}


def publication_plan(plan, candidate, factory, input_paths, lineage):
    target = Path(plan['target']['path'])
    source = Path(plan['source']['root'])
    bindings = bound_inputs(input_paths)
    before = package_state(candidate)
    source_before = package_state(source)
    target_before = package_state(target) if target.exists() else None
    factory_files = inventory(factory)
    body = read_file({'path': str(factory / 'SKILL.md')})
    require(body.decode('utf-8').strip(), 'factory body must be nonempty')
    content = {name: item['sha256'] for name, item in before['files'].items()
               if name != 'evals/source-lineage.json'}
    require(lineage['derivation']['target_baseline'] == content, 'future lineage target is stale')
    require(lineage['derivation']['candidate_digest'] == tree_digest(
        {name: item['sha256'] for name, item in before['files'].items()}), 'future lineage candidate is stale')
    files = future_files(before['files'], lineage)
    require(package_state(candidate) == before and package_state(source) == source_before,
            'variant source or candidate changed while planning publication')
    require((package_state(target) if target.exists() else None) == target_before,
            'variant target changed while planning publication')
    require(inventory(factory) == factory_files, 'factory changed while planning publication')
    check_bindings(bindings)
    return {'version': 1, 'scope_plan_sha256': tree_digest(plan), 'inputs': bindings,
            'candidate': str(candidate), 'candidate_before': before, 'source_before': source_before,
            'target': str(target), 'target_before': target_before, 'files': files,
            'factory_files': factory_files, 'factory_body': {'sha256': sha(body), 'text': body.decode('utf-8')},
            'execution_acceptance': 'pending',
            'limit': 'Calculated future bytes and current identities only. Initial/per-file source review, '
                     'guarded staging, real variant behavior, promotion and recovery remain required.'}


def future_files(before, lineage):
    files = {name: dict(value) for name, value in before.items()}
    raw = (json.dumps(lineage, indent=2) + '\n').encode('utf-8')
    files['evals/source-lineage.json'] = {'mode': before.get('evals/source-lineage.json', {}).get('mode', 0o644),
        'sha256': sha(raw), 'content_base64': base64.b64encode(raw).decode('ascii')}
    return ordered([{'path': name, **item} for name, item in files.items()])
