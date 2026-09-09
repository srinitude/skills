#!/usr/bin/env python3
"""Scaffold a new skill directory with every factory check owner.

Creates SKILL.md, mise.toml, a CI workflow, support directories,
starter script and tests, seed evals, and copies of the checker
scripts so the new skill verifies itself. Prints a JSON summary.

Exit codes:
  0  skill created
  1  target already exists
  2  usage or input error

Example:
  python3 scripts/scaffold_skill.py --name release-notes \\
    --description "Use when release notes are needed from a git log." \\
    --dest /path/to/skills --scope user --audience human

Scope classifies intended availability. The explicit destination is an
authoring directory, not evidence of scope or an installation instruction.
"""
import argparse
import datetime
import json
import re
import shutil
import sys
from pathlib import Path
from scope_placement import check_placement
from skill_package import copy_owned, inventory, promote, real_path, staged, tree_digest
from use_case_audience import reading_key
from skill_scope import read_fields
from source_coverage import load_json, require
from invocation_acceptance import arguments, bindings
from runtime_package import copy_runtime, NATIVE_PROBES, HUMAN_SUPPORT

SKILL_DIR = Path(__file__).resolve().parents[1]
ASSETS = SKILL_DIR / "assets"
NAME_RE = re.compile(r"^(?!.*--)[a-z0-9]+(?:-[a-z0-9]+)*$")
DIRS = ["references", "assets", "examples", "scripts",
        "scripts/tests", "evals", ".github/workflows"]
FILLED = [
    ("SKILL.md", "skill-template.md"),
    ("mise.toml", "mise-template.toml"),
    ("references/decisions.md", "decisions-template.md"),
    ("examples/example-first-run.md", "example-template.md"),
    ("evals/evals.json", "evals-template.json"),
    ("evals/trigger-queries.json", "trigger-template.json"),
    ("assets/use-case-contract.json", "use-case-contract-template.json"),
    ("assets/decision-records.json", "decision-records-template.json"),
    ("assets/mise-primitives.json", "mise-primitives-template.json"),
    ("assets/primitive-lifecycle.json", "primitive-lifecycle-template.json"),
    ("assets/agentic-request-template.json", "agentic-request-template.json"),
]
COPIED = [
    ("assets/human-catalogs.json", "human-catalogs.json"),
    (".github/workflows/ci.yml", "ci/ci.yml"),
    ("scripts/skill_info.py", "starter-script.py"),
    ("scripts/tests/test_scripts.py", "starter-test.py"),
    ("scripts/tests/test_ci_contract.py", "starter-ci-test.py"),
    ("assets/eval-case-template.json", "eval-case-template.json"),
    ("assets/improvement-contract.json", "improvement-contract.json"),
    ("assets/mise-primitives-catalog.json", "mise-primitives-catalog.json"),
    ("assets/invocation-receipt-template.json",
     "invocation-receipt-template.json"),
    ("scripts/tests/test_agentic_request.py", "starter-agentic-test.py"),
]
SCRIPT_COPIED = [
    ("scripts/run_agentic_request.py", "run_agentic_request.py"),
    ("scripts/agentic_request_contract.py", "agentic_request_contract.py"),
]
SCRIPT_COPIED += [("scripts/tests/" + name, "tests/" + name) for name in NATIVE_PROBES]
SCRIPT_COPIED += [("scripts/" + name, name) for name in HUMAN_SUPPORT]
CHECKERS = ["lint_writing.py", "validate_skill.py",
            "check_code_rules.py", "check_evals.py",
            "check_placeholders.py", "check_improvement_contract.py",
            "check_use_case_contract.py", "check_domain_research.py",
            "check_task_graph.py", "check_invocation_receipt.py"]
CHECKERS.append("domain_text.py")
CHECKERS.append("source_coverage.py")
CHECKERS.append("mise_task_graph.py")
CHECKERS.append("check_native_code.mjs")
CHECKERS.extend(["code_languages.py", "check_shell_code.py"])
CHECKERS.extend(["invocation_acceptance.py", "skill_package.py", "skill_scope.py", "use_case_audience.py"])
CHECKERS.append("check_decision_records.py")
CHECKERS.extend(["check_mise_primitives.py", "check_primitive_lifecycle.py",
                 "sync_mise_primitives.py"])


def fill(template, tokens):
    text = (ASSETS / template).read_text(encoding="utf-8")
    for key, value in tokens.items():
        text = text.replace("{{%s}}" % key, value)
    return text


def argument_error(args):
    if not NAME_RE.fullmatch(args.name) or len(args.name) > 64:
        return ("name must use 1 to 64 lowercase letters, numbers, and single "
                f"hyphens without edge hyphens and got: {args.name!r}")
    if "Use when" not in args.description:
        return 'description must contain "Use when" so the skill triggers'
    if len(args.description) > 1024:
        return "description caps at 1024 characters"
    if "\n" in args.description or "\r" in args.description:
        return "description must stay on one line"
    if not Path(args.dest).is_dir():
        return f"destination directory does not exist: {args.dest}"
    return None


def build(target, tokens):
    for sub in DIRS:
        (target / sub).mkdir(parents=True)
    copy_runtime(SKILL_DIR, target)
    for destination, template in FILLED:
        (target / destination).write_text(fill(template, tokens),
                                          encoding="utf-8")
    for destination, source in COPIED:
        shutil.copy(ASSETS / source, target / destination)
    for destination, source in SCRIPT_COPIED:
        shutil.copy(SKILL_DIR / "scripts" / source, target / destination)
    for name in CHECKERS:
        shutil.copy(SKILL_DIR / "scripts" / name, target / "scripts" / name)
    for name in ["generation-contract.md", "resource-and-experiment-design.md",
                 "use-case-specificity.md", "writing-rules.md", "skill-scope-contract.md",
                 "evidence-acceptance.md", "human-matrix-format.md"]:
        shutil.copy(SKILL_DIR / "references" / name,
                    target / "references" / name)
    return len(inventory(target))


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--scope", choices=("user", "project"), required=True)
    parser.add_argument("--audience", choices=("human", "agent"), required=True)
    parser.add_argument("--placement-receipt", help="verified integration receipt when installing")
    parser.add_argument("--dest", required=True,
                        help="parent directory for the new skill")
    parser.add_argument("--candidate", help="deliver an exact reviewed package instead of creating a seed")
    arguments(parser)
    return parser.parse_args(argv)


def create_seed(args, target):
    require(not any(bindings(args).values()) and not args.placement_receipt,
            "acceptance or installation requires a reviewed --candidate; a scaffold remains unaccepted")
    tokens = {"NAME": args.name, "DESCRIPTION": json.dumps(args.description)[1:-1],
              "SCOPE": args.scope, "AUDIENCE": args.audience, "AUDIENCE_KEY": reading_key(args.audience),
              "DATE": datetime.date.today().isoformat()}
    with staged(target.parent, target.name) as candidate:
        count = build(candidate, tokens)
        promote(candidate, target, draft=True)
    return {"files": count, "acceptance": "pending; unaccepted scaffold",
            "next": "run mise run ci inside the new skill",
            "blocked_until": "every SCAFFOLD placeholder is replaced; check_placeholders.py exits 1 until then"}


def deliver_candidate(args, target, placement):
    from variant_accept import package_checks
    source = real_path(args.candidate)
    require(not source.is_relative_to(target) and not target.is_relative_to(source),
            "candidate and destination must be separate")
    with staged(target.parent, target.name) as candidate:
        copy_owned(source, candidate)
        fields = read_fields(candidate)
        require(fields["name"] == args.name and fields["description"] == args.description
                and fields["metadata"].get("scope") == args.scope, "candidate differs from creation intent")
        require(load_json(candidate / "assets/use-case-contract.json")["audience"]["primary"] == args.audience,
                "candidate audience differs from creation intent")
        checked = package_checks(candidate)
        inputs = {"candidate": tree_digest(inventory(source)), "scope": args.scope, "audience": args.audience,
                  "description": args.description, "placement": placement["kind"]}
        check_placement(args.placement_receipt, args.scope, target)
        promote(candidate, target, acceptance=({"route": "new", "inputs": inputs}, bindings(args)))
    return {"files": len(inventory(target)), "acceptance": "passed", "validation": checked,
            "limit": "Only the host-bound claims and selected package checks."}


def main(argv=None):
    args = parse_args(argv)
    error = argument_error(args)
    if error:
        print(f"error: {error}")
        return 2
    target = Path(args.dest).resolve() / args.name
    if target.exists():
        print(f"error: {target} exists; choose a new destination")
        return 1
    try:
        placement = check_placement(args.placement_receipt, args.scope, target)
    except (OSError, ValueError, KeyError) as error:
        print(f"error: {error}")
        return 1
    try:
        delivery = deliver_candidate(args, target, placement) if args.candidate else create_seed(args, target)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"error: {error}")
        return 1
    print(json.dumps({"created": str(target),
                      "scope": args.scope, "scope_label": args.scope + "-level",
                      "audience": args.audience, "placement": placement["kind"], **delivery}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
