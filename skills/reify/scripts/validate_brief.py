#!/usr/bin/env python3
"""Validate a saved reification brief.

The input is a JSON object holding the reification record fields:
signal, outcome, done_means, first_milestone, and next_action strings,
constraints, sources_checked, decisions, and open_questions lists, and
a status of active, finalized, or scrapped. Each decisions entry is an
object with id, choice, reason, dependents, and reversible. Pass - to
read the object from stdin. The report is JSON on stdout.

Exit codes:
  0  the brief passes
  1  the brief is invalid or cannot be read
  2  command usage is invalid, including a wrong script path

Example:
  SKILL_DIR=/path/to/skills/reify
  python3 "$SKILL_DIR/scripts/validate_brief.py" ./BRIEF.json
"""
import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_TEXT = ("done_means", "first_milestone", "next_action",
                 "outcome", "signal")
REQUIRED_LISTS = ("constraints", "decisions", "open_questions",
                  "sources_checked")
STATUSES = ("active", "finalized", "scrapped")
DECISION_TEXT = ("choice", "reason")
DECISION_ID = re.compile(r"^D-[0-9]{3}$")


def load_source(name):
    if name == "-":
        return sys.stdin.read()
    return Path(name).read_text(encoding="utf-8")


def filled(value):
    return isinstance(value, str) and bool(value.strip())


def entry_errors(entry, index):
    where = f"decisions[{index}]"
    if not isinstance(entry, dict):
        return [f"{where} must be an object"]
    errors = []
    if not filled(entry.get("id")) or not DECISION_ID.match(entry["id"]):
        errors.append(where + ".id must match ^D-[0-9]{3}$")
    errors.extend(f"{where}.{field} must be a non-empty string"
                  for field in DECISION_TEXT if not filled(entry.get(field)))
    if not isinstance(entry.get("dependents"), list):
        errors.append(f"{where}.dependents must be a list")
    if not isinstance(entry.get("reversible"), bool):
        errors.append(f"{where}.reversible must be true or false")
    return errors


def decision_errors(decisions):
    if not isinstance(decisions, list):
        return []
    errors = []
    for index, entry in enumerate(decisions, start=1):
        errors.extend(entry_errors(entry, index))
    return errors


def validate(value):
    if not isinstance(value, dict):
        return ["brief must be a JSON object"]
    errors = [f"{field} must be a non-empty string"
              for field in REQUIRED_TEXT if not filled(value.get(field))]
    errors.extend(f"{field} must be a list" for field in REQUIRED_LISTS
                  if not isinstance(value.get(field), list))
    if value.get("status") not in STATUSES:
        errors.append("status must be one of " + ", ".join(STATUSES))
    errors.extend(decision_errors(value.get("decisions")))
    return errors


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
