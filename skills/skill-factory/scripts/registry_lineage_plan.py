"""Calculate registry formatting and attribution without package or manifest writes."""
import base64
import json
import stat
from pathlib import Path

from agentic_request_contract import read_json
from registry_lineage_sources import (FACTORY_SOURCE, baseline_state, canonical_digest,
    classify_source_kind, retained_source_state, validate_names)
from review_ledger_context import require
from review_ledger_source import read_file
from review_ledger_write import target_path
from skill_package import inventory, sha
from standardization_format import format_contents, check_formatter
from standardization_plan import capture_files, directory_modes

LINEAGE = 'evals/source-lineage.json'


def file_record(path):
    raw = read_file({'path': str(path)})
    return {'sha256': sha(raw), 'mode': stat.S_IMODE(path.stat().st_mode),
            'content_base64': base64.b64encode(raw).decode('ascii')}


def archive_bytes(raw, skill, source):
    archive = read_json(raw.decode('utf-8'))
    require(archive.get('schema') == 'source-archive/v1' and archive.get('skill') == skill,
            'invalid source archive identity')
    matches = [item for item in archive['files'] if item['path'] == source]
    require(len(matches) == 1, 'source archive must have exactly one matching entry')
    item = matches[0]; value = base64.b64decode(item['base64'], validate=True)
    require(len(value) == item['bytes'] and sha(value) == item['sha256'], 'corrupt source archive entry')
    return value


def source_inputs(root, name, manifest):
    result = {}
    if manifest['source_kind'] == 'repository_baseline':
        return result
    for entry in manifest['files']:
        if entry['source_path'] == FACTORY_SOURCE:
            continue
        kind = entry['location_kind']
        require(kind in {'repository', 'archive', 'evidence'}, 'unsupported source location kind')
        owner = root if kind == 'repository' else root / 'evidence/ports' / name
        path = target_path(owner, entry['location_path'], True)
        record = file_record(path); result[str(path)] = record
        raw = base64.b64decode(record['content_base64'])
        value = archive_bytes(raw, name, entry['source_path']) if kind == 'archive' else raw
        if kind != 'repository':
            require(len(value) == entry['bytes'] and sha(value) == entry['sha256'], 'source evidence bytes differ')
    return result


def documents(root, name, files, manifest, lineage, inputs):
    public = sorted(path for path in files if path != LINEAGE)
    contents = {str(Path(path).relative_to(root)): base64.b64decode(item['content_base64'])
                for path, item in inputs.items()}
    contents.update({f'skills/{name}/{path}': raw for path, raw in files.items()})
    if manifest['source_kind'] == 'repository_baseline':
        entries, sources, mapping = baseline_state(root, name, public, contents)
        identity = canonical_digest(sources)
        lineage['native_manifest_sha256'] = identity
        manifest['native_manifest_sha256'] = identity
    else:
        entries, sources, mapping = retained_source_state(root, manifest, lineage, public, contents)
        manifest['source_kind'] = classify_source_kind(entries)
    require(entries, 'registry lineage needs actual source entries')
    lineage.update(source_files=sources, public_files=mapping)
    manifest.update(files=entries, evidence_packet_sha256=canonical_digest(sources))
    return {LINEAGE: (json.dumps(lineage, indent=2) + '\n').encode(),
            str(root / f'evidence/ports/{name}/source-manifest.json'): (json.dumps(manifest, indent=2) + '\n').encode()}


def change_records(root, name, files, before, manifest_record):
    result = []
    for path, raw in files.items():
        related = Path(path).is_absolute()
        previous = manifest_record if related else before[path]
        if previous['sha256'] == sha(raw):
            continue
        result.append({'skill': name, 'owner': 'repository' if related else 'skill',
            'path': Path(path).relative_to(root).as_posix() if related else path,
            'expected_sha256': previous['sha256'], 'mode': previous['mode'],
            'sha256': sha(raw), 'content_base64': base64.b64encode(raw).decode('ascii')})
    return sorted(result, key=maintenance_order)


def maintenance_order(item):
    return (3 if item['owner'] == 'repository' else 2 if item['path'] == LINEAGE else
            0 if item['path'] == 'SKILL.md' else 1, item['path'])


def plan_skill(root, name):
    skill = root / 'skills' / name
    target_path(root, f'skills/{name}/SKILL.md', True)
    before = capture_files(skill); directories = directory_modes(skill)
    manifest_path = target_path(root, f'evidence/ports/{name}/source-manifest.json')
    manifest_record = file_record(manifest_path)
    manifest = read_json(base64.b64decode(manifest_record['content_base64']).decode('utf-8'))
    require(manifest.get('schema') == 'source-evidence/v1' and manifest.get('skill') == name
            and manifest.get('source_kind') in {'repository_baseline', 'archived_source',
                'hybrid_archived_and_repository_baseline'}, 'invalid source manifest identity or kind')
    inputs = source_inputs(root, name, manifest); inputs[str(manifest_path)] = manifest_record
    files = {path: base64.b64decode(item['content_base64']) for path, item in before.items()}
    lineage = read_json(files.pop(LINEAGE).decode('utf-8'))
    public_format = format_contents(skill, {}, files)
    metadata = documents(root, name, files, manifest, lineage, inputs)
    metadata_format = format_contents(skill, {}, metadata)
    files.update(metadata)
    require(capture_files(skill) == before and directory_modes(skill) == directories
            and all(file_record(Path(path)) == item for path, item in inputs.items()),
            'registry inputs changed during planning')
    return {'name': name, 'root': str(skill), 'before': before, 'directories': directories,
            'inputs': inputs, 'formatters': [public_format, metadata_format],
            'changes': change_records(root, name, files, before, manifest_record)}


def current_inputs(plan, selected=None, installed=False):
    target, new = None, None
    if selected is not None:
        owner = Path(plan['root']) if selected['owner'] == 'repository' else Path(plan['root']) / 'skills' / selected['skill']
        target = owner / selected['path']
        new = {key: selected[key] for key in ['sha256', 'mode', 'content_base64']}
    runtime = Path(plan['runtime_root']); runtime_files = dict(plan['runtime_files'])
    if installed and target.is_relative_to(runtime):
        runtime_files[target.relative_to(runtime).as_posix()] = selected['sha256']
    require(inventory(runtime) == runtime_files, 'registry runtime changed since planning')
    for skill in plan['skills']:
        root = Path(skill['root']); expected = dict(skill['before'])
        if installed and target.is_relative_to(root):
            expected[target.relative_to(root).as_posix()] = new
        require(capture_files(root) == expected and directory_modes(root) == skill['directories'],
                'registry skill bytes, modes or directories changed')
        for path, item in skill['inputs'].items():
            wanted = new if installed and Path(path) == target else item
            require(file_record(Path(path)) == wanted, 'registry source or manifest changed')
        for formatter in skill['formatters']:
            check_formatter(formatter, {str(target): new} if installed else None)
    return True



def build_plan(root, names):
    root = Path(root)
    require(root.is_absolute() and root.resolve() == root and root.is_dir(), 'registry root must be canonical')
    validate_names(root, names)
    require(len(set(names)) == len(names), 'duplicate registry skill name')
    runtime = Path(__file__).resolve().parents[1]; runtime_files = inventory(runtime)
    skills = [plan_skill(root, name) for name in names]
    require(inventory(runtime) == runtime_files, 'registry runtime changed during planning')
    plan = {'version': 1, 'root': str(root), 'skills': skills,
            'runtime_root': str(runtime), 'runtime_files': runtime_files,
            'changes': sorted([item for skill in skills for item in skill['changes']], key=maintenance_order), 'execution_acceptance': 'pending',
            'limit': 'Current calculated bytes with body before source changes, then lineage and repository manifest. '
                     'This known maintenance order is not complete semantic dependency acceptance. Each reviewed call '
                     'applies at most the next file; replan after each effect. Complete source, domain and recipient '
                     'validation remains required after no changes remain. Formatter limitations are retained per record.'}

    current_inputs(plan)
    return plan
