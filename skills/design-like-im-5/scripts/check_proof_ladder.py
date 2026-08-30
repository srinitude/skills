#!/usr/bin/env python3
"""Check the proof ladder and its small tests.

Exit codes:
  0  all proof rules passed
  1  a proof rule failed
  2  a path or JSON file was bad

Example:
  python3 scripts/check_proof_ladder.py .
"""
import argparse
import itertools
import json
import sys
from pathlib import Path

RUNG_IDS = [
    "atomic", "mutation", "metamorphic", "judgment_pilot", "combinatorial",
    "representative", "whole_skill",
]
RUNG_FIELDS = {
    "id", "owner", "proves", "does_not_prove", "advance_when", "evidence",
    "mise_task", "support",
}
AGREEMENT = [
    "action_order", "context_accounting", "evidence_classes", "vetoes",
    "status",
]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def text_list(value):
    return (isinstance(value, list) and bool(value)
            and all(isinstance(item, str) and item.strip() for item in value))


def check_packet(doc, issues):
    packet = doc.get("packet_contract", {})
    fields = packet.get("required_fields", [])
    required = {"goal", "current_inputs", "required_paths", "fixed_constraints",
                "required_evidence", "success_rule", "output_schema",
                "stop_conditions", "worked_example", "failure_example"}
    if set(fields) != required:
        issues.append("packet_contract: required_fields are incomplete")
    expected = {"one_action_per_packet": True, "missing_field_result": "BLOCKED",
                "mechanical_owner": "mise", "judgment_owner": "judgment"}
    for key, value in expected.items():
        if packet.get(key) != value:
            issues.append(f"packet_contract: {key} is wrong")


def check_repeatability(doc, issues):
    row = doc.get("repeatability", {})
    if row.get("runs") != 2 or not row.get("clean_context"):
        issues.append("repeatability: two clean runs are required")
    if not row.get("same_fixture") or row.get("compare") != AGREEMENT:
        issues.append("repeatability: fixed comparison fields are wrong")
    allowed = set(row.get("allowed_variation", []))
    if allowed != {"wording", "option_count_above_minimum", "creative_direction"}:
        issues.append("repeatability: allowed variation is wrong")
    if row.get("disagreement_status") != "STALE":
        issues.append("repeatability: disagreement must be STALE")


def check_rung(root, rung, issues):
    name = rung.get("id", "missing")
    if set(rung) != RUNG_FIELDS:
        issues.append(f"{name}: rung fields are wrong")
    for key in ["proves", "does_not_prove", "evidence", "support"]:
        if not text_list(rung.get(key)):
            issues.append(f"{name}: {key} must be a non-empty text list")
    for key in ["owner", "advance_when", "mise_task"]:
        if not isinstance(rung.get(key), str) or not rung[key].strip():
            issues.append(f"{name}: {key} is missing")
    for path in rung.get("support", []):
        if not (root / path).is_file():
            issues.append(f"{name}: missing support path: {path}")


def check_rungs(root, doc, issues):
    rows = doc.get("rungs", [])
    if [row.get("id") for row in rows] != RUNG_IDS:
        issues.append("rung order does not match the fixed ladder")
    for rung in rows:
        check_rung(root, rung, issues)
    if len(rows) > 3 and rows[3].get("owner") != "judgment":
        issues.append("judgment_pilot: judgment must own the review")


def check_case(root, case, issues):
    name = case.get("id", "missing")
    fields = ["fixture", "expected_detection", "claim_scope", "blocked_claim",
              "expansion_trigger", "review_records", "agreement_fields"]
    for key in fields:
        if not case.get(key):
            issues.append(f"{name}: {key} is missing")
    if not text_list(case.get("fault_seed")) or len(case["fault_seed"]) != 1:
        issues.append(f"{name}: fault_seed must name one fault")
    if case.get("repeatability_runs") != 2:
        issues.append(f"{name}: repeatability_runs must be two")
    if case.get("agreement_fields") != AGREEMENT:
        issues.append(f"{name}: agreement_fields are wrong")
    path = str(case.get("fixture", "")).split("#", 1)[0]
    if not path or not (root / path).is_file():
        issues.append(f"{name}: fixture path is missing")


def pairwise_issues(coverage):
    dims = coverage.get("dimensions", [])
    rows = coverage.get("rows", [])
    values = {item.get("id"): item.get("values") for item in dims}
    issues = []
    row_values = [tuple(row.get("values", {}).get(dim) for dim in values)
                  for row in rows]
    if len(row_values) != len(set(row_values)):
        issues.append("pairwise rows must be unique")
    for left, right in itertools.combinations(values, 2):
        expected = set(itertools.product(values[left], values[right]))
        found = {(row.get("values", {}).get(left),
                  row.get("values", {}).get(right)) for row in rows}
        if expected - found:
            issues.append(f"pairwise coverage is missing: {left} x {right}")
    return issues


def check_pilots(root, doc, issues):
    cases = doc.get("cases", [])
    if len(cases) < 5:
        issues.append("pilot-cases: at least five cases are required")
    ids = [case.get("id") for case in cases]
    if len(ids) != len(set(ids)):
        issues.append("pilot-cases: case ids must be unique")
    for case in cases:
        check_case(root, case, issues)
    coverage = doc.get("coverage", {})
    if coverage.get("strength") != 2:
        issues.append("pairwise coverage strength must be two")
    issues.extend(pairwise_issues(coverage))


def check(root):
    issues = []
    ladder = load(root / "assets" / "proof-ladder.json")
    pilots = load(root / "evals" / "pilot-cases.json")
    if ladder.get("checked_date") != "2026-08-30":
        issues.append("proof ladder checked_date is wrong")
    check_packet(ladder, issues)
    check_repeatability(ladder, issues)
    check_rungs(root, ladder, issues)
    check_pilots(root, pilots, issues)
    return issues


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", nargs="?", default=".")
    args = parser.parse_args(argv)
    root = Path(args.skill_dir).resolve()
    if not root.is_dir():
        print(f"error: no such skill folder: {root}", file=sys.stderr)
        return 2
    try:
        issues = check(root)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"error: proof ladder could not be read: {error}", file=sys.stderr)
        return 2
    for issue in issues:
        print(issue)
    print(f"proof ladder: {len(issues)} problems")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
