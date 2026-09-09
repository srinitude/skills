#!/usr/bin/env python3
"""Validate a domain-specific Mise graph with one dependency path.

Usage:
  python3 scripts/check_task_graph.py [skill-root]

Exit codes:
  0  graph is specialized, connected, acyclic, and single-path
  1  graph or its domain contract is invalid
  2  bad usage

Example:
  python3 scripts/check_task_graph.py .
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

from domain_text import uses_generic_task_template, uses_term
from mise_task_graph import cycle, graphs, structure_problems
from source_coverage import load_json

DETAIL_FIELDS = {"outcome", "motivation", "value", "proof",
                 "applicability"}
OP_FIELDS = {"task", "outcome", "motivation", "why_default_path", "proof"}


def load(root):
    try:
        with (root / "mise.toml").open("rb") as handle:
            tasks = tomllib.load(handle).get("tasks", {})
        path = root / "assets/use-case-contract.json"
        use_case = load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise ValueError(str(error)) from error
    return tasks, use_case


def path_counts(tasks, start):
    reachable, pending = set(), [start]
    while pending:
        name = pending.pop()
        if name in reachable:
            continue
        reachable.add(name)
        pending.extend(item for item in tasks[name] if item in tasks)
    incoming = {name: 0 for name in reachable}
    for name in reachable:
        for dependency in tasks[name]:
            if dependency in incoming:
                incoming[dependency] += 1
    ready = [name for name, count in incoming.items() if count == 0]
    counts = {name: 0 for name in tasks}
    counts[start] = 1
    while ready:
        name = ready.pop()
        for dependency in tasks[name]:
            if dependency not in incoming:
                continue
            counts[dependency] = min(2, counts[dependency] + counts[name])
            incoming[dependency] -= 1
            if incoming[dependency] == 0:
                ready.append(dependency)
    return counts


def domain_record_problems(label, item, fields, terms):
    if not isinstance(item, dict) or not fields <= set(item):
        return [f"{label} needs {', '.join(sorted(fields))}"]
    found = []
    for field in sorted(fields - {"task"}):
        if not uses_term(item[field], terms):
            found.append(f"{label}.{field} needs a package domain term")
        if uses_generic_task_template(item[field]):
            found.append(f"{label}.{field} uses generic scaffold language")
    return found


def contract_problems(tasks, use_case):
    found, graph = [], use_case.get("task_graph", {})
    terms = use_case.get("domain_terms", [])
    ci_task = graph.get("ci_task")
    operations = graph.get("public_operations", [])
    records = graph.get("tasks", {})
    if ci_task not in tasks:
        found.append("task_graph.ci_task must name a declared task")
    if not isinstance(operations, list) or not operations:
        found.append("task_graph.public_operations needs a non-CI operation")
        operations = []
    if not isinstance(records, dict):
        found.append("task_graph.tasks must be an object")
        records = {}
    missing, extra = set(tasks) - set(records), set(records) - set(tasks)
    if missing:
        found.append("missing task records: " + ", ".join(sorted(missing)))
    if extra:
        found.append("unknown task records: " + ", ".join(sorted(extra)))
    for name, item in records.items():
        found.extend(domain_record_problems(f"tasks.{name}", item,
                                            DETAIL_FIELDS, terms))
    return found, ci_task, operations, terms


def operation_problems(tasks, operations, terms):
    found, names = [], []
    for index, item in enumerate(operations):
        label = f"public_operations.{index}"
        found.extend(domain_record_problems(label, item, OP_FIELDS, terms))
        if isinstance(item, dict) and item.get("task") in tasks:
            names.append(item["task"])
        else:
            found.append(f"{label}.task must name a declared task")
    if len(names) != len(set(names)):
        found.append("public operation tasks must be unique")
    return found, names


def route_problems(tasks, entries):
    found, reached = [], set()
    for entry in entries:
        if entry not in tasks:
            continue
        counts = path_counts(tasks, entry)
        reached.update(name for name, count in counts.items() if count)
        for name, count in counts.items():
            if count > 1:
                found.append(f"multiple dependency paths from {entry} to {name}")
    for name in sorted(set(tasks) - reached):
        found.append(f"no public operation reaches {name}")
    return found


def problems(tasks, use_case):
    found = structure_problems(tasks)
    if found:
        return found
    contract, ci_task, operations, terms = contract_problems(tasks, use_case)
    found.extend(contract)
    operation_issues, names = operation_problems(tasks, operations, terms)
    found.extend(operation_issues)
    for windows in (False, True):
        calls, order = graphs(tasks, windows)
        found_cycle = cycle(calls) or cycle(order)
        if found_cycle:
            found.append("cycle: " + " -> ".join(found_cycle))
        else:
            found.extend(route_problems(calls, [ci_task] + names))
    return list(dict.fromkeys(found))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill_root", nargs="?", default=".")
    args = parser.parse_args(argv)
    try:
        tasks, use_case = load(Path(args.skill_root).resolve())
    except ValueError as error:
        print(f"FAIL {error}")
        return 1
    found = problems(tasks, use_case)
    for problem in found:
        print(f"FAIL {problem}")
    print(f"task graph: {len(found)} problems")
    print("Explicit references only; native configuration, phase/argument variants and runtime effects require separate evidence.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
