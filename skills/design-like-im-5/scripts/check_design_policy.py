#!/usr/bin/env python3
"""Check design scope, tasks, and choice rules."""
import argparse
import json
import sys
import tomllib
from pathlib import Path

from lib.design_policy_contract import decision_problems, dimension_problems, term_problems
from lib.design_policy_graph import find_cycle, route_problems, structure_problems
from lib.design_policy_research import research_problems
from lib.design_policy_text import text_problems

ASPECTS = {"actors", "objects", "actions", "states", "invariants", "variants",
           "interfaces", "authorities", "failures", "recoveries", "evidence",
           "time", "resources", "quality", "terminology", "exclusions"}
PRIMITIVES = {"skill_body", "references", "assets", "scripts", "tests",
              "mise_tasks", "examples", "evals", "policies", "schemas",
              "records"}
PHASES = {"discover", "research", "experiment", "decide", "create", "inspect",
          "update", "validate", "accept", "restore", "deprecate", "retire"}
TEXT_FIELDS = {"outcome", "motivation", "value", "proof", "applicability"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load(root):
    paths = ["use-case-contract", "primitive-lifecycle", "decision-records",
             "mise-primitives-catalog", "mise-primitives"]
    values = [read_json(root / f"assets/{name}.json") for name in paths]
    with (root / "mise.toml").open("rb") as handle:
        tasks = tomllib.load(handle)["tasks"]
    return (*values, tasks)


def check_domain_research(contract, *_, root=None):
    return research_problems(contract, ASPECTS)


def check_use_case(contract, *_, root=None):
    found, terms = [], contract.get("domain_terms", [])
    if contract.get("skill") != "design-like-im-5":
        found.append("design skill name is wrong")
    found += term_problems(terms)
    found += dimension_problems(contract.get("domain_dimensions"), ASPECTS, terms)
    if set(contract.get("primitive_roles", {})) != PRIMITIVES:
        found.append("design part list is not full")
    for name, role in contract.get("primitive_roles", {}).items():
        fields = {"role", "outcome", "motivation", "value",
                  "failure_prevented", "proof"}
        found += text_problems(role, fields, terms, f"primitive.{name}")
    return found


def actual_groups(root, catalog):
    with (root / "mise.toml").open("rb") as handle:
        data = tomllib.load(handle)
    groups = {"config": set(data) & set(catalog["groups"]["config"])}
    allowed = set(catalog["groups"]["task"])
    groups["task"] = {key for task in data["tasks"].values()
                      for key in task if key in allowed}
    groups["task_config"] = set(data.get("task_config", {}))
    groups["tool"] = {"version"} if data.get("tools") else set()
    return groups


def check_mise_primitives(contract, _, __, catalog, dispositions, tasks,
                          root=None):
    found, terms = [], contract["domain_terms"]
    if dispositions.get("catalog_version") != catalog.get("version"):
        found.append("design Mise list is old")
    actual = actual_groups(root, catalog)
    for group, names in catalog["groups"].items():
        record = dispositions.get("groups", {}).get(group, {})
        used = set(record.get("used", []))
        skipped = set(record.get("not_applicable", []))
        if used | skipped != set(names) or used & skipped:
            found.append(f"design Mise group {group} is not full")
        if used != actual[group]:
            found.append(f"design Mise group {group} does not match mise.toml")
        fields = {"used_reason", "nonuse_reason", "creative_use"}
        found += text_problems(record, fields, terms, f"mise.{group}")
    return found


def check_lifecycle(contract, lifecycle, _, __, ___, tasks, root=None):
    found, terms = [], contract["domain_terms"]
    if set(lifecycle.get("required_phases", [])) != PHASES:
        found.append("design life steps are not full")
    if set(lifecycle.get("aspects", {})) != ASPECTS:
        found.append("design life parts are not full")
    if set(lifecycle.get("primitives", {})) != PRIMITIVES:
        found.append("design file parts are not full")
    for name, profile in lifecycle.get("profiles", {}).items():
        if set(profile) != PHASES or not set(profile.values()) <= set(tasks):
            found.append(f"design life path {name} is not valid")
    for name, item in lifecycle.get("aspects", {}).items():
        found += text_problems(item, {"outcome", "motivation", "proof"},
                               terms, f"aspect.{name}")
    return found


def check_task_graph(contract, _, __, ___, ____, tasks, root=None):
    found, names = structure_problems(tasks), set(tasks)
    records = contract.get("task_graph", {}).get("tasks", {})
    if set(records) != names:
        found.append("design task records do not match mise.toml")
    for name, record in records.items():
        found += text_problems(record, TEXT_FIELDS, contract["domain_terms"],
                               f"task.{name}")
    operations = contract.get("task_graph", {}).get("public_operations", [])
    for index, operation in enumerate(operations):
        fields = {"outcome", "motivation", "why_default_path", "proof"}
        found += text_problems(operation, fields, contract["domain_terms"],
                               f"operation.{index}")
    cycle = find_cycle(tasks)
    if cycle:
        found.append("design task graph has a loop: " + " -> ".join(cycle))
    starts = [contract["task_graph"]["ci_task"]]
    starts += [item["task"] for item in operations if item.get("task") in tasks]
    return found if cycle else found + route_problems(tasks, starts)


def check_decisions(contract, _, decisions, __, ___, tasks, root=None):
    return decision_problems(decisions, contract["domain_terms"])


CHECKS = {"domain-research": check_domain_research, "use-case": check_use_case,
          "mise-primitives": check_mise_primitives,
          "primitive-lifecycle": check_lifecycle,
          "task-graph": check_task_graph, "decisions": check_decisions}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=sorted(CHECKS))
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        found = CHECKS[args.mode](*load(root), root=root)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL {error}")
        return 2
    for problem in found:
        print(f"FAIL {problem}")
    print(f"design {args.mode}: {len(found)} problems")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
