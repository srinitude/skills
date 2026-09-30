"""Apply the exact standardization plan through the existing per-file ledger guard."""
import base64
from pathlib import Path

from agentic_request_contract import read_json
from review_ledger_context import require
from review_ledger_source import read_file
from scaffold_review import build_reviewed, current_inputs, load_review, read_context
from standardization_assets import validate_policy_assets
from standardization_mapping import repair_mapping_json
from standardization_format import check_formatter
from standardization_plan import build_plan, capture_files, directory_modes
from skill_package import promote, staged
from skill_scope import read_fields


def selected_plan(path):
    raw = read_file({'path': str(Path(path).absolute())})
    record = read_json(raw.decode('utf-8'))
    require(isinstance(record, dict) and isinstance(record.get('plan'), dict), 'plan-file needs the complete plan output')
    plan = record['plan']
    require(plan.get('version') == 1 and isinstance(plan.get('captured_at'), str), 'invalid standardization plan version or time')
    return plan, raw


def check_sources(root, plan, bindings):
    require(capture_files(root) == plan['before'], 'target bytes or modes changed since standardization planning')
    require(directory_modes(root) == plan['directory_modes'], 'target directories changed since planning')
    check_bindings(bindings)


def check_bindings(bindings):
    for path, raw in bindings:
        require(read_file({'path': str(path)}) == raw, 'standardization input changed: ' + str(path))


def planned_files(plan):
    return {item['path']: {key: item[key] for key in ['sha256', 'mode', 'content_base64']} for item in plan['files']}


def promotion_checks(root, factory, plan, bindings, review_path, review, review_raw, expected, changed):
    protected = [Path(name).resolve() for name in read_context(review['context'])[1]]
    protected += [Path(review['body_review']['path']).resolve(), *(path.resolve() for path, _ in bindings)]
    require(not (root.is_relative_to(factory) or factory.is_relative_to(root)), 'factory and target must be independent')
    require(not {root / name for name in changed}.intersection(protected), 'change overlaps a governing input')
    def before_promotion():
        check_sources(root, plan, bindings)
        check_formatter(plan['formatter'])
        current_inputs(factory, plan, review_path, review_raw)
        read_context(review['context'])
    def after_promotion(_backup):
        check_bindings(bindings)
        check_formatter(plan['formatter'], expected)
        current_inputs(factory, plan, review_path, review_raw)
        read_context(review['context'])
        require(capture_files(root) == expected, 'promoted target differs from reviewed bytes or modes')
        actual = directory_modes(root)
        require(all(actual.get(name) == mode for name, mode in plan['directory_modes'].items()), 'directory modes changed')
    return before_promotion, after_promotion


def apply_reviewed(root, profile, scope, rebase, factory, sources, plan_path, review_path, profile_path):
    require(plan_path and review_path, 'standardization requires --plan-file and --review before applying')
    supplied, plan_raw = selected_plan(plan_path)
    plan = build_plan(root, profile, scope, rebase, factory, sources, profile_path, supplied['captured_at'])
    require(plan == supplied, 'stale or altered standardization plan')
    require(all(type(item['mode']) is int and 0 <= item['mode'] <= 0o777 for item in plan['files']),
            'standardization can preserve only ordinary permission bits through this writer')
    review, review_raw = load_review(review_path, plan)
    bindings = [(Path(plan_path).absolute(), plan_raw), (Path(review_path).absolute(), review_raw),
                (Path(plan['profile_input']['path']), base64.b64decode(plan['profile_input']['content_base64']))]
    check_sources(root, plan, bindings)
    check_formatter(plan['formatter'])
    expected = planned_files(plan)
    changed = [name for name, item in expected.items() if plan['before'].get(name) != item]
    if not changed:
        validate_candidate(root)
        check_sources(root, plan, bindings)
        return {'changed': [], 'writes': [], 'execution_acceptance': 'pending'}
    before_promotion, after_promotion = promotion_checks(
        root, factory, plan, bindings, review_path, review, review_raw, expected, changed)
    with staged(root.parent, root.name) as candidate:
        writes = build_reviewed(factory, candidate, plan, review_path, review, review_raw,
                                check=lambda: check_sources(root, plan, bindings))
        validate_candidate(candidate)
        require(capture_files(candidate) == expected, 'candidate differs from planned bytes or modes')
        promote(candidate, root, {name: item['sha256'] for name, item in plan['before'].items()},
                preserve_unowned=True, check=before_promotion, verify=after_promotion)
    return {'changed': changed, 'writes': writes, 'execution_acceptance': 'pending'}


def validate_candidate(root):
    read_fields(root)
    repair_mapping_json(root)
    validate_policy_assets(root)
