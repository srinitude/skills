#!/usr/bin/env python3
"""Check the safe design change rule."""
import argparse
import json
import sys
from pathlib import Path

REQUIRED_DIMENSIONS = {
    "correctness", "wall_clock_time", "deterministic_coverage", "task_success",
    "safety", "portability", "token_efficiency", "creative_range",
    "experimental_range", "exploratory_range", "semantic_judgment",
    "visual_judgment", "maintainability", "simplicity", "plain_language",
    "current_skill_contract",
}
REQUIRED_EVIDENCE = {
    "baseline_content_digest", "candidate_content_digest", "named_dimension",
    "frozen_evaluator_digest", "environment_receipt", "baseline_results",
    "candidate_results", "protected_dimension_results", "elapsed_seconds",
    "applicable_resource_results", "not_applicable_resource_reasons", "status",
    "restoration_receipt_when_rejected",
}
RESOURCE_GROUPS = {
    "time", "cpu", "memory", "storage", "network", "cache", "context",
    "process", "concurrency", "accelerator", "cost", "human_attention",
}


def load_contract(root):
    path = root / "assets/improvement-contract.json"
    if not path.is_file():
        raise ValueError(f"missing {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def problems(data):
    found = []
    expected = {"mode": "optional_final_step", "cli_owner": "mise",
                "acceptance": "pareto_non_regression",
                "failure": "restore_last_accepted_version"}
    for key, value in expected.items():
        if data.get(key) != value:
            found.append(f"{key} must equal {value}")
    if data.get("trial", {}).get("change") != "one_named_dimension":
        found.append("trial.change must name one part")
    if data.get("resource_policy") != "measure_or_justify_not_applicable":
        found.append("each run must check its resource use")
    if not RESOURCE_GROUPS <= set(data.get("resource_catalog", {})):
        found.append("design resource list is not full")
    if not data.get("baseline", {}).get("freeze_before_trial"):
        found.append("save the passed design before the test")
    evaluator = data.get("evaluator", {})
    for key in ["freeze_before_trial", "same_inputs", "same_environment",
                "same_time_budget", "repeat_when_noisy"]:
        if not evaluator.get(key):
            found.append(f"evaluator.{key} must be on")
    if not REQUIRED_DIMENSIONS <= set(data.get("protected_dimensions", [])):
        found.append("safe design parts are not full")
    if not REQUIRED_EVIDENCE <= set(data.get("required_evidence", [])):
        found.append("design proof fields are not full")
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_root", nargs="?", default=".")
    args = parser.parse_args(argv)
    try:
        found = problems(load_contract(Path(args.skill_root).resolve()))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL {error}")
        return 2
    for problem in found:
        print(f"FAIL {problem}")
    print(f"safe design change rule: {len(found)} problems")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
