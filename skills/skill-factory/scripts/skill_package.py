"""Owned file snapshots and recoverable, guarded package promotion."""
import hashlib
import json
import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path

SKIP = {".git", ".mise", ".artifacts", ".venv", "__pycache__", "node_modules",
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
    return {path.relative_to(root).as_posix(): sha(path.read_bytes())
            for path in sorted(owned_files(root))}


def walk_error(error):
    raise error


def excluded(path):
    return path.name in SKIP | {".DS_Store"} or path.suffix in {".pyc", ".pyo"}


def owned_entries(root):
    root = real_path(root)
    if not root.is_dir():
        raise ValueError("package or project directory is missing")
    for parent, directories, names in os.walk(root, onerror=walk_error, followlinks=False):
        directories[:] = sorted(name for name in directories if not excluded(Path(name)))
        for name in sorted(directories + names):
            path = Path(parent) / name
            if excluded(path):
                continue
            if not path.is_symlink() and not (path.is_dir() or path.is_file()):
                raise ValueError(f"unsupported package entry: {path.name}")
            yield path


def owned_files(root):
    for path in owned_entries(root):
        if path.is_symlink():
            raise ValueError(f"unsupported package symlink: {path.name}")
        if path.is_file():
            yield path


def selected_files(targets, suffixes):
    files = []
    for target in targets:
        path = Path(target)
        if path.is_symlink():
            raise ValueError("selected input is a symlink")
        if path.is_dir():
            files.extend(sorted(p for p in owned_files(path) if p.suffix in suffixes))
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError(target)
    return files


def tree_digest(files):
    return sha(json.dumps(files, sort_keys=True, separators=(",", ":")).encode())


def content_files(root):
    return {key: value for key, value in inventory(root).items()
            if key != "evals/source-lineage.json"}


def copy_owned(source, target):
    source = real_path(source)
    target.mkdir(parents=True)
    for relative in inventory(source):
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, destination)
    directories = [source, *(path for path in owned_entries(source) if path.is_dir())]
    for directory in reversed(directories):
        destination = target / directory.relative_to(source)
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copystat(directory, destination)


@contextmanager
def staged(parent, name):
    with tempfile.TemporaryDirectory(prefix=".skill-stage-", dir=parent) as temp:
        yield Path(temp) / name


def promote(stage, target, expected=None, acceptance=None, draft=False):
    """Guard concurrent writers and restore the prior directory on failure."""
    lock = target.parent / ("." + target.name + ".skill-lock")
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        current = inventory(target) if target.exists() else None
        if current != expected:
            raise ValueError("destination collision or destination changed since planning")
        if draft:
            if current is not None or acceptance is not None:
                raise ValueError("an unaccepted draft must use a new destination")
        else:
            from invocation_acceptance import guard
            if acceptance is None:
                raise ValueError("host-bound acceptance is required before promotion")
            guard(stage, target, *acceptance)
        replace_directory(stage, target)
    finally:
        os.close(descriptor)
        lock.unlink()


def transfer_unowned(source, target, moved):
    for parent, directories, names in os.walk(source, onerror=walk_error, followlinks=False):
        entries = sorted(directories + names)
        directories[:] = sorted(name for name in directories if not excluded(Path(name)))
        for name in entries:
            path = Path(parent) / name
            if not excluded(path):
                continue
            destination = target / path.relative_to(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            path.rename(destination)
            moved.append((path, destination))


def replace_directory(stage, target):
    expected = inventory(stage)
    with tempfile.TemporaryDirectory(prefix=".skill-backup-", dir=target.parent) as temp:
        backup, incoming = Path(temp) / "original", Path(temp) / "incoming"
        copy_owned(stage, incoming)
        if target.exists():
            target.rename(backup)
        moved = []
        try:
            incoming.rename(target)
            if backup.exists():
                transfer_unowned(backup, target, moved)
                shutil.copystat(backup, target)
            if inventory(target) != expected:
                raise ValueError("promoted package differs from the validated candidate")
            stage.rename(Path(temp) / "consumed-candidate")
        except BaseException:
            for original, destination in reversed(moved):
                destination.rename(original)
            if target.exists():
                target.rename(incoming)
            if backup.exists():
                backup.rename(target)
            raise
