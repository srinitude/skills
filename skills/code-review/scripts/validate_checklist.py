#!/usr/bin/env python3
"""Validate a saved code review checklist.

The input is a JSON object holding the review record fields: target,
contract, verdict, and next_check strings, findings and decisions lists,
and a status of active, blocked, or finalized. Each findings entry is an
object with id, severity, file, line, clause, evidence, suggestion, and
state. Each decisions entry is an object with id, finding, choice, reason,
and reversible. Pass - to read the object from stdin. The report is JSON
on stdout.

Exit codes:
  0  the checklist passes
  1  the checklist is invalid or cannot be read
  2  command usage is invalid, including a wrong script path

Example:
  SKILL_DIR=/path/to/skills/code-review
  python3 "$SKILL_DIR/scripts/validate_checklist.py" ./CHECKLIST.json
"""
import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_TEXT = ("contract", "next_check", "target")
REQUIRED_LISTS = ("decisions", "findings")
STATUSES = ("active", "blocked", "finalized")
VERDICTS = ("", "sign-off", "block")
SEVERITIES = ("blocker", "major", "minor", "nit")
FINDING_STATES = ("open", "resolved", "unverified")
FINDING_ID = re.compile(r"^F-[0-9]{3}$")
DECISION_ID = re.compile(r"^D-[0-9]{3}$")
DECISION_TEXT = ("choice", "reason")


def load_source(name):
    if name == "-":
        return sys.stdin.read()
    return Path(name).read_text(encoding="utf-8")


def filled(value):
    return isinstance(value, str) and bool(value.strip())


def finding_errors(entry, index):
    where = f"findings[{index}]"
    if not isinstance(entry, dict):
        return [f"{where} must be an object"]
    errors = []
    if not filled(entry.get("id")) or not FINDING_ID.match(entry["id"]):
        errors.append(where + ".id must match ^F-[0-9]{3}$")
    if entry.get("severity") not in SEVERITIES:
        errors.append(where + ".severity must be one of " + ", ".join(SEVERITIES))
    errors.extend(f"{where}.{field} must be a non-empty string"
                  for field in ("evidence", "file", "suggestion")
                  if not filled(entry.get(field)))
    if entry.get("state") not in FINDING_STATES:
        errors.append(where + ".state must be one of " + ", ".join(FINDING_STATES))
    return errors


def decision_errors(entry, index):
    where = f"decisions[{index}]"
    if not isinstance(entry, dict):
        return [f"{where} must be an object"]
    errors = []
    if not filled(entry.get("id")) or not DECISION_ID.match(entry["id"]):
        errors.append(where + ".id must match ^D-[0-9]{3}$")
    errors.extend(f"{where}.{field} must be a non-empty string"
                  for field in DECISION_TEXT if not filled(entry.get(field)))
    if not filled(entry.get("finding")):
        errors.append(where + ".finding must be a non-empty string")
    if not isinstance(entry.get("reversible"), bool):
        errors.append(where + ".reversible must be true or false")
    return errors


def list_errors(name, value, checker):
    if not isinstance(value, list):
        return []
    errors = []
    for index, entry in enumerate(value, start=1):
        errors.extend(checker(entry, index))
    return errors


def open_blockers(findings):
    if not isinstance(findings, list):
        return []
    rows = []
    for index, entry in enumerate(findings, start=1):
        if (isinstance(entry, dict)
                and entry.get("severity") == "blocker"
                and entry.get("state") == "open"):
            rows.append(index)
    return rows


def consistency_errors(value):
    status = value.get("status")
    verdict = value.get("verdict")
    errors = []
    if status == "blocked" and verdict != "block":
        errors.append("status blocked requires verdict block")
    if verdict == "sign-off" and status == "finalized":
        for row in open_blockers(value.get("findings")):
            errors.append(f"findings[{row}] open blocker conflicts with "
                          "sign-off verdict")
    return errors


def validate(value):
    if not isinstance(value, dict):
        return ["checklist must be a JSON object"]
    errors = [f"{field} must be a non-empty string"
              for field in REQUIRED_TEXT if not filled(value.get(field))]
    errors.extend(f"{field} must be a list" for field in REQUIRED_LISTS
                  if not isinstance(value.get(field), list))
    if value.get("status") not in STATUSES:
        errors.append("status must be one of " + ", ".join(STATUSES))
    if value.get("verdict") not in VERDICTS:
        errors.append("verdict must be one of " + ", ".join(VERDICTS))
    errors.extend(list_errors("findings", value.get("findings"), finding_errors))
    errors.extend(list_errors("decisions", value.get("decisions"), decision_errors))
    errors.extend(consistency_errors(value))
    return errors


def report(errors):
    return {"errors": errors, "status": "FAIL" if errors else "PASS"}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("checklist", help="JSON file path, or - for stdin")
    args = parser.parse_args(argv)
    try:
        value = json.loads(load_source(args.checklist))
        errors = validate(value)
    except (OSError, json.JSONDecodeError) as error:
        errors = [f"cannot read checklist: {error}"]
    print(json.dumps(report(errors), sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
