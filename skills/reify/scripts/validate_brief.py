#!/usr/bin/env python3
"""Validate a saved reification brief.

The input is a JSON object with outcome, done_means, first_milestone,
and next_action strings. Pass - to read the object from stdin. The
report is JSON on stdout.

Exit codes:
  0  the brief passes
  1  the brief is invalid or cannot be read
  2  command usage is invalid

Example:
  python3 scripts/validate_brief.py BRIEF.json
"""
import argparse
import json
import sys
from pathlib import Path

REQUIRED = ("done_means", "first_milestone", "next_action", "outcome")


def load_source(name):
    if name == "-":
        return sys.stdin.read()
    return Path(name).read_text(encoding="utf-8")


def validate(value):
    if not isinstance(value, dict):
        return ["brief must be a JSON object"]
    return [
        f"{field} must be a non-empty string"
        for field in REQUIRED
        if not isinstance(value.get(field), str) or not value[field].strip()
    ]


def report(errors):
    return {"errors": errors, "status": "FAIL" if errors else "PASS"}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("brief", help="JSON file path, or - for stdin")
    args = parser.parse_args(argv)
    try:
        value = json.loads(load_source(args.brief))
        errors = validate(value)
    except (OSError, json.JSONDecodeError) as error:
        errors = [f"cannot read brief: {error}"]
    print(json.dumps(report(errors), sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
