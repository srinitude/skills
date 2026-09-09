"""Bound non-body file writes; callers retain authority and semantic judgment."""
import os
import re
import stat
import tempfile
from contextlib import contextmanager
from pathlib import Path

from agentic_request_contract import read_json
from review_ledger_context import recorded_work_contract, require
from review_ledger_source import check_source_capture, read_file
from skill_package import SKIP, package_lock, sha


def target_path(root, name):
    require(root.is_absolute() and root.is_dir() and root.resolve() == root,
            'write root must be an absolute canonical directory')
    relative = Path(name)
    require(name and relative.parts and not relative.is_absolute()
            and relative.as_posix() == name and not set(relative.parts) & (SKIP | {'..'})
            and name.casefold() != 'skill.md', 'unsupported owned file path; body writes need their separate review')
    target = root / relative
    require(target.resolve() == target and not target.is_symlink() and target.parent.is_dir(),
            'file path escapes its root, uses a symlink or has a missing parent')
    if target.exists():
        require(target.is_file() and target.stat().st_nlink == 1, 'target must be a singly linked regular file')
    return target


def bindings(request, root):
    return [{'path': request['ledger'], 'sha256': request['ledger_sha256']},
            {'path': str(root / 'SKILL.md'), 'sha256': request['change']['body_sha256']},
            *request['expected_documents'], request['original_source'], request['change']['new_file']]


def capture(request, root):
    return {path: read_file({'path': path}) for path in dict.fromkeys(
        binding['path'] for binding in bindings(request, root))}


def validate(captured, request, root):
    for binding in bindings(request, root):
        require(sha(captured[binding['path']]) == binding['sha256'], 'current write input digest mismatch')
    ledger_raw = captured[request['ledger']]
    data = read_json(ledger_raw.decode('utf-8'))
    sources = check_source_capture(data, request, captured)
    protocol = recorded_work_contract(data)
    fields = [row['field'] for row in protocol['review_fields']]
    change, review = request['change'], request['change']['review']
    require(len(set(fields)) == len(fields) and isinstance(review, dict) and set(review) == set(fields)
            and all(isinstance(value, str) and value.strip() for value in review.values()),
            'supply one nonempty declaration for every actual review field')
    require(isinstance(change['reviewer'], str) and change['reviewer'].strip(), 'missing declared reviewer')
    body_path = str(root / 'SKILL.md')
    body_text = captured[body_path].decode('utf-8')
    require(body_text.strip(), 'current target body must be nonempty')
    return {'ledger_sha256': sha(ledger_raw), 'ledger_bytes': len(ledger_raw),
            'documents': sources['documents'], 'source_sha256': sources['source_sha256'],
            'body': {'path': body_path, 'sha256': sha(captured[body_path]),
                     'text': body_text},
            'input_bytes': {path: len(raw) for path, raw in captured.items()},
            'method': protocol['method'], 'review_fields': protocol['review_fields']}


def current(target):
    if not target.exists():
        return None
    require(target.is_file() and not target.is_symlink(), 'target is no longer a regular file')
    return target.read_bytes(), stat.S_IMODE(target.stat().st_mode)


@contextmanager
def prepared_file(root, raw, mode):
    descriptor, name = tempfile.mkstemp(prefix='.skill-file-', dir=root.parent)
    path = Path(name)
    try:
        with os.fdopen(descriptor, 'wb') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        path.chmod(mode)
        yield path
    finally:
        path.unlink(missing_ok=True)


def install(root, target, wanted, expected):
    with prepared_file(root, *wanted) as prepared:
        require(current(target) == expected, 'target changed before file installation')
        if expected is None:
            os.link(prepared, target)
            prepared.unlink()
        else:
            os.replace(prepared, target)


def restore(request, root, target, old, installed):
    capture(request, root)
    require(current(target) == installed, 'post-check failed; independently changed target was not overwritten')
    if old is None:
        target.unlink()
    else:
        install(root, target, old, installed)
    capture(request, root)
    require(current(target) == old, 'failed to read back restored file state')


def apply_change(request, root, target):
    captured = capture(request, root)
    before = validate(captured, request, root)
    change, old = request['change'], current(target)
    expected = change['expected_sha256']
    require(expected is None or isinstance(expected, str) and re.fullmatch('[a-f0-9]{64}', expected),
            'expected file identity must be null or a lowercase SHA-256')
    require((None if old is None else sha(old[0])) == expected, 'stale file identity or creation collision')
    wanted = (captured[change['new_file']['path']], 0o644 if old is None else old[1])
    require(wanted != old, 'file change makes no difference')
    install(root, target, wanted, old)
    try:
        after = validate(capture(request, root), request, root)
        require(current(target) == wanted, 'file differs from the requested bytes or mode after writing')
    except BaseException:
        restore(request, root, target, old, wanted)
        raise
    return {'path': change['path'], 'old_sha256': expected, 'new_sha256': sha(wanted[0]),
            'mode': wanted[1], 'before': before, 'after': after,
            'reviewer': change['reviewer'], 'review': change['review'], 'execution_acceptance': 'pending',
            'limit': 'Exact supplied byte bindings and this individual non-body create/replacement only. '
                     'Review values are caller declarations, not authenticated judgment or permission. '
                     'The caller establishes source authority and completes semantic review and invalidation. '
                     'Other write paths are not guarded by this function. Cooperating package lock, atomic '
                     'replacement and conditional in-process restoration only; no crash rollback, cross-file '
                     'transaction or hostile-writer isolation. Unreadable inputs can prevent restoration.'}


def write_file(request, root):
    root = Path(root)
    require(request.get('action') == 'write-file', 'file writer requires write-file action')
    change = request['change']
    require(set(change) == {'path', 'expected_sha256', 'new_file', 'body_sha256', 'reviewer', 'review'},
            'file change has missing or unsupported fields')
    target = target_path(root, change['path'])
    input_paths = [Path(item['path']) for item in bindings(request, root)]
    with package_lock(root):
        target = target_path(root, change['path'])
        require(all(target != path.resolve() and (not target.exists() or not path.exists()
                    or not target.samefile(path)) for path in input_paths),
                'file change overlaps a governing or prepared input')
        return apply_change(request, root, target)
