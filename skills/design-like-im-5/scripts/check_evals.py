#!/usr/bin/env python3
"""Check the shape of skill test files and the lossless speed policy.

Each case needs a prompt, result, and checks.
Trigger tests need both yes and no cases.

Exit codes:
  0  both files pass
  1  at least one check failed
  2  usage or input error

Examples:
  python3 scripts/check_evals.py .
  python3 scripts/check_evals.py path/to/skill --min-cases 4 --min-queries 8
"""
import argparse
import json
import sys
from pathlib import Path


def nonempty(value):
    return isinstance(value, str) and value.strip()


def exact_ids(rows, expected):
    if not isinstance(rows, list):
        return False
    return {row.get("id") for row in rows if isinstance(row, dict)} == expected


def check_manifest(doc, problems):
    if not isinstance(doc, dict):
        return
    required = {
        "schema_version", "skill", "public_version", "case_source",
        "trigger_source", "contract", "rubric", "speed_budgets",
        "conditions", "repetitions", "test_classes",
    }
    if set(doc) != required:
        problems.append("manifest.json: fields do not match the eval schema")
    if doc.get("conditions") != ["with_skill", "without_skill"]:
        problems.append("manifest.json: conditions are wrong")
    if doc.get("repetitions") != 2:
        problems.append("manifest.json: repetitions must be two")


def check_speed_shape(doc, problems):
    if doc.get("objective") != "minimum_elapsed_time_to_fully_verified_result":
        problems.append("speed-policy.json: objective is wrong")
    required = {
        "proof_loss_allowed": False,
        "required_work": "all",
        "scope_loss_allowed": False,
        "workflow_action_concurrency": 1,
        "writers_per_artifact": 1,
    }
    if doc.get("invariants") != required:
        problems.append("speed-policy.json: invariants must preserve all work and proof")


def check_budgets(doc, problems):
    required = {"schema_version", "skill", "fixture", "live", "failure_rule"}
    if set(doc) != required:
        problems.append("speed-budgets.json: fields do not match the eval schema")
    if doc.get("failure_rule") != "BLOCKED":
        problems.append("speed-budgets.json: failure rule must be BLOCKED")


def check_parallel(doc, problems):
    where = "speed-policy.json"
    parallel = {"context_reads", "current_sources", "package_checks",
                "render_capture_matrix"}
    if not exact_ids(doc.get("parallel_groups"), parallel):
        problems.append(f"{where}: parallel_groups are incomplete")
    for row in doc.get("parallel_groups", []):
        if not isinstance(row, dict) or set(row) != {
                "id", "enter_when", "work", "must_wait_for", "stop_if"}:
            problems.append(f"{where}: each parallel group needs one full gate")
            break
        if not all(nonempty(row.get(key)) for key in
                   ["enter_when", "work", "stop_if"]):
            problems.append(f"{where}: parallel group text is incomplete")
            break
        if not isinstance(row.get("must_wait_for"), list) or not row["must_wait_for"]:
            problems.append(f"{where}: parallel group needs prerequisites")
            break


def check_serial(doc, problems):
    where = "speed-policy.json"
    barred = {"missing_context_judgment", "shared_writer",
              "unfrozen_inputs", "workflow_actions"}
    if not exact_ids(doc.get("never_parallelize"), barred):
        problems.append(f"{where}: never_parallelize is incomplete")
    if any(set(row) != {"id", "rule"} or not nonempty(row.get("rule"))
           for row in doc.get("never_parallelize", [])
           if isinstance(row, dict)):
        problems.append(f"{where}: each serial gate needs one rule")


def check_reuse_measure(doc, problems):
    where = "speed-policy.json"
    reuse = doc.get("reuse", {})
    if reuse.get("required_check") != "rerun_each_required_check":
        problems.append(f"{where}: every required check must rerun")
    if reuse.get("invalidation_result") != "STALE":
        problems.append(f"{where}: invalid reuse must become STALE")
    measure = doc.get("measurement", {})
    if measure.get("segments") != ["discovery", "full_load", "task", "transport"]:
        problems.append(f"{where}: timing segments are incomplete")
    if measure.get("conditions") != ["cold", "warm"]:
        problems.append(f"{where}: cold and warm timing are required")
    if measure.get("package_jobs") != 8:
        problems.append(f"{where}: package_jobs must match the measured graph")


def check_speed(doc, problems):
    if not isinstance(doc, dict):
        return
    check_speed_shape(doc, problems)
    check_parallel(doc, problems)
    check_serial(doc, problems)
    check_reuse_measure(doc, problems)


def check_case(case, index, skill, problems):
    where = f"evals.json case {index}"
    if not isinstance(case.get("id"), int):
        problems.append(f"{where}: id must be an integer")
    for key in ["prompt", "expected_output"]:
        if not nonempty(case.get(key)):
            problems.append(f"{where}: {key} must be a non-empty string")
    assertions = case.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        problems.append(f"{where}: assertions must be a non-empty list")
    elif not all(nonempty(a) for a in assertions):
        problems.append(f"{where}: every assertion must be a string")
    for name in case.get("files", []):
        if not (skill / name).is_file():
            problems.append(f"{where}: listed file missing: {name}")


def check_cases(doc, skill, minimum, problems):
    if not nonempty(doc.get("skill_name")):
        problems.append("evals.json: skill_name must be a non-empty string")
    cases = doc.get("evals")
    if not isinstance(cases, list) or len(cases) < minimum:
        problems.append(f"evals.json: needs at least {minimum} cases")
        return
    ids = [case.get("id") for case in cases]
    if len(set(ids)) != len(ids):
        problems.append("evals.json: case ids must be unique")
    for index, case in enumerate(cases, start=1):
        check_case(case, index, skill, problems)


def check_queries(queries, minimum, problems):
    if not isinstance(queries, list) or len(queries) < minimum:
        problems.append(f"trigger-queries.json: needs at least {minimum} "
                        "queries")
        return
    labels = set()
    for index, entry in enumerate(queries, start=1):
        if not isinstance(entry, dict):
            problems.append(f"trigger-queries.json entry {index}: "
                            "must be an object")
            continue
        if not nonempty(entry.get("query")):
            problems.append(f"trigger-queries.json entry {index}: "
                            "query must be a non-empty string")
        flag = entry.get("should_trigger")
        if not isinstance(flag, bool):
            problems.append(f"trigger-queries.json entry {index}: "
                            "should_trigger must be true or false")
        labels.add(flag)
    if not {True, False} <= labels:
        problems.append("trigger-queries.json: needs positive and "
                        "negative queries")


def load(path, problems):
    if not path.is_file():
        problems.append(f"missing {path.parent.name}/{path.name}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        problems.append(f"{path.name}: invalid JSON: {error}")
        return None


def check_all(skill, minimum, queries_minimum, problems):
    doc = load(skill / "evals" / "evals.json", problems)
    if doc is not None:
        check_cases(doc, skill, minimum, problems)
    queries = load(skill / "evals" / "trigger-queries.json", problems)
    if queries is not None:
        check_queries(queries, queries_minimum, problems)
    manifest = load(skill / "evals" / "manifest.json", problems)
    if manifest is not None:
        check_manifest(manifest, problems)
    budgets = load(skill / "evals" / "speed-budgets.json", problems)
    if budgets is not None:
        check_budgets(budgets, problems)
    policy = load(skill / "assets" / "speed-policy.json", problems)
    if policy is not None:
        check_speed(policy, problems)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill_dir", help="path to the skill directory")
    parser.add_argument("--min-cases", type=int, default=4)
    parser.add_argument("--min-queries", type=int, default=4)
    args = parser.parse_args(argv)
    skill = Path(args.skill_dir).resolve()
    if not skill.is_dir():
        print(f"error: no such directory: {skill}", file=sys.stderr)
        return 2
    problems = []
    check_all(skill, args.min_cases, args.min_queries, problems)
    for problem in problems:
        print(problem)
    print(f"eval checks: {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
