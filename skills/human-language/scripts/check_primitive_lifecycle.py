#!/usr/bin/env python3
"""Validate domain aspects and package primitives across their full lifecycle.

Usage: check_primitive_lifecycle.py [skill-root]
Exit codes: 0 passes, 1 fails policy, 2 cannot read the input.
Example: check_primitive_lifecycle.py .
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

from domain_text import uses_term

REQUIRED_PHASES = {
    "discover", "research", "experiment", "decide", "create", "inspect",
    "update", "validate", "accept", "restore", "deprecate", "retire",
}
ROLE_FIELDS = ["role", "outcome", "motivation", "value",
               "failure_prevented", "proof"]
TASK_FIELDS = ["outcome", "motivation", "value", "proof", "applicability"]
ASPECT_FIELDS = ["outcome", "motivation", "proof"]


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path}: {error}") from error


def terms(contract):
    values = [contract.get("skill", "")] + contract.get("domain_terms", [])
    return [str(value) for value in values if str(value).strip()]


def text_problems(label, record, fields, domain_terms):
    problems = []
    for field in fields:
        value = record.get(field)
        if not isinstance(value, str) or len(value.strip()) < 12:
            problems.append(f"{label}.{field} needs specific text")
        if isinstance(value, str) and not uses_term(value, domain_terms):
            problems.append(f"{label}.{field} must name a domain term")
    return problems


def profile_problems(name, profile, phases, tasks, task_records, domain_terms):
    problems = []
    if not isinstance(profile, dict):
        return [f"profile {name} must be an object"]
    if set(profile) != phases:
        problems.append(f"profile {name} must cover every lifecycle phase")
    for phase, task in profile.items():
        if task not in tasks:
            problems.append(f"profile {name}.{phase} uses unknown Mise task {task}")
            continue
        record = task_records.get(task)
        if not isinstance(record, dict):
            problems.append(f"Mise task {task} lacks a domain lifecycle record")
            continue
        problems += text_problems(f"task {task}", record, TASK_FIELDS,
                                  domain_terms)
    return problems


def item_problems(kind, items, expected, profiles, contract, domain_terms):
    problems = []
    if set(items) != set(expected):
        problems.append(f"lifecycle inventory must match {kind}")
        return problems
    for name, item in items.items():
        profile = item.get("profile") if isinstance(item, dict) else None
        if profile not in profiles:
            problems.append(f"{kind}.{name} needs a real lifecycle profile")
        if kind == "primitive roles":
            role = contract["primitive_roles"].get(name, {})
            problems += text_problems(f"primitive {name}", role, ROLE_FIELDS,
                                      domain_terms)
        else:
            problems += text_problems(f"aspect {name}", item, ASPECT_FIELDS,
                                      domain_terms)
    return problems


def validate(root):
    lifecycle = read_json(root / "assets" / "primitive-lifecycle.json")
    contract = read_json(root / "assets" / "use-case-contract.json")
    with (root / "mise.toml").open("rb") as handle:
        tasks = set(tomllib.load(handle).get("tasks", {}))
    problems = []
    if lifecycle.get("skill") != contract.get("skill"):
        problems.append("lifecycle must name the current skill")
    phases = set(lifecycle.get("required_phases", []))
    if phases != REQUIRED_PHASES:
        problems.append("required lifecycle phases must match the contract")
    profiles = lifecycle.get("profiles", {})
    records = contract.get("task_graph", {}).get("tasks", {})
    domain_terms = terms(contract)
    for name, profile in profiles.items():
        problems += profile_problems(name, profile, phases, tasks, records,
                                     domain_terms)
    aspects = lifecycle.get("aspects", {})
    aspect_names = "domain aspects"
    problems += item_problems(aspect_names, aspects,
                              contract.get("domain_dimensions", {}), profiles,
                              contract, domain_terms)
    primitives = lifecycle.get("primitives", {})
    primitive_names = "primitive roles"
    problems += item_problems(primitive_names, primitives,
                              contract.get("primitive_roles", {}), profiles,
                              contract, domain_terms)
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args(argv)
    try:
        problems = validate(Path(args.root).resolve())
    except (ValueError, OSError, tomllib.TOMLDecodeError) as error:
        print(f"error: {error}")
        return 2
    for problem in problems:
        print(f"FAIL {problem}")
    print(f"Primitive lifecycle: {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
