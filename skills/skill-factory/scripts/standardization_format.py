"""Apply an owning repository's local formatter when it is available."""
import json
import shutil
from skill_package import inventory, sha
from pathlib import Path
import subprocess


CONFIG_NAMES = (
    ".prettierrc",
    ".prettierrc.json",
    ".prettierrc.yaml",
    ".prettierrc.yml",
    "prettier.config.js",
    "prettier.config.mjs",
)


def formatter_command(root):
    target = root.resolve()
    node = shutil.which("node")
    if not node:
        return None
    for repo in target.parents:
        script = repo / "node_modules/prettier/bin/prettier.cjs"
        configured = any((repo / name).is_file() for name in CONFIG_NAMES)
        if (repo / ".git").exists() and configured and script.is_file():
            return [node, str(script), "--write", str(target)], repo
    return None


def format_target(root):
    owner = formatter_command(root)
    if owner is None:
        return
    command, repo = owner
    run_formatter(command, repo)


def format_files(root, paths):
    paths = tuple(paths)
    if not paths:
        return
    owner = formatter_command(root)
    if owner is None:
        return
    command, repo = owner
    command = [*command[:-1], *(str(path.resolve()) for path in paths)]
    run_formatter(command, repo)


def run_formatter(command, repo):
    result = subprocess.run(command, cwd=repo, check=False,
                            capture_output=True, text=True)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ValueError(f"repository formatter failed: {detail}")


def format_input(command, repo, path, raw):
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
    owner = formatter_command(root)
    changed = [name for name, raw in files.items() if original.get(name) != raw]
    if owner is None or not changed:
        return None
    command, repo = owner
    command = command[:2]
    captured = formatter_snapshot(root, command, repo)
    records = []
    for name in changed:
        files[name], record = format_input(command, repo, root / name, files[name])
        records.append(record)
    if formatter_snapshot(root, command, repo) != captured:
        raise ValueError('formatter inputs changed during planning')
    return {'command': command, 'cwd': str(repo), 'root': str(root), 'inputs': captured, 'files': records,
            'limit': 'Actual file-info and stdin output under the current configured owner. '
                     'Ignored or unsupported files keep their bytes. Configuration candidates, the selected Node binary and '
                     'Prettier package are bound. Dynamic config/plugin transitive imports and external effects need '
                     'their own reviewed dependency evidence. This is not sandboxing or semantic validation.'}


def formatter_snapshot(root, command, repo):
    names = set(CONFIG_NAMES) | {'.prettierrc.js', '.prettierrc.cjs', '.prettierrc.mjs', '.prettierrc.json5',
            '.prettierrc.toml', '.prettierrc.ts', '.prettierrc.cts', '.prettierrc.mts', 'prettier.config.cjs',
            'prettier.config.ts', 'prettier.config.cts', 'prettier.config.mts', '.editorconfig',
            '.prettierignore', '.gitignore', 'package.json', 'package.yaml'}
    configs = {str(folder / name): sha((folder / name).read_bytes()) if (folder / name).is_file() else None
               for folder in [root, *root.parents] for name in sorted(names)}
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
    if formatter_snapshot(Path(record['root']), record['command'], Path(record['cwd'])) != expected:
        raise ValueError('formatter inputs changed since the reviewed plan')
