"""Apply an owning repository's local formatter when it is available."""
import json
import os
import shutil
from skill_package import inventory, sha
from pathlib import Path
import subprocess


CONFIG_NAMES = (
    ".prettierrc", ".prettierrc.json", ".prettierrc.yml", ".prettierrc.yaml",
    ".prettierrc.json5", ".prettierrc.js", "prettier.config.js", ".prettierrc.ts",
    "prettier.config.ts", ".prettierrc.mjs", "prettier.config.mjs", ".prettierrc.mts",
    "prettier.config.mts", ".prettierrc.cjs", "prettier.config.cjs", ".prettierrc.cts",
    "prettier.config.cts", ".prettierrc.toml",
)


def package_configuration(folder, command, repo):
    package = folder / 'package.json'; yaml = folder / 'package.yaml'
    if not package.is_file() and not yaml.is_file():
        return False
    if command is None:
        if yaml.is_file():
            return True  # Native resolution is required to distinguish YAML ownership when runtime is missing.
        value = json.loads(package.read_text()).get('prettier')
        return value is not None and value is not False and value != '' and value != 0
    result = subprocess.run([*readonly_command(command), '--find-config-path',
                             str(folder / '.skill-factory-configuration-probe.json')],
                            cwd=repo, capture_output=True, text=True)
    if result.returncode == 1:
        return False
    if result.returncode:
        raise ValueError('repository formatter configuration lookup failed: ' + result.stderr.strip())
    resolved = (repo / result.stdout.strip()).resolve()
    return bool(result.stdout.strip()) and resolved.is_relative_to(repo)


def formatter_command(root, paths=()):
    target = root.resolve(); node = shutil.which("node")
    folders = {target, *target.parents, *(parent for path in paths for parent in path.parents)}
    for repo in (target, *target.parents):
        if not (repo / ".git").exists():
            continue
        script = repo / "node_modules/prettier/bin/prettier.cjs"
        command = [node, str(script)] if node and script.is_file() else None
        owned = sorted(folder for folder in folders if folder.is_relative_to(repo))
        configured = any((folder / name).is_file() for folder in owned for name in CONFIG_NAMES)
        configured = configured or any(package_configuration(folder, command, repo) for folder in owned)
        if configured and command is None:
            raise ValueError("configured repository formatter is not ready; selected Node and local Prettier are required")
        if configured:
            return command, repo
    return None


def readonly_command(command):
    if os.environ.get('NODE_OPTIONS'):
        raise ValueError('reviewed formatting requires NODE_OPTIONS to be unset; injected runtime behavior is not bound')
    return [command[0], '--permission', '--allow-fs-read=*', *command[1:]]


def format_input(command, repo, path, raw):
    command = readonly_command(command)
    info = subprocess.run([*command, '--file-info', str(path)], cwd=repo,
                          check=False, capture_output=True, text=True)
    if info.returncode:
        raise ValueError('repository formatter file-info failed: ' + info.stderr.strip())
    try:
        data = json.loads(info.stdout)
        if data['ignored'] or data['inferredParser'] is None:
            return raw, {'path': str(path), 'file_info': data, 'formatted': False}
    except (ValueError, KeyError, TypeError) as error:
        raise ValueError('repository formatter returned invalid file-info') from error
    result = subprocess.run([*command, '--stdin-filepath', str(path)], cwd=repo,
                            input=raw, check=False, capture_output=True)
    if result.returncode:
        raise ValueError('repository formatter failed: ' + result.stderr.decode('utf-8', errors='replace'))
    return result.stdout, {'path': str(path), 'file_info': data, 'formatted': True,
                           'input_sha256': sha(raw), 'output_sha256': sha(result.stdout)}


def format_contents(root, original, files):
    changed = [name for name, raw in files.items() if original.get(name) != raw]
    if not changed:
        return None
    paths = [root / name for name in changed]
    owner = formatter_command(root, paths)
    if owner is None:
        return None
    command, repo = owner
    captured = formatter_snapshot(root, command, repo, paths)
    records = []
    for name in changed:
        files[name], record = format_input(command, repo, root / name, files[name])
        records.append(record)
    if formatter_snapshot(root, command, repo, paths) != captured:
        raise ValueError('formatter inputs changed during planning')
    return {'command': command, 'execution_command': readonly_command(command), 'cwd': str(repo), 'root': str(root), 'inputs': captured, 'files': records,
            'limit': 'Actual file-info and stdin output under the current configured owner. '
                     'Ignored or unsupported files keep their bytes. Configuration candidates, the selected Node binary and '
                     'Prettier package are bound. Dynamic config/plugin transitive imports and external effects need '
                     'their own reviewed dependency evidence. Selected Node permissions reject incidental filesystem writes and '
                     'ungranted operations in the tested trusted-code execution; read access remains unrestricted. '
                     'Unsupported runtimes fail without a fallback. This is not hostile-code isolation or semantic validation.'}


def formatter_snapshot(root, command, repo, paths=()):
    names = set(CONFIG_NAMES) | {'.editorconfig', '.prettierignore', '.gitignore', 'package.json', 'package.yaml'}
    folders = {root, *root.parents, *(parent for path in paths for parent in path.parents)}
    configs = {str(folder / name): sha((folder / name).read_bytes()) if (folder / name).is_file() else None
               for folder in sorted(folders) for name in sorted(names)}
    package = Path(command[1]).parents[1].resolve()
    return {'node': {'path': command[0], 'sha256': sha(Path(command[0]).read_bytes())},
            'prettier': {'path': str(package), 'files': inventory(package)}, 'configuration': configs}


def check_formatter(record, files=None):
    if record is None:
        return
    expected = {**record['inputs'], 'configuration': dict(record['inputs']['configuration'])}
    for name, item in (files or {}).items():
        path = str(Path(record['root']) / name)
        if path in expected['configuration']:
            expected['configuration'][path] = item['sha256']
    paths = [Path(item['path']) for item in record['files']]
    if formatter_snapshot(Path(record['root']), record['command'], Path(record['cwd']), paths) != expected:
        raise ValueError('formatter inputs changed since the reviewed plan')
