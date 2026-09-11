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

def walk_error(error):
    raise error

class PackageRecoveryError(ValueError):
    """Automatic restoration failed; retain both directories for authorized recovery."""

@contextmanager
def package_lock(target):
    """One cooperating writer for this package or its individual files."""
    lock = target.parent / ("." + target.name + ".skill-lock")
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        yield
    finally:
        os.close(descriptor)
        lock.unlink()

def restore_package(stage, target, backup, moved):
    if target.exists():
        target.rename(stage)
    for original, destination in reversed(moved):
        if original.exists() or original.is_symlink():
            raise ValueError("unowned restoration collision")
        destination.rename(original)
    if backup.exists():
        backup.rename(target)

def tree_digest(files):
    return sha(json.dumps(files, sort_keys=True, separators=(",", ":")).encode())

def owned_entries(root):
    root = real_path(root)
    if not root.is_dir():
        raise ValueError("package or project directory is missing")
    for folder, dirs, names in os.walk(root, followlinks=False, onerror=walk_error):
        dirs[:] = sorted(name for name in dirs if name not in SKIP)
        for name in (name for name in sorted(dirs + names) if name not in SKIP and name != ".DS_Store"):
            yield Path(folder) / name

def unowned_entries(root):
    for folder, dirs, names in os.walk(root, followlinks=False, onerror=walk_error):
        for name in (name for name in sorted(dirs) if name in SKIP):
            dirs.remove(name)
            yield Path(folder) / name
        paths = (Path(folder) / name for name in sorted(names))
        yield from (path for path in paths if path.name in SKIP or path.name == ".DS_Store"
                    or path.suffix in {".pyc", ".pyo"})

@contextmanager
def retained_workdir(parent, prefix):
    folder = Path(tempfile.mkdtemp(prefix=prefix, dir=parent))
    try:
        yield folder
    except PackageRecoveryError:
        raise
    except BaseException:
        shutil.rmtree(folder)
        raise
    else:
        shutil.rmtree(folder)

def recover_stage(stage, target, backup, moved):
    try:
        restore_package(stage, target, backup, moved)
    except BaseException as error:
        raise PackageRecoveryError(f"restoration failed; retain {stage} and {backup} for recovery") from error

def owned_paths(root):
    root = real_path(root)
    for path in owned_entries(root):
        if path.is_symlink() or not (path.is_dir() or path.is_file()):
            raise ValueError(f"unsupported package entry: {path.relative_to(root)}")
        if path.is_file() and path.suffix not in {".pyc", ".pyo"}:
            yield path

def preserve_layout(source, destination):
    source = source.resolve()
    if not source.exists():
        return
    for original in [source, *(p for p in owned_entries(source) if p.is_dir())]:
        target = destination / original.relative_to(source)
        target.mkdir(parents=True, exist_ok=True)
        shutil.copystat(original, target)

def move_unowned(source, destination, moved):
    if not source.exists():
        return
    for original in unowned_entries(source):
        target = destination / original.relative_to(source)
        if target.exists() or target.is_symlink():
            raise ValueError("unowned destination collision; existing state must be preserved")
        target.parent.mkdir(parents=True, exist_ok=True)
        original.rename(target)
        moved.append((original, target))

@contextmanager
def staged(parent, name):
    with retained_workdir(parent, ".skill-stage-") as folder:
        yield folder / name

def inventory(root):
    root = real_path(root)
    return {path.relative_to(root).as_posix(): sha(path.read_bytes())
            for path in sorted(owned_paths(root))}

def content_files(root):
    return {key: value for key, value in inventory(root).items()
            if key != "evals/source-lineage.json"}

def copy_owned(source, target):
    target.mkdir(parents=True)
    for relative in inventory(source):
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, destination)

def install_stage(stage, target, backup, moved, expected, preserve_unowned, verify):
    if preserve_unowned:
        preserve_layout(backup, stage)
        move_unowned(backup, stage, moved)
    stage.rename(target)
    if inventory(target) != expected:
        raise ValueError("promoted package differs from the validated candidate")
    if verify:
        verify(backup)

def replace_directory(stage, target, *, preserve_unowned=False, verify=None):
    expected = inventory(stage)
    with retained_workdir(target.parent, ".skill-backup-") as temp:
        backup = Path(temp) / target.name
        if target.exists():
            target.rename(backup)
        moved = []
        try:
            install_stage(stage, target, backup, moved, expected, preserve_unowned, verify)
        except BaseException:
            recover_stage(stage, target, backup, moved)
            raise

def promote(stage, target, expected=None, *, preserve_unowned=False, check=None, verify=None):
    """Guard concurrent writers and restore the prior directory on failure."""
    with package_lock(target):
        current = inventory(target) if target.exists() else None
        if current != expected:
            raise ValueError("destination collision or destination changed since planning")
        if check:
            check()
        replace_directory(stage, target, preserve_unowned=preserve_unowned, verify=verify)
