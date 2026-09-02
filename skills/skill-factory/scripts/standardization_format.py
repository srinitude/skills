"""Apply an owning repository's local formatter when it is available."""
import shutil
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
