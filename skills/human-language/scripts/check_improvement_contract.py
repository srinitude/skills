#!/usr/bin/env python3
"""Validate the optional skill-improvement policy.

Usage:
  python3 scripts/check_improvement_contract.py [skill-root]

Exit codes:
  0  contract passes
  1  contract is missing or invalid
  2  bad usage

Example:
  python3 scripts/check_improvement_contract.py .
"""
import argparse
import json
import sys
from pathlib import Path

REQUIRED_DIMENSIONS = {
    "correctness", "wall_clock_time", "deterministic_coverage",
    "task_success", "safety", "portability", "token_efficiency",
    "creative_range", "experimental_range", "exploratory_range",
    "semantic_judgment", "maintainability", "simplicity",
    "plain_language", "current_skill_contract",
}
REQUIRED_EVIDENCE = {
    "baseline_content_digest", "candidate_content_digest",
    "named_dimension", "frozen_evaluator_digest", "environment_receipt",
    "baseline_results", "candidate_results", "protected_dimension_results",
    "elapsed_seconds", "applicable_resource_results",
    "not_applicable_resource_reasons", "status",
    "restoration_receipt_when_rejected",
}
RESOURCE_GROUPS = {
    "time", "cpu", "memory", "storage", "network", "cache", "context",
    "process", "concurrency", "accelerator", "cost", "human_attention",
}


def load_contract(root):
    path = root / "assets" / "improvement-contract.json"
    if not path.is_file():
        raise ValueError(f"missing {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON: {error}") from error


def problems(data):
    found = []
    expected = {
        "mode": "optional_final_step", "cli_owner": "mise",
        "acceptance": "pareto_non_regression",
        "failure": "restore_last_accepted_version",
    }
    for key, value in expected.items():
        if data.get(key) != value:
            found.append(f"{key} must equal {value}")
    if data.get("trial", {}).get("change") != "one_named_dimension":
        found.append("trial.change must equal one_named_dimension")
    if data.get("resource_policy") != "measure_or_justify_not_applicable":
        found.append("resource_policy must require case-by-case disposition")
    if not RESOURCE_GROUPS <= set(data.get("resource_catalog", {})):
        found.append("resource_catalog is incomplete")
    if not data.get("baseline", {}).get("freeze_before_trial"):
        found.append("baseline must be frozen before the trial")
    evaluator = data.get("evaluator", {})
    for key in ["freeze_before_trial", "same_inputs", "same_environment",
                "same_time_budget", "repeat_when_noisy"]:
        if not evaluator.get(key):
            found.append(f"evaluator.{key} must be true")
    if not REQUIRED_DIMENSIONS <= set(data.get("protected_dimensions", [])):
        found.append("protected_dimensions are incomplete")
    if not REQUIRED_EVIDENCE <= set(data.get("required_evidence", [])):
        found.append("required_evidence is incomplete")
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill_root", nargs="?", default=".")
    args = parser.parse_args(argv)
    try:
        data = load_contract(Path(args.skill_root).resolve())
    except ValueError as error:
        print(f"FAIL {error}")
        return 1
    found = problems(data)
    for problem in found:
        print(f"FAIL {problem}")
    print(f"improvement contract: {len(found)} problems")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
