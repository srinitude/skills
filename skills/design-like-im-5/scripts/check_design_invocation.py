#!/usr/bin/env python3
"""Check one design run receipt."""
import argparse
import json
import sys
import tomllib
from pathlib import Path

from lib.design_policy_graph import dependencies
from lib.design_policy_text import text_problems

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
        return [f"entries.{index} lacks fields"]
    found = []
    if not isinstance(item["task"], str) or not item["task"]:
        found.append(f"entries.{index}.task needs text")
    if item["status"] not in STATUSES:
        found.append(f"entries.{index}.status is not valid")
    found += text_problems(item, {"applicability_reason", "proof"}, terms,
                           f"entries.{index}")
    return found


def required_run_tasks(tasks):
    found, pending = set(), ["complete"]
    while pending:
        name = pending.pop()
        if name in found or name not in tasks:
            continue
        found.add(name)
        pending.extend(dependencies(tasks[name]))
    return found - {SELF_TASK}


def problems(tasks, contract, receipt):
    found, entries = [], receipt.get("entries", [])
    terms = contract.get("domain_terms", [])
    if receipt.get("skill") != "design-like-im-5":
        found.append("skill must be design-like-im-5")
    found += text_problems(receipt, {"operation"}, terms, "receipt")
    if not isinstance(entries, list):
        return found + ["entries must be a list"]
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
        found.append("each task must be named once")
    status_by_name = {item.get("task"): item.get("status") for item in entries
                      if isinstance(item, dict)}
    for name in sorted(required_run_tasks(tasks)):
        if status_by_name.get(name) != "run":
            found.append(f"default task {name} must run")
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root")
    parser.add_argument("receipt")
    args = parser.parse_args()
    try:
        found = problems(*load(Path(args.root).resolve(),
                               Path(args.receipt).resolve()))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL {error}")
        return 2
    for problem in found:
        print(f"FAIL {problem}")
    print(f"design run receipt: {len(found)} problems")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
