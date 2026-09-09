#!/usr/bin/env python3
"""Validate that one skill invocation accounts for every Mise task.

Usage:
  python3 scripts/check_invocation_receipt.py SKILL_ROOT RECEIPT

Exit codes:
  0  every task was run or has a domain-specific inapplicability proof
  1  the receipt is incomplete or invalid
  2  bad usage

Example:
  python3 scripts/check_invocation_receipt.py . /tmp/invocation.json
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

from domain_text import uses_generic_task_template, uses_term
from invocation_acceptance import check
from source_coverage import load_json

FIELDS = {"task", "status", "applicability_reason", "proof"}
STATUSES = {"run", "inapplicable"}
SELF_TASK = "invocation-policy"


def load(root, receipt_path):
    try:
        with (root / "mise.toml").open("rb") as handle:
            tasks = tomllib.load(handle).get("tasks", {})
        use_case = load_json(root / "assets/use-case-contract.json")
        receipt = load_json(receipt_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise ValueError(str(error)) from error
    return tasks, use_case, receipt


def entry_problems(item, index, terms):
    if not isinstance(item, dict) or not FIELDS <= set(item):
        return [f"entries.{index} needs {', '.join(sorted(FIELDS))}"]
    found = []
    if not isinstance(item["task"], str) or not item["task"]:
        found.append(f"entries.{index}.task must be a nonempty string")
    status = item["status"]
    if not isinstance(status, str) or status not in STATUSES:
        found.append(f"entries.{index}.status is invalid")
    for field in ["applicability_reason", "proof"]:
        if not isinstance(item[field], str) or not uses_term(item[field], terms):
            found.append(f"entries.{index}.{field} needs a package domain term")
        elif uses_generic_task_template(item[field]):
            found.append(f"entries.{index}.{field} uses generic scaffold language")
    return found


def problems(tasks, use_case, receipt, skill):
    if not isinstance(use_case, dict) or not isinstance(receipt, dict):
        return ["use-case and receipt must be objects"]
    found, entries = [], receipt.get("entries", [])
    terms = use_case.get("domain_terms", [])
    if receipt.get("skill") != skill:
        found.append(f"skill must equal directory name {skill}")
    operation = receipt.get("operation")
    if not isinstance(operation, str) or not operation:
        found.append("operation must be a nonempty string")
    if not isinstance(entries, list):
        return found + ["entries must be an array"]
    names = []
    for index, item in enumerate(entries):
        found.extend(entry_problems(item, index, terms))
        if isinstance(item, dict) and isinstance(item.get("task"), str):
            names.append(item["task"])
    expected = set(tasks) - {SELF_TASK}
    missing, extra = expected - set(names), set(names) - expected
    if missing:
        found.append("missing tasks: " + ", ".join(sorted(missing)))
    if extra:
        found.append("unknown tasks: " + ", ".join(sorted(extra)))
    if len(names) != len(set(names)):
        found.append("task entries must be unique")
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill_root")
    parser.add_argument("receipt")
    for name in ["acceptance-context", "context-sha256", "receipt-sha256"]:
        parser.add_argument("--" + name, help="host-bound evidence acceptance input")
    args = parser.parse_args(argv)
    root = Path(args.skill_root).resolve()
    try:
        receipt_path = Path(args.receipt).absolute()
        tasks, use_case, receipt = load(root, receipt_path)
        found = problems(tasks, use_case, receipt, root.name)
        report = check(root, receipt_path, receipt, args) if not found else None
    except (ValueError, OSError, UnicodeError, KeyError, TypeError) as error:
        print(f"FAIL {error}")
        return 1
    for problem in found:
        print(f"FAIL {problem}")
    print(f"invocation receipt: {len(found)} problems")
    print("evidence acceptance: " + (json.dumps(report) if report else "pending; task accounting only"))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
