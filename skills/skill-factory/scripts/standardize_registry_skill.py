#!/usr/bin/env python3
"""Plan or apply one factory-owned registry skill standardization."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from standardization_profile import load_profile, validate_profile
from standardization_runtime import LEDGER_EXAMPLES, LEDGER_FILES, ROOT_FILES
from skill_package import inventory, owned_paths
from skill_scope import SCOPES, label, read_fields, resolve
from scope_placement import check_placement

FACTORY = Path(__file__).resolve().parents[1]
COPIES = [
    ("assets/improvement-contract.json", "assets/improvement-contract.json"),
    ("assets/mise-primitives-catalog.json", "assets/mise-primitives-catalog.json"),
    ("references/resource-and-experiment-design.md", "references/resource-and-experiment-design.md"),
    ("references/improvement-dimensions.md", "references/improvement-dimensions.md"),
    ("references/use-case-specificity.md", "references/use-case-specificity.md"),
    ("references/generation-contract.md", "references/generation-contract.md"),
    ("references/skill-scope-contract.md", "references/skill-scope-contract.md"),
]
SCRIPTS = [
    "agentic_request_contract.py", "run_agentic_request.py", "domain_text.py",
    "check_improvement_contract.py", "check_domain_research.py",
    "check_use_case_contract.py", "check_mise_primitives.py",
    "check_primitive_lifecycle.py", "check_task_graph.py",
    "check_decision_records.py", "check_invocation_receipt.py",
    "sync_mise_primitives.py",
]
SCRIPTS += ["validate_skill.py", "lint_writing.py", "check_code_rules.py",
            "check_evals.py", "check_placeholders.py", "agentic_context.py",
            "check_javascript.ts", "skill_package.py"]
SCRIPTS += list(LEDGER_FILES)
CANONICAL_SCRIPTS = set(SCRIPTS[:12]) | {
    "check_placeholders.py",
    "agentic_context.py",
    "lint_writing.py",
    "validate_skill.py",
    "check_code_rules.py",
    "check_javascript.ts",
    "skill_package.py",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def planned_paths(root, profile):
    paths = {root / path.relative_to(root.resolve()) for path in owned_paths(root)}
    paths.update(root / name for name in ROOT_FILES + LEDGER_EXAMPLES)
    paths.add(root / "evals/source-mapping.json")
    paths.add(root / "scripts/tests/test_package_contract.py")
    paths.update(root / target for _, target in COPIES)
    paths.update(root / "scripts" / name for name in SCRIPTS)
    assets = ["use-case-contract.json", "primitive-lifecycle.json",
              "decision-records.json", "invocation-receipt-template.json",
              "mise-primitives.json"]
    paths.update(root / "assets" / name for name in assets)
    paths.update(root / path for path in profile.get("text_rewrites", {}))
    paths.update(root / rule["path"]
                 for rule in profile.get("section_rewrites", []))
    return sorted(paths)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_root", help="Existing real skill directory to inspect or update.")
    parser.add_argument("--profile", required=True, help="JSON profile containing the reviewed domain mappings and rewrites for this skill.")
    parser.add_argument("--apply", action="store_true", help="Apply the saved current plan through the per-file review and package promotion guards; requires --plan-file and --review.")
    parser.add_argument("--plan-file", help="saved complete no-write plan output")
    parser.add_argument("--review", help="current ledger, initial body and every planned-file review")
    parser.add_argument("--rebase-tracked-text", action="store_true", help="Plan from Git HEAD versions of tracked Markdown and evals/source-mapping.json; reviewed apply can replace their working-tree text.")
    parser.add_argument("--scope", choices=SCOPES, help="Intended availability. Retain an existing scope; a scope change requires the separate variant adaptation path.")
    parser.add_argument("--placement-receipt", help="Optional integration-owned installation receipt for the exact destination and discovery roots; omission means authoring, not installation proof.")
    return parser


def parse_args(argv):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.apply and (args.plan_file or args.review):
        parser.error('--plan-file and --review require --apply')
    return args


def scope_choice(root, args):
    existing = read_fields(root).get("metadata", {}).get("scope")
    choice = resolve(existing, args.scope) if args.apply or existing or args.scope else None
    if existing and args.scope and existing != args.scope:
        raise ValueError("scope change needs adaptation checks; use variant plan --in-place")
    inventory(root)
    if choice:
        check_placement(args.placement_receipt, choice["scope"], root.resolve())
    return choice


def prepare_inputs(args):
    root = Path(args.skill_root)
    if root.is_symlink() or not (root / 'SKILL.md').is_file():
        raise ValueError('target must be a real skill directory')
    profile = validate_profile(load_profile(args.profile, root.name), root.resolve())
    return root, profile, scope_choice(root, args)


def operation(args, root, profile, choice):
    scope = choice['scope'] if choice else None
    sources = (COPIES, SCRIPTS, CANONICAL_SCRIPTS)
    if not args.apply:
        from standardization_plan import build_plan
        plan = build_plan(root, profile, scope, args.rebase_tracked_text, FACTORY, sources, args.profile)
        return {'target': str(root.resolve()), 'mode': 'plan', 'writes': 0,
                'changed': [], 'scope': scope, 'plan': plan}
    from standardization_review import apply_reviewed
    result = apply_reviewed(root.resolve(), profile, scope, args.rebase_tracked_text,
                            FACTORY, sources, args.plan_file, args.review, args.profile)
    return {'target': str(root.resolve()), 'mode': 'apply', 'scope': scope, 'scope_label': label(scope),
            'writes': len(result['changed']), 'changed': [str(root / name) for name in result['changed']],
            'file_writes': result['writes'], 'execution_acceptance': 'pending'}


def main(argv=None):
    args = parse_args(argv)
    try:
        root, profile, choice = prepare_inputs(args)
    except ValueError as error:
        print(f'error: {error}', file=sys.stderr)
        return 2
    try:
        report = operation(args, root, profile, choice)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 1
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
