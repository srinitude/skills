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

DETAIL_FIELDS = {"outcome", "motivation", "value", "proof",
                 "applicability"}
OP_FIELDS = {"task", "outcome", "motivation", "why_default_path", "proof"}


def dependencies(task):
    return task.get("depends", []) + task.get("depends_post", [])


def run_commands(task):
    value = task.get("run", "")
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    return []


def load(root):
    try:
        with (root / "mise.toml").open("rb") as handle:
            tasks = tomllib.load(handle).get("tasks", {})
        path = root / "assets/use-case-contract.json"
        use_case = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise ValueError(str(error)) from error
    return tasks, use_case


def structure_problems(tasks):
    found, declared = [], set(tasks)
    for name, task in tasks.items():
        if not isinstance(task.get("depends"), list):
            found.append(f"tasks.{name}.depends must be an explicit array")
            continue
        if "depends_post" in task and not isinstance(task["depends_post"], list):
            found.append(f"tasks.{name}.depends_post must be an array")
            continue
        unknown = set(dependencies(task)) - declared
        if unknown:
            found.append(f"tasks.{name} has unknown dependencies: " +
                         ", ".join(sorted(unknown)))
        if not task.get("description"):
            found.append(f"tasks.{name}.description is required")
        if "run" in task and not run_commands(task):
            found.append(f"tasks.{name}.run must be text or a text array")
        elif any("mise run" in command for command in run_commands(task)):
            found.append(f"tasks.{name}.run must not invoke Mise")
    return found


def visit_node(tasks, name, state, trail):
    if state.get(name) == 1:
        return trail[trail.index(name):] + [name]
    if state.get(name) == 2:
        return None
    state[name] = 1
    trail.append(name)
    for dependency in dependencies(tasks[name]):
        if dependency in tasks:
            cycle = visit_node(tasks, dependency, state, trail)
            if cycle:
                return cycle
    trail.pop()
    state[name] = 2
    return None


def find_cycle(tasks):
    state, trail = {}, []
    for name in tasks:
        cycle = visit_node(tasks, name, state, trail)
        if cycle:
            return cycle
    return None


def path_counts(tasks, start):
    reachable, pending = set(), [start]
    while pending:
        name = pending.pop()
        if name in reachable:
            continue
        reachable.add(name)
        pending.extend(item for item in dependencies(tasks[name]) if item in tasks)
    incoming = {name: 0 for name in reachable}
    for name in reachable:
        for dependency in dependencies(tasks[name]):
            if dependency in incoming:
                incoming[dependency] += 1
    ready = [name for name, count in incoming.items() if count == 0]
    counts = {name: 0 for name in tasks}
    counts[start] = 1
    while ready:
        name = ready.pop()
        for dependency in dependencies(tasks[name]):
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
    cycle = find_cycle(tasks)
    if cycle:
        found.append("cycle: " + " -> ".join(cycle))
    contract, ci_task, operations, terms = contract_problems(tasks, use_case)
    found.extend(contract)
    operation_issues, names = operation_problems(tasks, operations, terms)
    found.extend(operation_issues)
    if not cycle:
        found.extend(route_problems(tasks, [ci_task] + names))
    return found


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
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
