#!/usr/bin/env python3
"""Resolve skill scope without writes. Evidence interpretation remains model-owned.

Exit codes: 0 resolved, 1 needs clarification or invalid input, 2 bad usage.
Example: mise run resolve-scope -- --skill ../example --scope user
"""
import argparse
import json
from pathlib import Path

from skill_scope import QUESTION, SCOPES, label, load_json, read_fields, resolve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill")
    parser.add_argument("--scope", choices=SCOPES)
    parser.add_argument("--evidence")
    args = parser.parse_args()
    try:
        fields = read_fields(Path(args.skill)) if args.skill else {}
        evidence = load_json(args.evidence) if args.evidence else []
        if not isinstance(evidence, list):
            raise ValueError("scope evidence must be an array")
        result = resolve(fields.get("metadata", {}).get("scope"), args.scope, evidence)
        result.update(status="READY", label=label(result["scope"]), writes=0)
    except (OSError, ValueError) as error:
        result = {"status": "NEEDS_CLARIFICATION" if str(error) == QUESTION else "FAIL",
                  "question" if str(error) == QUESTION else "error": str(error), "writes": 0}
    print(json.dumps(result))
    return 0 if result["status"] == "READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
