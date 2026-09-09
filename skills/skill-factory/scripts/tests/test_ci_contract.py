"""Contract tests for the mise task graph and the CI workflow template."""
import pathlib
import json
import tomllib
import unittest

from cli import run

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
REQUIRED_TASKS = [
    "ci", "test-ci", "test", "validate", "lint-writing",
    "lint-code", "lint-placeholders", "evals", "improvement-policy",
    "decision-policy", "task-graph-policy", "use-case-policy",
    "domain-research-policy", "mise-primitives-policy",
    "primitive-lifecycle-policy", "invocation-policy",
    "agentic-request",
    "mise-latest", "mise-primitives-update",
    "doctor", "new", "resolve-scope", "variant", "validate-target", "eval-target",
    "plan-standardize", "standardize-target", "refresh-registry-lineage",
    "source-corpus", "audit-source-corpus",
    "lineage", "refresh-lineage",
]
CHECK_JOBS = ["validate", "lint-writing", "lint-code",
              "lint-placeholders", "evals", "improvement-policy",
              "decision-policy"]
FACTORY_CI_JOBS = ["test"] + [job for job in CHECK_JOBS if job != "lint-code"] + ["source-corpus", "lineage"]


def load_tasks(path):
    with open(path, "rb") as handle:
        data = tomllib.load(handle)
    tasks = data.get("tasks", {})
    for task in tasks.values():
        for field in ["depends", "depends_post"]:
            if field in task:
                task[field] = [item["task"] if isinstance(item, dict) else item for item in task[field]]
    return tasks


class TestMiseTaskGraph(unittest.TestCase):
    def setUp(self):
        self.tasks = load_tasks(SKILL_DIR / "mise.toml")

    def test_required_tasks_exist(self):
        for name in REQUIRED_TASKS:
            self.assertIn(name, self.tasks, f"missing task: {name}")

    def test_native_workflow_has_pinned_tools_and_an_ordered_check_path(self):
        config = tomllib.loads((SKILL_DIR / "mise.toml").read_text())
        self.assertEqual(config["tools"]["node"], "24.18.0")
        self.assertEqual(config["tools"]["python"], "3.13.14")
        self.assertEqual(config["tools"]["uv"], "0.11.29")
        package = json.loads((SKILL_DIR / "package.json").read_text())
        self.assertEqual(package["dependencies"]["@mastra/core"], "1.64.0")
        self.assertEqual(package["dependencies"]["@mastra/libsql"], "1.22.3")
        self.assertEqual(package["packageManager"], "npm@11.16.0")
        self.assertEqual(self.tasks["test-ci"]["depends"], ["runtime-install"])
        self.assertEqual(self.tasks["lint-code"]["depends"], ["test-ci"])
        self.assertEqual(self.tasks["typecheck-native"]["depends"], ["lint-code"])
        self.assertEqual(self.tasks["test-native"]["depends"], ["typecheck-native"])
        self.assertIn("test-native", self.tasks["test"]["depends"])
        self.assertNotIn("lint-code", self.tasks["ci"]["depends"])
        self.assertIn("--ignore-scripts", self.tasks["runtime-install"]["run"])
        self.assertIn("scripts/workflow.ts", self.tasks["workflow"]["run"])

    def test_workflow_cli_exposes_domain_operation_and_external_acceptance(self):
        import subprocess
        result = subprocess.run(["node", str(SKILL_DIR / "scripts/workflow.ts"), "--help"],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        for flag in ["start", "resume", "reject", "--source", "--profile", "--candidate",
                     "--state-dir", "--run-id", "--acceptance-context", "--receipt-sha256"]:
            self.assertIn(flag, result.stdout)

    def test_source_coverage_uses_the_existing_public_policy_route(self):
        self.assertIn("check_use_case_contract.py", self.tasks["use-case-policy"]["run"])
        result = run("check_use_case_contract.py", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for flag in ["--source", "--coverage", "--source-sha256", "--coverage-sha256"]:
            self.assertIn(flag, result.stdout)

    def test_acceptance_stays_at_the_existing_invocation_owner(self):
        self.assertIn("check_invocation_receipt.py", self.tasks["invocation-policy"]["run"])
        result = run("check_invocation_receipt.py", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for flag in ["--acceptance-context", "--context-sha256", "--receipt-sha256"]:
            self.assertIn(flag, result.stdout)

    def test_audience_uses_current_authoring_and_validation_routes(self):
        for script in ["scaffold_skill.py", "standardize_registry_skill.py"]:
            result = run(script, "--help")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("--audience", result.stdout)
        self.assertIn("--inspect-legacy", run("check_use_case_contract.py", "--help").stdout)

    def test_mutating_consumers_take_external_acceptance_bindings(self):
        for command in [("scaffold_skill.py",), ("standardize_registry_skill.py",),
                        ("skill_variant.py", "accept"), ("check_target.py",)]:
            result = run(*command, "--help")
            self.assertEqual(result.returncode, 0, result.stderr)
            for flag in ["--acceptance-context", "--context-sha256", "--receipt", "--receipt-sha256"]:
                self.assertIn(flag, result.stdout)

    def test_ci_uses_dependency_edges(self):
        task = self.tasks["ci"]
        self.assertEqual(set(task["depends"]), set(FACTORY_CI_JOBS))
        self.assertNotIn("run", task)
        self.assertEqual(self.tasks["test"]["depends"], ["test-native"])

    def test_ci_covers_every_check_job(self):
        self.assertEqual(set(self.tasks["ci"]["depends"]),
                         set(FACTORY_CI_JOBS))

    def test_each_check_job_has_one_default_path(self):
        for job in CHECK_JOBS + ["task-graph-policy", "use-case-policy",
                                 "domain-research-policy",
                                 "mise-primitives-policy",
                                 "primitive-lifecycle-policy"]:
            run = self.tasks[job]["run"]
            self.assertIsInstance(run, str, f"{job} must run one command")
            self.assertIn("scripts/", run)
            self.assertNotIn("mise run", run)

    def test_target_commands_stay_behind_mise(self):
        self.assertEqual(
            self.tasks["validate-target"]["run"],
            "uv run --with PyYAML==6.0.3 scripts/check_target.py validate")
        self.assertEqual(self.tasks["eval-target"]["run"],
                         "uv run --with PyYAML==6.0.3 scripts/check_target.py eval")

    def test_standardization_plan_stays_behind_mise(self):
        run = self.tasks["plan-standardize"]["run"]
        self.assertEqual(run, "python3 scripts/plan_standardize.py")

    def test_source_corpus_checks_stay_behind_mise(self):
        for name in ["source-corpus", "audit-source-corpus"]:
            self.assertEqual(
                self.tasks[name]["run"],
                "python3 scripts/check_source_corpus.py")

    def test_mise_update_is_deferred_and_isolated(self):
        task = self.tasks["mise-latest"]
        self.assertEqual(task["depends"], [])
        self.assertEqual(task["run"],
                         "mise self-update --yes --no-plugins")
        self.assertNotIn("mise-latest", self.tasks["ci"]["depends"])
        update = self.tasks["mise-primitives-update"]
        self.assertEqual(update["depends"], ["mise-latest"])
        self.assertEqual(update["depends_post"], ["refresh-lineage"])
        self.assertEqual(update["run"],
                         "python3 scripts/sync_mise_primitives.py .")


class TestWorkflowTemplate(unittest.TestCase):
    def setUp(self):
        self.path = SKILL_DIR / "assets" / "ci" / "ci.yml"
        self.text = self.path.read_text(encoding="utf-8")

    def test_template_exists_in_assets(self):
        self.assertTrue(self.path.is_file())

    def test_workflow_runs_only_mise_run_ci(self):
        run_lines = [
            line.strip() for line in self.text.splitlines()
            if line.strip().startswith("- run:")
        ]
        self.assertEqual(run_lines, ["- run: mise run ci"])

    def test_workflow_installs_mise(self):
        self.assertIn("jdx/mise-action", self.text)

    def test_workflow_triggers_on_push_and_pull_request(self):
        self.assertIn("push:", self.text)
        self.assertIn("pull_request:", self.text)


class TestGeneratedSkillTemplate(unittest.TestCase):
    def setUp(self):
        path = SKILL_DIR / "assets" / "mise-template.toml"
        self.tasks = load_tasks(path)

    def test_template_has_single_ci_entrypoint(self):
        task = self.tasks["ci"]
        self.assertEqual(set(task["depends"]), set(FACTORY_CI_JOBS) - {"source-corpus", "lineage"})
        self.assertNotIn("run", task)

    def test_template_native_gates_form_one_prerequisite_path(self):
        self.assertEqual(self.tasks["lint-code"]["depends"], ["runtime-install"])
        self.assertEqual(self.tasks["typecheck-native"]["depends"], ["lint-code"])
        self.assertEqual(self.tasks["test-native"]["depends"], ["typecheck-native"])
        self.assertEqual(self.tasks["test"]["depends"], ["test-native"])
        self.assertIn("--ignore-scripts", self.tasks["runtime-install"]["run"])

    def test_template_jobs_match_factory_jobs(self):
        for job in ["info", "test", "domain-research-policy",
                    "mise-primitives-policy", "primitive-lifecycle-policy",
                    "task-graph-policy", "invocation-policy",
                    "agentic-request",
                    "mise-latest", "mise-primitives-update"] + CHECK_JOBS:
            self.assertIn(job, self.tasks)

    def test_template_defers_latest_stable_mise(self):
        task = self.tasks["mise-latest"]
        self.assertEqual(task["depends"], [])
        self.assertEqual(task["run"],
                         "mise self-update --yes --no-plugins")

    def test_use_case_gate_depends_on_domain_research(self):
        self.assertEqual(
            self.tasks["use-case-policy"]["depends"],
            ["domain-research-policy"])

    def test_decision_gate_depends_on_task_graph_policy(self):
        self.assertEqual(
            self.tasks["decision-policy"]["depends"],
            ["task-graph-policy"])

    def test_task_graph_gate_depends_on_use_case_policy(self):
        self.assertEqual(
            self.tasks["task-graph-policy"]["depends"],
            ["primitive-lifecycle-policy"])

    def test_lifecycle_and_primitive_gates_are_serial(self):
        self.assertEqual(self.tasks["mise-primitives-policy"]["depends"],
                         ["use-case-policy"])
        self.assertEqual(self.tasks["primitive-lifecycle-policy"]["depends"],
                         ["mise-primitives-policy"])

    def test_generated_catalog_update_follows_self_update(self):
        update = self.tasks["mise-primitives-update"]
        self.assertEqual(update["depends"], ["mise-latest"])
        self.assertEqual(update["depends_post"], ["mise-primitives-policy"])


if __name__ == "__main__":
    unittest.main()
