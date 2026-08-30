#!/usr/bin/env python3
"""Generate or apply one exact tool behavior configuration.

Exit codes:
  0  generated, applied, or already satisfied
  1  checked conflict, stale plan, or failed validation
  2  usage, identity, path, or input error

Examples:
  python3 scripts/tool_call_config.py generate @tool.json --behavior @rules.json --output ./out
  python3 scripts/tool_call_config.py apply @tool.json --target my-skill --skills-root ../ --behavior @rules.json --integration @plan.json
"""
import argparse
import json
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent / "lib"
sys.path.insert(0, str(LIB))

from apply_plan import apply, load_plan, resolve_target  # noqa: E402
from common import InputError, WorkflowError, generated_name, write_json  # noqa: E402
from profiles import read_behavior, resolve_tool  # noqa: E402
from render_skill import render  # noqa: E402
from matrix import rule_matrix  # noqa: E402


def parser():
    root = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = root.add_subparsers(dest="command")
    generate = commands.add_parser("generate")
    add_common(generate)
    generate.add_argument("--output", required=True)
    apply_parser = commands.add_parser("apply")
    add_common(apply_parser)
    apply_parser.add_argument("--target", required=True)
    apply_parser.add_argument("--skills-root", required=True)
    apply_parser.add_argument("--integration", required=True)
    apply_parser.add_argument("--evidence")
    return root


def add_common(command):
    command.add_argument("tool_reference")
    command.add_argument("--behavior", required=True)
    command.add_argument("--registry")


def normalize_argv(argv):
    args = list(argv)
    if args == ["help"]:
        return []
    if args and args[0] not in {"generate", "apply", "-h", "--help"}:
        args.insert(0, "generate")
    return args


def evidence(root, tool, behavior):
    path = Path(root).resolve()
    path.mkdir(parents=True, exist_ok=True)
    write_json(path / "tool-profile.json", tool)
    write_json(path / "behavior-profile.json", behavior)
    write_json(path / "rule-to-contract.json", rule_matrix(tool, behavior))
    return path


def generate(args, source_skill):
    tool = resolve_tool(args.tool_reference, args.registry)
    behavior = read_behavior(args.behavior)
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    evidence_dir = evidence(output / "evidence", tool, behavior)
    skill_path = render(output, tool, behavior, source_skill)
    report = {"status": "generated", "generated_name": generated_name(tool),
              "skill_path": str(skill_path), "evidence_dir": str(evidence_dir),
              "tool_identity_hash": tool["identity_hash"],
              "behavior_hash": behavior["behavior_hash"]}
    write_json(evidence_dir / "generation-result.json", report)
    return report


def apply_command(args):
    tool = resolve_tool(args.tool_reference, args.registry)
    behavior = read_behavior(args.behavior)
    target = resolve_target(args.target, args.skills_root)
    plan = load_plan(args.integration, tool, behavior)
    report = apply(target, plan)
    report["tool_identity_hash"] = tool["identity_hash"]
    report["behavior_hash"] = behavior["behavior_hash"]
    if args.evidence:
        directory = evidence(args.evidence, tool, behavior)
        write_json(directory / "apply-result.json", report)
        report["evidence_dir"] = str(directory)
    return report


def main(argv=None):
    root = parser()
    normalized = normalize_argv(sys.argv[1:] if argv is None else argv)
    if not normalized:
        root.print_help()
        return 0
    try:
        args = root.parse_args(normalized)
        source_skill = Path(__file__).resolve().parents[1]
        result = generate(args, source_skill) if args.command == "generate" else apply_command(args)
        print(json.dumps(result, sort_keys=True))
        return 0
    except InputError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except WorkflowError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
