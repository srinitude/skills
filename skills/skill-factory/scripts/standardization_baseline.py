"""Restore a target's tracked Markdown baseline before a corrected transform."""
import subprocess
from pathlib import Path


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, text=True).stdout


def tracked_paths(root):
    repo = Path(git(root, "rev-parse", "--show-toplevel").strip()).resolve()
    target = root.resolve()
    if not target.is_relative_to(repo):
        raise ValueError("target is outside the Git repository")
    relative = target.relative_to(repo)
    names = git(repo, "ls-tree", "-r", "--name-only", "HEAD", "--", str(relative))
    allowed = []
    for name in names.splitlines():
        path = Path(name)
        if path.suffix == ".md" or path.as_posix().endswith("evals/source-mapping.json"):
            allowed.append((repo / path, path.as_posix()))
    return repo, allowed


def restore_tracked_text(root):
    repo, paths = tracked_paths(root)
    restored = []
    for destination, git_path in paths:
        content = subprocess.run(["git", "-C", str(repo), "show", f"HEAD:{git_path}"],
                                 check=True, capture_output=True).stdout
        destination.write_bytes(content)
        restored.append(str(destination))
    return restored
