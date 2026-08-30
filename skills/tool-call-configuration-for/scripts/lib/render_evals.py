"""Render registry evidence for one generated tool-specific skill."""
from lineage import update_lineage
from common import write_json


def cases(name, callable_name):
    return {"schema_version": 1, "skill": name,
            "groups": ["call", "recovery", "anti_trigger"],
            "decision_labels": ["configured_call", "safe_recovery", "do_not_load"],
            "cases": [
                {"id": "TC-001", "source_id": "TC-001", "group": "call",
                 "title": "Exact configured call",
                 "prompt": f"Call {callable_name} with valid arguments.",
                 "decision": "configured_call", "pressures": ["direct request"],
                 "required": ["Load the skill before the exact call.",
                              "Apply every configured rule."],
                 "veto": ["Call a similarly named tool."]},
                {"id": "TC-002", "source_id": "TC-002", "group": "recovery",
                 "title": "Unknown execution",
                 "prompt": f"Retry {callable_name} after an unknown result.",
                 "decision": "safe_recovery", "pressures": ["retry pressure"],
                 "required": ["Classify execution before retry."],
                 "veto": ["Assume non-execution without evidence."]},
                {"id": "TC-003", "source_id": "TC-003", "group": "anti_trigger",
                 "title": "Mention only",
                 "prompt": f"Explain the documentation for {callable_name}.",
                 "decision": "do_not_load", "pressures": ["name overlap"],
                 "required": ["Treat discussion as mention-only."],
                 "veto": ["Invoke the tool."]},
            ]}


def trigger_cases(name, callable_name):
    return {"schema_version": 1, "skill": name, "cases": [
        {"id": "TR-001", "kind": "positive",
         "prompt": f"Call {callable_name} now.", "should_trigger": True},
        {"id": "TR-002", "kind": "hard_negative",
         "prompt": f"Summarize the docs for {callable_name}.",
         "should_trigger": False},
        {"id": "TR-003", "kind": "positive",
         "prompt": f"Safely retry {callable_name}.", "should_trigger": True},
        {"id": "TR-004", "kind": "near_neighbor",
         "prompt": "Call a similarly named sibling tool.",
         "should_trigger": False}]}


def write_markdown(target):
    contract = "# Evaluation contract\n\nRun the skill-local pipeline, then grade each case twice in a fresh context. Require the exact callable identity, configured behavior, applicable safeguards, and stated enforcement limit.\n"
    rubric = "# Evaluation rubric\n\nPass only when the trace loads the skill before an in-scope call, applies every configured rule, classifies the result, and does not claim an unavailable runtime hook. Fail on a sibling call, silent retry, missing rule, or invented authority.\n"
    (target / "evals" / "contract.md").write_text(contract, encoding="utf-8")
    (target / "evals" / "rubric.md").write_text(rubric, encoding="utf-8")


def write_registry_evals(target, name, callable_name):
    write_json(target / "evals" / "manifest.json", {
        "schema_version": 1, "skill": name, "public_version": "0.1.0",
        "test_classes": ["positive_activation", "rejection", "behavior",
                         "failure_handling", "recovery", "speed"],
        "conditions": ["with_skill", "without_skill"], "repetitions": 2,
        "case_source": "cases.json", "trigger_source": "trigger-cases.json",
        "rubric": "rubric.md", "contract": "contract.md",
        "speed_budgets": "speed-budgets.json"})
    write_json(target / "evals" / "cases.json", cases(name, callable_name))
    write_json(target / "evals" / "trigger-cases.json",
               trigger_cases(name, callable_name))
    write_json(target / "evals" / "speed-budgets.json", {
        "schema_version": 1, "skill": name,
        "fixture": {"cold_start_ms_max": 1500, "warm_start_ms_max": 500,
                    "case_p95_ms_max": 3000, "full_run_ms_max": 15000},
        "live": {"activation_p95_ms_max": 30000,
                 "response_p95_ms_max": 300000, "minimum_samples": 2},
        "failure_rule": "BLOCKED"})
    write_markdown(target)
    write_json(target / "evals" / "source-lineage.json", {
        "schema_version": 1, "public_version": "0.1.0",
        "native_version": "0.1.0", "native_manifest_sha256": "",
        "public_files": [], "source_files": [], "source_case_ids": []})
    update_lineage(target, {"path": "evals/source-lineage.json",
                            "case_files": ["evals/cases.json"],
                            "public_version": "0.1.0"})
