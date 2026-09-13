"""Contract tests for the mise task graph and the CI workflow template."""
import pathlib
import tomllib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
REQUIRED_TASKS = [
    "setup-graph-renderer", "render-file-graph", "ci", "test-ci", "test", "validate", "lint-writing",
    "lint-code", "lint-placeholders", "evals", "improvement-policy",
    "decision-policy", "task-graph-policy", "use-case-policy",
    "domain-research-policy", "mise-primitives-policy",
    "primitive-lifecycle-policy", "invocation-policy",
    "agentic-request",
    "mise-latest", "mise-primitives-plan", "mise-primitives-update",
    "doctor", "new", "resolve-scope", "variant", "validate-target", "eval-target",
    "plan-standardize", "standardize-target", "refresh-registry-lineage",
    "source-corpus", "audit-source-corpus",
    "lineage", "refresh-lineage",
]
CHECK_JOBS = ["validate", "lint-writing", "lint-code",
              "lint-placeholders", "evals", "improvement-policy",
              "decision-policy"]
DIRECT_CHECKS = [job for job in CHECK_JOBS if job != "lint-code"]
FACTORY_CI_JOBS = ["test"] + DIRECT_CHECKS + ["source-corpus", "lineage"]


def load_tasks(path):
    with open(path, "rb") as handle:
        data = tomllib.load(handle)
    return data.get("tasks", {})


check = unittest.TestCase()


def test_required_tasks_exist_testmisetaskgraph():
    tasks = load_tasks(SKILL_DIR / "mise.toml")
    for name in REQUIRED_TASKS:
        check.assertIn(name, tasks, f"missing task: {name}")

def test_ci_uses_dependency_edges_testmisetaskgraph():
    tasks = load_tasks(SKILL_DIR / "mise.toml")
    task = tasks["ci"]
    check.assertEqual(set(task["depends"]), set(FACTORY_CI_JOBS))
    check.assertNotIn("run", task)
    check.assertEqual(tasks["test"]["depends"], ["test-ci", "setup-graph-renderer"])

def test_ci_covers_every_check_job_testmisetaskgraph():
    tasks = load_tasks(SKILL_DIR / "mise.toml")
    check.assertEqual(set(tasks["ci"]["depends"]),
                     set(FACTORY_CI_JOBS))

def test_each_check_job_has_one_default_path_testmisetaskgraph():
    tasks = load_tasks(SKILL_DIR / "mise.toml")
    for job in CHECK_JOBS + ["task-graph-policy", "use-case-policy",
                             "domain-research-policy",
                             "mise-primitives-policy",
                             "primitive-lifecycle-policy"]:
        run = tasks[job]["run"]
        check.assertIsInstance(run, str, f"{job} must run one command")
        check.assertIn("scripts/", run)
        check.assertNotIn("mise run", run)

def test_policy_routes_require_changed_output_designations_testmisetaskgraph():
    tasks = load_tasks(SKILL_DIR / "mise.toml")
    for relative in ["mise.toml", "assets/mise-template.toml"]:
        task = load_tasks(SKILL_DIR / relative)["use-case-policy"]
        check.assertIn("--accept", task["run"])

def test_target_commands_stay_behind_mise_testmisetaskgraph():
    tasks = load_tasks(SKILL_DIR / "mise.toml")
    check.assertEqual(
        tasks["validate-target"]["run"],
        "uv run --no-project --isolated --no-python-downloads --with PyYAML==6.0.3 scripts/check_target.py validate")
    check.assertEqual(tasks["eval-target"]["run"],
                     "python3 scripts/check_target.py eval")

def test_standardization_plan_stays_behind_mise_testmisetaskgraph():
    tasks = load_tasks(SKILL_DIR / "mise.toml")
    run = tasks["plan-standardize"]["run"]
    check.assertEqual(run, "python3 scripts/plan_standardize.py")

def test_source_corpus_checks_stay_behind_mise_testmisetaskgraph():
    tasks = load_tasks(SKILL_DIR / "mise.toml")
    for name in ["source-corpus", "audit-source-corpus"]:
        check.assertEqual(
            tasks[name]["run"],
            "python3 scripts/check_source_corpus.py")

def test_mise_update_is_deferred_and_isolated_testmisetaskgraph():
    tasks = load_tasks(SKILL_DIR / "mise.toml")
    task = tasks["mise-latest"]
    check.assertEqual(task["depends"], [])
    check.assertEqual(task["run"],
                     "mise self-update --yes --no-plugins")
    check.assertNotIn("mise-latest", tasks["ci"]["depends"])
    update = tasks["mise-primitives-update"]
    check.assertEqual(update["depends"], ["mise-latest"])
    check.assertEqual(update["depends_post"], [{"task": "refresh-lineage", "args": ["--review", "{{usage.lineage_review}}"]}])
    check.assertEqual(update["run"],
                     'python3 scripts/sync_mise_primitives.py . --review "${usage_catalog_review?}"')
    plan = tasks["mise-primitives-plan"]
    check.assertEqual(plan["depends"], [])
    check.assertIn("--plan", plan["run"])
    check.assertIn("--catalog-review", update["usage"])
    check.assertIn("--lineage-review", update["usage"])

def test_template_exists_in_assets_testworkflowtemplate():
    path = SKILL_DIR / "assets/ci/ci.yml"
    text = path.read_text(encoding="utf-8")
    check.assertTrue(path.is_file())

def test_workflow_runs_only_mise_run_ci_testworkflowtemplate():
    path = SKILL_DIR / "assets/ci/ci.yml"
    text = path.read_text(encoding="utf-8")
    run_lines = [
        line.strip() for line in text.splitlines()
        if line.strip().startswith("- run:")
    ]
    check.assertEqual(run_lines, ["- run: mise run ci"])

def test_workflow_installs_mise_testworkflowtemplate():
    path = SKILL_DIR / "assets/ci/ci.yml"
    text = path.read_text(encoding="utf-8")
    check.assertIn("jdx/mise-action", text)

def test_workflow_triggers_on_push_and_pull_request_testworkflowtemplate():
    path = SKILL_DIR / "assets/ci/ci.yml"
    text = path.read_text(encoding="utf-8")
    check.assertIn("push:", text)
    check.assertIn("pull_request:", text)

def test_template_has_single_ci_entrypoint_testgeneratedskilltemplate():
    tasks = load_tasks(SKILL_DIR / "assets/mise-template.toml")
    task = tasks["ci"]
    check.assertEqual(set(task["depends"]), set(["test"] + DIRECT_CHECKS))
    check.assertNotIn("run", task)

def test_template_jobs_match_factory_jobs_testgeneratedskilltemplate():
    tasks = load_tasks(SKILL_DIR / "assets/mise-template.toml")
    for job in ["info", "test", "domain-research-policy",
                "mise-primitives-policy", "primitive-lifecycle-policy",
                "task-graph-policy", "invocation-policy",
                "agentic-request",
                "mise-latest", "mise-primitives-plan", "mise-primitives-update"] + CHECK_JOBS:
        check.assertIn(job, tasks)

def test_template_defers_latest_stable_mise_testgeneratedskilltemplate():
    tasks = load_tasks(SKILL_DIR / "assets/mise-template.toml")
    task = tasks["mise-latest"]
    check.assertEqual(task["depends"], [])
    check.assertEqual(task["run"],
                     "mise self-update --yes --no-plugins")

def test_use_case_gate_depends_on_domain_research_testgeneratedskilltemplate():
    tasks = load_tasks(SKILL_DIR / "assets/mise-template.toml")
    check.assertEqual(
        tasks["use-case-policy"]["depends"],
        ["domain-research-policy"])

def test_decision_gate_depends_on_task_graph_policy_testgeneratedskilltemplate():
    tasks = load_tasks(SKILL_DIR / "assets/mise-template.toml")
    check.assertEqual(
        tasks["decision-policy"]["depends"],
        ["task-graph-policy"])

def test_task_graph_gate_depends_on_use_case_policy_testgeneratedskilltemplate():
    tasks = load_tasks(SKILL_DIR / "assets/mise-template.toml")
    check.assertEqual(
        tasks["task-graph-policy"]["depends"],
        ["primitive-lifecycle-policy"])

def test_lifecycle_and_primitive_gates_are_serial_testgeneratedskilltemplate():
    tasks = load_tasks(SKILL_DIR / "assets/mise-template.toml")
    check.assertEqual(tasks["mise-primitives-policy"]["depends"],
                     ["use-case-policy"])
    check.assertEqual(tasks["primitive-lifecycle-policy"]["depends"],
                     ["mise-primitives-policy"])

def test_generated_catalog_update_follows_self_update_testgeneratedskilltemplate():
    tasks = load_tasks(SKILL_DIR / "assets/mise-template.toml")
    update = tasks["mise-primitives-update"]
    check.assertEqual(update["depends"], ["mise-latest"])
    check.assertEqual(update["depends_post"], ["mise-primitives-policy"])
    check.assertEqual(update["usage"], 'flag "--review <path>" required=#true')
    check.assertIn('--review "${usage_review?}"', update["run"])
    check.assertEqual(tasks["mise-primitives-plan"]["depends"], [])


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(unittest.FunctionTestCase(value) for name, value in globals().items()
                              if name.startswith('test_') and callable(value))


if __name__ == '__main__':
    unittest.main()
