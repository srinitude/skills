"""Capture exact standardization inputs and calculate a package without writing it."""
import base64
import datetime
import stat
import subprocess
from pathlib import Path

from review_ledger_source import read_file
from scaffold_plan import phase
from standardization_assets import resolved_initial_profile
from standardization_baseline import tracked_paths
from standardization_render import render
from standardization_format import format_contents
from skill_package import inventory, owned_entries, owned_paths, sha
from standardization_profile import selected_profile
from agentic_request_contract import read_json


def capture_files(root):
    result = {}
    for path in owned_paths(root):
        raw = path.read_bytes()
        result[path.relative_to(root).as_posix()] = {
            'sha256': sha(raw), 'mode': stat.S_IMODE(path.stat().st_mode),
            'content_base64': base64.b64encode(raw).decode('ascii')}
    return result


def rebase_files(root, files):
    repo, paths = tracked_paths(root)
    bindings = []
    for destination, git_path in paths:
        raw = subprocess.run(['git', '-C', str(repo), 'show', 'HEAD:' + git_path],
                             check=True, capture_output=True).stdout
        name = destination.relative_to(root).as_posix()
        files[name] = raw
        bindings.append({'path': name, 'git_path': git_path, 'sha256': sha(raw),
                         'content_base64': base64.b64encode(raw).decode('ascii')})
    return {'repository': str(repo), 'commit': subprocess.check_output(
        ['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip(), 'files': bindings}


def directory_modes(root):
    root = root.resolve()
    return {path.relative_to(root).as_posix(): stat.S_IMODE(path.stat().st_mode)
            for path in [root, *(p for p in owned_entries(root) if p.is_dir())]}


def profile_input(path, profile, root):
    path = Path(path).absolute()
    raw = read_file({'path': str(path)})
    if selected_profile(read_json(raw.decode('utf-8')), root.name) != profile:
        raise ValueError('profile changed while loading')
    return {'path': str(path), 'sha256': sha(raw), 'content_base64': base64.b64encode(raw).decode('ascii')}


def planned_records(files, before):
    records = [{'path': name, 'sha256': sha(raw), 'content_base64': base64.b64encode(raw).decode('ascii'),
                'mode': before.get(name, {}).get('mode', 0o644), 'construction_phase': phase(name)}
               for name, raw in files.items()]
    records.sort(key=lambda item: (item['construction_phase'], item['path'] != 'SKILL.md', item['path']))
    return records


def build_plan(root, profile, scope, rebase, factory, sources, profile_path, stamp=None):
    root = root.resolve()
    profile_binding = profile_input(profile_path, profile, root)
    directories = directory_modes(root)
    body = read_file({'path': str(factory / 'SKILL.md')})
    if not body.decode('utf-8').strip():
        raise ValueError('factory body must be nonempty')
    factory_files = inventory(factory)
    before = capture_files(root)
    profile = resolved_initial_profile(root, profile)
    original = {name: base64.b64decode(item['content_base64']) for name, item in before.items()}
    tracked = rebase_files(root, original) if rebase else None
    stamp = stamp or datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    files = render(root, original, profile, scope, factory, sources, stamp)
    formatting = format_contents(root, original, files)
    records = planned_records(files, before)
    if (capture_files(root) != before or inventory(factory) != factory_files
            or directory_modes(root) != directories
            or sha(read_file(profile_binding)) != profile_binding['sha256']):
        raise ValueError('standardization input changed while planning')
    return {'version': 1, 'captured_at': stamp, 'target': str(root), 'scope': scope,
            'profile': profile, 'profile_input': profile_binding, 'tracked_text': tracked,
            'before': before, 'directory_modes': directories, 'formatter': formatting,
            'factory_files': factory_files, 'factory_body': {'sha256': sha(body), 'text': body.decode('utf-8')},
            'files': records, 'execution_acceptance': 'pending',
            'limit': 'Exact captured source and calculated package bytes. Fixed construction phases are not '
                     'complete reading/runtime dependencies. Protected application, '
                     'mapping/policy checks, source/semantic review and whole-goal acceptance remain required.'}
