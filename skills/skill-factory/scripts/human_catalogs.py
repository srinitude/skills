"""Resolve complete captured inventories and a bound matrix before returning data.

Exit codes: 0 returns resolved data, 1 rejects a source or contract, 2 is bad usage.
Example public route:
  mise run human-matrix -- --resources bindings.json --concepts '["icatus-2016/741"]'
"""
import sys

if __name__ == "__main__" and not sys.flags.isolated:
    import os
    os.execv(sys.executable, [sys.executable, "-I", "-B", __file__, *sys.argv[1:]])

import argparse
import graphlib
import hashlib
import importlib.util
import json
from pathlib import Path


def load_support():
    for name in ["skill_package", "source_coverage", "invocation_acceptance", "human_catalog_sources",
                 "human_pdf_catalogs", "human_matrix_records", "human_matrix_budget", "human_combinations", "human_matrix"]:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)


if sys.flags.isolated:
    load_support()

from human_catalog_sources import icatus, isco, onet
from human_pdf_catalogs import nist, oecd
from skill_package import inventory, tree_digest
from source_coverage import bound_bytes, load_json, parse_json, require
from human_matrix_budget import arguments, check, emit, start

ROOT = Path(__file__).resolve().parents[1]
PARSERS = {"oecd-ford-2015": oecd, "isco-08": isco, "icatus-2016": icatus,
           "onet-31.0": onet, "nist-ai-200-1-2024": nist}


def captured_bytes(identifier, spec, binding, base):
    require(isinstance(binding, dict) and set(binding) == {"path", "sha256"}, "invalid resource binding")
    require(binding["sha256"] == spec["sha256"], "declared source changed: " + identifier)
    require(isinstance(binding["path"], str) and binding["path"], "resource needs an explicit path")
    path = Path(binding["path"])
    path = path if path.is_absolute() else base / path
    require(path.stat().st_size == spec["bytes"], "captured source changed: " + identifier)
    return bound_bytes(path, spec["sha256"], "captured source " + identifier)


def catalog(identifier, spec, raw):
    records = PARSERS[identifier](raw)
    ids = [item["native_id"] for item in records]
    require(len(ids) == len(set(ids)) == spec["concepts"], "complete inventory differs: " + identifier)
    parents = {item["native_id"]: item["broader"] for item in records}
    require(all(parent in parents for values in parents.values() for parent in values), "missing concept parent")
    require(sum(not values for values in parents.values()) == spec["roots"], "catalog root coverage differs")
    graphlib.TopologicalSorter(parents).prepare()
    for item in records:
        require(isinstance(item["label"], str) and item["label"].strip(), "empty concept label")
        require(item["definition"] is None or isinstance(item["definition"], str), "invalid source definition")
        item["id"] = identifier + "/" + item["native_id"]
        item["broader"] = [identifier + "/" + parent for parent in item["broader"]]
        item["definition_status"] = "provided" if item["definition"] else "not-supplied"
        item["aliases"] = []
    digest = hashlib.sha256(json.dumps(records, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    summary = {"concepts": len(records), "roots": spec["roots"],
               "missing_definitions": sum(not item["definition"] for item in records),
               "inventory_sha256": digest, "source_sha256": spec["sha256"],
               "source_version": spec["version"], "url": spec["url"], "license": spec["license"],
               "scope": spec["scope"], "attribution": spec["attribution"]}
    return summary, {item["id"]: item for item in records}


def resolve(path, budget=None):
    registry_path = ROOT / "assets/human-catalogs.json"
    registry, bindings = load_json(registry_path), load_json(path)
    require(isinstance(bindings, dict) and type(bindings.get("version")) is int
            and bindings["version"] == 1, "invalid resource binding version")
    resources = bindings.get("resources")
    require(isinstance(resources, dict) and set(resources) == set(registry["catalogs"]) == set(PARSERS),
            "complete declared inventory resource bindings are required")
    summaries, concepts = {}, {}
    for identifier, spec in registry["catalogs"].items():
        raw = captured_bytes(identifier, spec, resources[identifier], Path(path).resolve().parent)
        summary, records = catalog(identifier, spec, raw)
        summaries[identifier] = summary
        concepts.update(records)
        check(budget)
    result = {"implementation": tree_digest(inventory(ROOT)),
              "registry_sha256": hashlib.sha256(registry_path.read_bytes()).hexdigest(), "catalogs": summaries}
    return result, concepts


def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["inspect", "select", "matrix"])
    parser.add_argument("--resources", required=True)
    parser.add_argument("--concepts")
    parser.add_argument("--matrix")
    parser.add_argument("--matrix-sha256")
    arguments(parser)
    return parser.parse_args()


def main():
    args = parse_arguments()
    try:
        budget = start(args)
        result, concepts = resolve(args.resources, budget)
        if args.operation == "matrix":
            from human_matrix import inspect
            require(bool(args.matrix) and bool(args.matrix_sha256), "matrix and digest are required")
            result = inspect(args.matrix, args.matrix_sha256, result, concepts)
            if args.enumerate:
                from human_combinations import enumerate_space
                result["enumeration"] = enumerate_space(result, args.enumerate, budget)
        if args.operation == "select":
            selected = parse_json(args.concepts.encode() if args.concepts else b"null")
            require(isinstance(selected, list) and all(isinstance(item, str) for item in selected), "concepts must be an ordered array of identifiers")
            require(all(item in concepts for item in selected), "unknown concept; resolve an explicit extension before selection")
            result.update(selected=[concepts[item] for item in selected], acceptance="pending")
        emit(result, budget)
        return 0
    except (OSError, ValueError, KeyError, TypeError, graphlib.CycleError) as error:
        print("FAIL " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
