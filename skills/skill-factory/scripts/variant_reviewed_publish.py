"""Publish complete future variant files through the existing ledger review guard."""
import base64
import stat
from pathlib import Path
from functools import partial

from agentic_request_contract import read_json
from review_ledger_context import require
from review_ledger_source import read_file
from scaffold_review import build_reviewed, current_inputs, load_review, read_context
from skill_package import inventory, promote, sha, staged
from standardization_plan import directory_modes
from standardization_review import planned_files
from variant_context import check_current
from variant_publication_plan import check_bindings, package_state


def current_sources(plan, publication, staging=None, backup=None, locked=False):
    target = Path(plan['target']['path'])
    excluded = [target.parent / ('.' + target.name + '.skill-lock')] if locked else []
    if backup is not None:
        excluded.append(backup.parent)
    source = backup if backup is not None and plan['in_place'] else Path(plan['source']['root'])
    check_current(plan, staging, source_root=source if plan['in_place'] else None, excluded_paths=excluded)
    require(package_state(source) == publication['source_before'], 'variant source bytes or permissions changed')
    require(package_state(Path(publication['candidate'])) == publication['candidate_before'],
            'variant candidate changed since publication planning')
    if backup is None:
        require((package_state(target) if target.exists() else None) == publication['target_before'],
                'variant destination changed since publication planning')
    check_bindings(publication['inputs'])


def publication_review(path, review_path, publication, factory):
    require(path and review_path, 'variant publication requires --plan-file and --ledger-review')
    binding = {'path': str(Path(path).absolute())}
    raw = read_file(binding)
    record = read_json(raw.decode('utf-8'))
    require(isinstance(record, dict) and record.get('plan') == publication, 'stale or altered variant publication plan')
    review, review_raw = load_review(review_path, publication)
    protected = [Path(name).resolve() for name in read_context(review['context'])[1]]
    protected += [Path(review['body_review']['path']).resolve(), Path(binding['path']).resolve(),
                  Path(review_path).resolve(), *(Path(item['path']).resolve() for item in publication['inputs'])]
    target = Path(publication['target'])
    require(not (target.is_relative_to(factory) or factory.is_relative_to(target)),
            'factory and variant destination must be independent')
    require(not any(path == target or path.is_relative_to(target) for path in protected),
            'variant publication overlaps a governing input')
    return review, review_raw, (binding, raw)


def prepare_directories(candidate, modes):
    for name in sorted(modes, key=lambda item: (len(Path(item).parts), item)):
        (candidate / name).mkdir(parents=True, exist_ok=True)
    for name in sorted(modes, key=lambda item: len(Path(item).parts), reverse=True):
        (candidate / name).chmod(modes[name])


def verify_layout(target, publication):
    expected = dict(publication['candidate_before']['directories'])
    if publication['target_before'] is not None:
        expected.update(publication['target_before']['directories'])
    actual = directory_modes(target)
    require(actual == expected, 'variant directories or modes changed')



def retirement_checks(publication, review, check, original, target=None):
    records = []
    for item in publication['retirements']:
        check()
        body_root = original if target is None else target
        body = read_file({'path': str(body_root / 'SKILL.md')})
        expected_body = (publication['target_before']['files']['SKILL.md']['sha256'] if target is None else
                         next(file['sha256'] for file in publication['files'] if file['path'] == 'SKILL.md'))
        require(sha(body) == expected_body, 'retirement body changed')
        path = original / item['path']
        require(read_file({'path': str(path)}) == base64.b64decode(item['content_base64']),
                'retired file bytes changed')
        require(stat.S_IMODE(path.stat().st_mode) == item['mode'], 'retired file mode changed')
        if target is not None:
            removed = target / item['path']
            require(not removed.exists() and not removed.is_symlink(), 'retired file remains published')
            records.append({'action': 'retire-file', 'path': item['path'], 'old_sha256': item['sha256'],
                            'new_sha256': None, 'old_mode': item['mode'], 'new_mode': None,
                            **review['files'][item['path']], 'execution_acceptance': 'pending'})
    return records


def publish_reviewed(plan, publication, factory, plan_path, review_path, validate_candidate):
    review, review_raw, (binding, raw) = publication_review(plan_path, review_path, publication, factory)
    target = Path(publication['target'])
    expected = planned_files(publication)
    before = publication['target_before']
    def inputs(staging=None, backup=None, locked=False):
        current_sources(plan, publication, staging, backup, locked)
        require(read_file(binding) == raw, 'variant publication plan changed')
        current_inputs(factory, publication, review_path, review_raw)
        read_context(review['context'])
    inputs()
    with staged(target.parent, target.name) as candidate:
        writes = build_reviewed(factory, candidate, publication, review_path, review, review_raw,
                                check=partial(inputs, candidate.parent))
        prepare_directories(candidate, publication['candidate_before']['directories'])
        validation = validate_candidate(candidate)
        require(package_state(candidate)['files'] == expected, 'variant validation changed planned files or modes')
        inputs(candidate.parent)
        def before_promotion():
            inputs(candidate.parent, locked=True)
            retirement_checks(publication, review, partial(inputs, candidate.parent, locked=True), target)
        def verify(backup):
            inputs(candidate.parent, backup, True)
            require(package_state(target)['files'] == expected, 'published variant differs from reviewed files or modes')
            verify_layout(target, publication)
            writes.extend(retirement_checks(publication, review,
                partial(inputs, candidate.parent, backup, True), backup, target))
        promote(candidate, target, None if before is None else {name: x['sha256'] for name, x in before['files'].items()},
                preserve_unowned=True, check=before_promotion, verify=verify)
    return validation, writes
