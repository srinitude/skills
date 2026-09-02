#!/usr/bin/env python3
"""Validate one design-system run ledger.

Exit codes:
  0  record passes
  1  record has contract problems
  2  file or usage error
"""

import argparse
import json
import sys
from pathlib import Path

from lib.integrated_validation import check_integrated
from lib.comparison_validation import check_controlled_comparisons

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "assets" / "run-contract.json"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def require_equal(record, contract, key, problems):
    if record.get(key) != contract[key]:
        problems.append(f"{key} must equal the canonical contract")


def check_sources(record, contract, problems):
    sources = record.get("sources")
    if not isinstance(sources, list) or not sources:
        problems.append("sources must contain at least one source")
        return
    allowed = set(contract["source_types"])
    for index, source in enumerate(sources):
        if source.get("type") not in allowed:
            problems.append(f"sources[{index}].type is unsupported")
        if not source.get("location"):
            problems.append(f"sources[{index}].location is required")


def check_stages(record, contract, problems):
    stages = record.get("stages", [])
    ids = [stage.get("id") for stage in stages if isinstance(stage, dict)]
    if ids != contract["stage_order"]:
        problems.append("stages must follow stage_order exactly")
    allowed = set(contract["stage_states"])
    for index, stage in enumerate(stages):
        if stage.get("status") not in allowed:
            problems.append(f"stages[{index}].status is invalid")
        if stage.get("status") == "pass" and not stage.get("proof"):
            problems.append(f"stages[{index}] needs current stage proof")
        if stage.get("status") == "not_applicable":
            if not stage.get("reason") or not stage.get("proof"):
                problems.append(f"stages[{index}] needs not-applicable proof")


def check_capabilities(record, contract, problems):
    allowed = set(contract["capability_dispositions"])
    items = record.get("capabilities", [])
    for index, item in enumerate(items):
        if not item.get("role"):
            problems.append(f"capabilities[{index}].role is required")
        disposition = item.get("disposition")
        if disposition not in allowed:
            problems.append(f"capabilities[{index}].disposition is invalid")
        if disposition in {"not_applicable", "blocked"} and not item.get("reason"):
            problems.append(f"capabilities[{index}].reason is required")
    if record.get("completion") == "pass":
        final = {"use", "not_applicable"}
        if not items or any(item.get("disposition") not in final for item in items):
            problems.append("completion pass needs resolved capability proof")


def check_mutations(record, contract, problems):
    allowed = set(contract["mutation_effects"])
    permission = {"repository_write": "repository_write", "figma_write": "figma_write",
                  "metadata_publish": "publish", "metadata_unpublish": "unpublish",
                  "delete": "delete"}
    for index, item in enumerate(record.get("mutations", [])):
        where = f"mutations[{index}]"
        if item.get("effect") not in allowed:
            problems.append(f"{where}.effect is invalid")
        if item.get("status") == "executed":
            if not item.get("target"):
                problems.append(f"{where}.target is required")
            if not item.get("authorization_id"):
                problems.append(f"{where}.authorization_id is required")
            if not item.get("readback"):
                problems.append(f"{where}.readback is required")
            key = permission.get(item.get("effect"))
            if not key or record.get("permissions", {}).get(key) != "granted":
                problems.append(f"{where} needs matching permission")


def lineage_index(nodes, problems):
    index = {}
    for position, node in enumerate(nodes):
        node_id = node.get("id")
        if not node_id or node_id in index:
            problems.append(f"lineage[{position}].id must be unique")
        else:
            index[node_id] = node
    return index


def visit(node_id, index, active, done, problems):
    if node_id in active:
        problems.append(f"lineage cycle reaches {node_id}")
        return
    if node_id in done or node_id not in index:
        return
    active.add(node_id)
    for dependency in index[node_id].get("depends_on", []):
        visit(dependency, index, active, done, problems)
    active.remove(node_id)
    done.add(node_id)


def check_lineage(record, contract, problems):
    nodes = record.get("lineage", [])
    index = lineage_index(nodes, problems)
    levels = {name: i for i, name in enumerate(contract["hierarchy"])}
    for node in nodes:
        check_lineage_node(node, index, levels, problems)
    done = set()
    for node_id in index:
        visit(node_id, index, set(), done, problems)


def check_lineage_node(node, index, levels, problems):
    node_id = node.get("id", "<missing>")
    if node.get("level") not in levels:
        problems.append(f"lineage {node_id} has invalid level")
    if node.get("status") not in {"planned", "pass", "stale", "blocked"}:
        problems.append(f"lineage {node_id} has invalid status")
    if node.get("status") == "pass" and not node.get("proof"):
        problems.append(f"lineage {node_id} needs current lineage proof")
    for dependency in node.get("depends_on", []):
        if dependency not in index:
            problems.append(f"lineage {node_id} misses dependency {dependency}")
            continue
        own_level = levels.get(node.get("level"), -1)
        dependency_level = levels.get(index[dependency].get("level"), -1)
        if dependency_level >= own_level:
            problems.append(f"lineage {node_id} must depend on a lower layer")
        if index[dependency].get("status") == "stale" and node.get("status") == "pass":
            problems.append(f"lineage {node_id} passes with stale dependency {dependency}")


def validate(record, contract):
    problems = []
    if record.get("mode") not in contract["modes"]:
        problems.append("mode must be create or update")
    require_equal(record, contract, "hierarchy", problems)
    require_equal(record, contract, "template_kinds", problems)
    check_sources(record, contract, problems)
    check_stages(record, contract, problems)
    check_capabilities(record, contract, problems)
    check_mutations(record, contract, problems)
    check_lineage(record, contract, problems)
    check_controlled_comparisons(record, contract, problems)
    check_integrated(record, contract, problems)
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", help="path to run JSON")
    args = parser.parse_args(argv)
    try:
        record = load_json(Path(args.record))
        contract = load_json(CONTRACT)
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    problems = validate(record, contract)
    for problem in problems:
        print(problem)
    print(f"run validation: {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
