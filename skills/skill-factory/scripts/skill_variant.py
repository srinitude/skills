#!/usr/bin/env python3
"""Plan or accept a separately adapted scope variant; never auto-adapt semantics.

Exit codes: 0 success, 1 blocked or failed without promotion, 2 bad usage.
Examples:
  mise run variant -- plan --source SOURCE --source-id skill:original \\
    --scope user --name portable-variant --dest AUTHORING_PARENT
  mise run variant -- accept --plan PLAN.json --candidate CANDIDATE --review REVIEW.json
"""
import argparse
import json
import subprocess
from pathlib import Path

from skill_scope import SCOPES, load_json
from skill_package import inventory, tree_digest
from variant_accept import accept
from variant_draft import draft, save_output
from variant_plan import make_plan
from invocation_acceptance import arguments, bindings


def parser_for_operation():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    plan = commands.add_parser("plan", help="read-only source, destination and project inventory")
    plan.add_argument("--source", required=True)
    plan.add_argument("--source-id", required=True)
    plan.add_argument("--source-scope", choices=SCOPES)
    plan.add_argument("--scope", choices=SCOPES, required=True)
    plan.add_argument("--name", required=True)
    plan.add_argument("--dest", required=True)
    plan.add_argument("--project")
    plan.add_argument("--project-id")
    plan.add_argument("--placement-receipt", help="verified integration receipt when installing")
    plan.add_argument("--refresh", action="store_true", help="explicitly compare source baseline with variant customizations")
    plan.add_argument("--in-place", action="store_true", help="explicitly adapt the source in place using the same acceptance gates")
    plan.add_argument("--output", help="save exact plan JSON outside packages and project context")
    prepare = commands.add_parser("review", help="prepare an unaccepted review with bound digests and full coverage")
    prepare.add_argument("--plan", required=True)
    prepare.add_argument("--candidate", required=True)
    prepare.add_argument("--output", required=True)
    commit = commands.add_parser("accept", help="validate the reviewed candidate before promotion")
    commit.add_argument("--plan", required=True)
    commit.add_argument("--candidate", required=True)
    commit.add_argument("--review", required=True)
    commit.add_argument("--prepare", help="save an unaccepted complete candidate at a new path")
    arguments(commit)
    return parser


def execute(args, plan):
    if args.operation == "plan":
        result = plan
    elif args.operation == "review":
        result = draft(plan, args.candidate)
    else:
        return accept(plan, args.candidate, load_json(args.review), bindings(args), args.prepare)
    if args.output:
        save_output(args.output, result, plan, getattr(args, "candidate", None))
    return result


def failure_report(args, plan, error):
    plan = plan if isinstance(plan, dict) else {}
    source = plan.get("source", {})
    source = source if isinstance(source, dict) else {}
    target = plan.get("target") if plan else {"name": getattr(args, "name", None),
              "scope": getattr(args, "scope", None), "parent": getattr(args, "dest", None)}
    preserved = None
    if source.get("root"):
        try:
            preserved = tree_digest(inventory(Path(source["root"]))) == source["digest"]
        except (OSError, ValueError):
            preserved = False
    return {"status": "FAIL", "operation": args.operation, "error": str(error),
            "source": {key: source.get(key) for key in ["identity", "name", "scope", "digest"]},
            "target": target, "source_preserved": preserved, "promoted": False,
            "material_adaptations": [], "validation": [{"status": "FAIL", "claim": str(error)}]}


def main():
    args = parser_for_operation().parse_args()
    plan = None
    try:
        plan = make_plan(args) if args.operation == "plan" else load_json(args.plan)
        result = execute(args, plan)
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError) as error:
        print(json.dumps(failure_report(args, plan, error)))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
