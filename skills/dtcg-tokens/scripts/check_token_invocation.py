#!/usr/bin/env python3
"""Validate that one DTCG token invocation accounts for every Mise task."""
import argparse
import json
import sys
import tomllib
from pathlib import Path

from lib.token_policy_text import text_problems

FIELDS = {"task", "status", "applicability_reason", "proof"}
STATUSES = {"run", "inapplicable"}
SELF_TASK = "invocation-policy"


def load(root, receipt_path):
    with (root / "mise.toml").open("rb") as handle:
        tasks = tomllib.load(handle).get("tasks", {})
    contract = json.loads((root / "assets/use-case-contract.json").read_text())
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    return tasks, contract, receipt


def entry_problems(item, index, terms):
    if not isinstance(item, dict) or not FIELDS <= set(item):
        return [f"entries.{index} is incomplete"]
    found = []
    if not isinstance(item["task"], str) or not item["task"]:
        found.append(f"entries.{index}.task must be nonempty text")
    if not isinstance(item["status"], str) or item["status"] not in STATUSES:
        found.append(f"entries.{index}.status is invalid")
    found += text_problems(item, {"applicability_reason", "proof"}, terms,
                           f"entries.{index}")
    return found


def problems(tasks, contract, receipt):
    found, entries = [], receipt.get("entries", [])
    terms = contract.get("domain_terms", [])
    if receipt.get("skill") != "dtcg-tokens":
        found.append("skill must equal dtcg-tokens")
    if not receipt.get("operation"):
        found.append("operation is required")
    if not isinstance(entries, list):
        return found + ["entries must be an array"]
    names = []
    for index, item in enumerate(entries):
        found += entry_problems(item, index, terms)
        if isinstance(item, dict) and isinstance(item.get("task"), str):
            names.append(item["task"])
    expected = set(tasks) - {SELF_TASK}
    if expected - set(names):
        found.append("missing tasks: " + ", ".join(sorted(expected - set(names))))
    if set(names) - expected:
        found.append("unknown tasks: " + ", ".join(sorted(set(names) - expected)))
    if len(names) != len(set(names)):
        found.append("task entries must be unique")
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root")
    parser.add_argument("receipt")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        found = problems(*load(root, Path(args.receipt).resolve()))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL {error}")
        return 2
    for problem in found:
        print(f"FAIL {problem}")
    print(f"DTCG token invocation receipt: {len(found)} problems")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
