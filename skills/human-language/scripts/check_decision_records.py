#!/usr/bin/env python3
"""Validate motivated deterministic and model-owned skill decisions.

Usage:
  python3 scripts/check_decision_records.py [skill-root]

Exit codes:
  0  decision records pass
  1  records are missing, generic, or invalid
  2  bad usage

Example:
  python3 scripts/check_decision_records.py .
"""
import argparse
import json
import re
import sys
from pathlib import Path

from domain_text import uses_generic_task_template, uses_term

FIELDS = {"id", "kind", "outcome", "motivation", "why_this_path",
          "owner", "inputs", "expected_effect", "proof", "falsifier",
          "failure_branch"}
TEXT_FIELDS = {"outcome", "motivation", "why_this_path", "expected_effect",
               "proof", "falsifier", "failure_branch"}
OWNERS = {"deterministic": "mise", "model_owned": "model",
          "human_owned": "human"}
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SENTINEL = "SCAFFOLD-" + "PLACEHOLDER"


def load_json(path):
    if not path.is_file():
        raise ValueError(f"missing {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in {path}: {error}") from error


def record_problems(item, index, terms):
    found = []
    if not isinstance(item, dict):
        return [f"records.{index} must be an object"]
    missing = sorted(FIELDS - set(item))
    if missing:
        return [f"records.{index} missing {', '.join(missing)}"]
    if not ID_RE.fullmatch(item["id"]):
        found.append(f"records.{index}.id must use kebab-case")
    kind = item["kind"]
    if kind not in OWNERS:
        found.append(f"records.{index}.kind is invalid")
    elif item["owner"] != OWNERS[kind]:
        found.append(f"records.{index}.owner must equal {OWNERS[kind]}")
    if not isinstance(item["inputs"], list) or not item["inputs"]:
        found.append(f"records.{index}.inputs must be a nonempty array")
    for field in sorted(TEXT_FIELDS):
        if not uses_term(item[field], terms):
            found.append(f"records.{index}.{field} needs a package domain term")
        elif uses_generic_task_template(item[field]):
            found.append(f"records.{index}.{field} uses generic scaffold language")
    return found


def problems(data, terms, skill):
    found = []
    if data.get("skill") != skill:
        found.append(f"skill must equal directory name {skill}")
    if SENTINEL in json.dumps(data):
        found.append("scaffold placeholder remains in decision records")
    records = data.get("records", [])
    if not isinstance(records, list) or not records:
        return found + ["records must be a nonempty array"]
    ids = []
    for index, item in enumerate(records):
        found.extend(record_problems(item, index, terms))
        if isinstance(item, dict) and "id" in item:
            ids.append(item["id"])
    if len(ids) != len(set(ids)):
        found.append("record ids must be unique")
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill_root", nargs="?", default=".")
    args = parser.parse_args(argv)
    root = Path(args.skill_root).resolve()
    try:
        decisions = load_json(root / "assets" / "decision-records.json")
        use_case = load_json(root / "assets" / "use-case-contract.json")
    except ValueError as error:
        print(f"FAIL {error}")
        return 1
    found = problems(decisions, use_case.get("domain_terms", []), root.name)
    for problem in found:
        print(f"FAIL {problem}")
    print(f"decision records: {len(found)} problems")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
