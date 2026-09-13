"""Read-only predicates around externally performed native file effects.

The calling workflow retains authority, event correlation and semantic acceptance.
No check here performs the proposed effect or restores a failed native mutation.
"""
import re
from pathlib import Path

from review_ledger_body import revision
from review_ledger_context import require
from review_ledger_write import bindings, capture, current, target_path, validate
from skill_package import package_lock, sha


def native_contract(request, phase):
    require(phase in ('before', 'after'), 'invalid native check phase')
    require(request.get('phase', phase) == phase, 'request phase differs from the selected native check')
    require(request.get('action') == 'native-file', 'native check requires native-file action')
    change = request['change']
    require(isinstance(change, dict) and set(change) == {
        'operation', 'path', 'expected_sha256', 'new_file', 'body_sha256', 'reviewer', 'review', 'mode'},
        'native change has missing or unsupported fields')
    operation, expected = change['operation'], change['expected_sha256']
    require(operation in ('add', 'update', 'delete'), 'unsupported native file operation')
    require(expected is None or isinstance(expected, str) and re.fullmatch('[a-f0-9]{64}', expected),
        'invalid native before identity')
    require((expected is None) == (operation == 'add'), 'native operation and before identity disagree')
    require((change['new_file'] is None) == (operation == 'delete'), 'native replacement binding mismatch')
    require(operation != 'delete' or change['path'].casefold() != 'skill.md', 'cannot remove the root body')
    mode = change['mode']
    require(isinstance(mode, dict) and set(mode) == {'expected', 'new'}, 'invalid native mode fields')
    for key, absent in [('expected', operation == 'add'), ('new', operation == 'delete')]:
        require(mode[key] is None if absent else type(mode[key]) is int and 0 <= mode[key] <= 0o777,
            'native mode does not match operation or ordinary permissions')
    return change


def native_target(request, root, change):
    body_revision = revision(request)
    target = target_path(root, change['path'], body_revision is not None)
    inputs = bindings(request, root)
    if body_revision is not None:
        inputs.pop(1)
    paths = [Path(item['path']) for item in inputs]
    require(all(target != path.resolve() and (not target.exists() or not path.exists()
        or not target.samefile(path)) for path in paths), 'native target overlaps a governing or prepared input')
    return target


def desired_state(change, captured):
    if change['operation'] == 'delete':
        return None
    raw = captured[change['new_file']['path']]
    raw.decode('utf-8')
    return raw, change['mode']['new']


def identity(value):
    return None if value is None else {'sha256': sha(value[0]), 'mode': value[1]}


def inspect_state(change, old, wanted, phase):
    if phase == 'after':
        require(old == wanted, 'native readback differs from intended bytes, mode or absence')
        return
    expected = None if change['expected_sha256'] is None else {
        'sha256': change['expected_sha256'], 'mode': change['mode']['expected']}
    require(identity(old) == expected, 'stale native identity, mode or creation collision')
    require(old != wanted, 'native change makes no difference')


def native_check(request, root, phase, pending_body_review=None):
    change = native_contract(request, phase)
    require(pending_body_review is None or isinstance(pending_body_review, str)
        and re.fullmatch('[a-f0-9]{64}', pending_body_review), 'invalid caller-selected pending review digest')
    root = Path(root)
    target = native_target(request, root, change)
    with package_lock(root):
        target = native_target(request, root, change)
        captured = capture(request, root, phase)
        checked = validate(captured, request, root, phase, pending_body_review)
        observed, wanted = current(target), desired_state(change, captured)
        inspect_state(change, observed, wanted, phase)
    return {'phase': phase, 'path': change['path'], 'operation': change['operation'],
        'observed': identity(observed), 'intended': identity(wanted), 'checked': checked,
        'execution_acceptance': 'pending',
        'limit': 'Read-only source/body/review and exact file-state predicates. No native effect, event '
            'correlation, permission, semantic acceptance or automatic restoration. The cooperating '
            'lock ends when this check returns; it does not protect the interval before a native call. '
            'The caller must prove graph, lineage, authority, native capability and required isolation.'}
