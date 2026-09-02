#!/usr/bin/env python3
"""Validate exhaustive, domain-specific use of official Mise primitives.

Usage: check_mise_primitives.py [skill-root]
Exit codes: 0 passes, 1 fails policy, 2 cannot read the input.
Example: check_mise_primitives.py .
"""
import argparse
import json
import sys
import tomllib
from pathlib import Path

from domain_text import uses_term

TEXT_FIELDS = ["used_reason", "nonuse_reason", "creative_use", "evidence"]


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{path}: {error}") from error


def actual_fields(root, catalog):
    with (root / "mise.toml").open("rb") as handle:
        data = tomllib.load(handle)
    groups = {"config": set(data) & set(catalog["groups"]["config"])}
    groups["task"] = task_fields(data, catalog)
    groups["task_config"] = set(data.get("task_config", {}))
    groups["tool"] = tool_fields(data)
    return groups


def task_fields(data, catalog):
    allowed = set(catalog["groups"]["task"])
    return {key for task in data.get("tasks", {}).values()
            if isinstance(task, dict) for key in task if key in allowed}


def tool_fields(data):
    fields = set()
    for spec in data.get("tools", {}).values():
        fields |= set(spec) if isinstance(spec, dict) else {"version"}
    return fields


def domain_terms(contract):
    values = [contract.get("skill", "")] + contract.get("domain_terms", [])
    return [str(value) for value in values if str(value).strip()]


def text_problems(group, record, terms):
    problems = []
    for field in TEXT_FIELDS:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{group}.{field} must be nonempty text")
        elif "SCAFFOLD-PLACEHOLDER" in value:
            problems.append(f"{group}.{field} retains scaffold text")
    for field in TEXT_FIELDS[:3]:
        value = str(record.get(field, ""))
        if value and not uses_term(value, terms):
            problems.append(f"{group}.{field} must name a domain term")
    return problems


def group_problems(group, catalog, record, actual, terms):
    problems = text_problems(group, record, terms)
    used = record.get("used", [])
    skipped = record.get("not_applicable", [])
    if not isinstance(used, list) or not isinstance(skipped, list):
        return problems + [f"{group} dispositions must be string lists"]
    if not all(isinstance(item, str) for item in used + skipped):
        return problems + [f"{group} dispositions must be string lists"]
    if len(used) != len(set(used)) or len(skipped) != len(set(skipped)):
        problems.append(f"{group} dispositions contain duplicates")
    overlap = set(used) & set(skipped)
    if overlap:
        problems.append(f"{group} overlap: {sorted(overlap)}")
    if set(used) | set(skipped) != set(catalog):
        problems.append(f"{group} must classify every primitive")
    for name in sorted(set(used) - actual):
        problems.append(f"{group}.{name} claims used but is absent from mise.toml")
    for name in sorted(actual - set(used)):
        problems.append(f"{group}.{name} is present but classified not applicable")
    return problems


def validate(root):
    catalog = read_json(root / "assets" / "mise-primitives-catalog.json")
    decisions = read_json(root / "assets" / "mise-primitives.json")
    contract = read_json(root / "assets" / "use-case-contract.json")
    problems = []
    if decisions.get("catalog_version") != catalog.get("version"):
        problems.append("catalog_version must match the official catalog")
    if decisions.get("skill") != contract.get("skill"):
        problems.append("primitive decisions must name the current skill")
    if set(decisions.get("groups", {})) != set(catalog.get("groups", {})):
        problems.append("decision groups must match catalog groups")
        return problems
    actual = actual_fields(root, catalog)
    terms = domain_terms(contract)
    for group, primitives in catalog["groups"].items():
        record = decisions["groups"].get(group, {})
        problems += group_problems(group, primitives, record,
                                   actual.get(group, set()), terms)
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
    print(f"Mise primitives: {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
