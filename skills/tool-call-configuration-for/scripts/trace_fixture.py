#!/usr/bin/env python3
"""Emit a labeled fixture trace with or without skill instructions.

Exit codes:
  0  trace emitted
  1  checked source or behavior conflict
  2  usage or input error

Examples:
  python3 scripts/trace_fixture.py @tool.json --behavior @rules.json --condition with-skill
  python3 scripts/trace_fixture.py @tool.json --behavior @rules.json --condition without-skill
"""
import argparse
import json
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent / "lib"
sys.path.insert(0, str(LIB))

from common import InputError, WorkflowError  # noqa: E402
from profiles import read_behavior, resolve_tool  # noqa: E402


def events(tool, behavior, condition):
    name = tool["identity"]["callable_name"]
    trace = []
    if condition == "with-skill":
        trace.append({"event": "skill-load", "tool": name})
        trace.append({"event": "identity-check", "identity_hash": tool["identity_hash"]})
        trace.extend({"event": "behavior-rule", "rule_id": rule["id"],
                      "timing": rule["timing"]} for rule in behavior["rules"])
    trace.append({"event": "fixture-call", "tool": name, "executed": False})
    trace.append({"event": "result-classification", "result": "fixture-only"})
    return trace


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool_reference")
    parser.add_argument("--behavior", required=True)
    parser.add_argument("--registry")
    parser.add_argument("--condition", required=True,
                        choices=["with-skill", "without-skill"])
    args = parser.parse_args(argv)
    try:
        tool = resolve_tool(args.tool_reference, args.registry)
        behavior = read_behavior(args.behavior)
    except InputError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except WorkflowError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    result = {"schema": "tool-call-config/fixture-trace/v1",
              "condition": args.condition, "claim_limit": "fixture-only",
              "events": events(tool, behavior, args.condition)}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
