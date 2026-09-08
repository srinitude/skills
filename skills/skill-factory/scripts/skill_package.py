"""Owned file snapshots and recoverable, guarded package promotion."""
import hashlib
import json
import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path

SKIP = {".git", ".mise", ".artifacts", "__pycache__", "node_modules",
        ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def real_path(value):
    path = Path(value).absolute()
    if path.is_symlink():
        raise ValueError("symlink paths are not supported")
    return path.resolve()


def inventory(root):
    root = real_path(root)
    if not root.is_dir():
        raise ValueError("package or project directory is missing")
    found = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if SKIP.intersection(relative.parts) or path.name == ".DS_Store":
            continue
        if path.is_symlink() or not (path.is_dir() or path.is_file()):
            raise ValueError(f"unsupported package entry: {relative}")
        if path.is_file() and path.suffix not in {".pyc", ".pyo"}:
            found[relative.as_posix()] = sha(path.read_bytes())
    return found


def tree_digest(files):
    return sha(json.dumps(files, sort_keys=True, separators=(",", ":")).encode())


def content_files(root):
    return {key: value for key, value in inventory(root).items()
            if key != "evals/source-lineage.json"}


def copy_owned(source, target):
    target.mkdir(parents=True)
    for relative in inventory(source):
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, destination)


@contextmanager
def staged(parent, name):
    with tempfile.TemporaryDirectory(prefix=".skill-stage-", dir=parent) as temp:
        yield Path(temp) / name


def promote(stage, target, expected=None):
    """Guard concurrent writers and restore the prior directory on failure."""
    lock = target.parent / ("." + target.name + ".skill-lock")
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        current = inventory(target) if target.exists() else None
        if current != expected:
            raise ValueError("destination collision or destination changed since planning")
        replace_directory(stage, target)
    finally:
        os.close(descriptor)
        lock.unlink()


def replace_directory(stage, target):
    expected = inventory(stage)
    with tempfile.TemporaryDirectory(prefix=".skill-backup-", dir=target.parent) as temp:
        backup = Path(temp) / target.name
        if target.exists():
            target.rename(backup)
        try:
            stage.rename(target)
            if inventory(target) != expected:
                raise ValueError("promoted package differs from the validated candidate")
        except BaseException:
            if target.exists():
                target.rename(stage)
            if backup.exists():
                backup.rename(target)
            raise
