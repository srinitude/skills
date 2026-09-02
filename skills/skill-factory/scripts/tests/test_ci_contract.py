"""Contract tests for the mise task graph and the CI workflow template."""
import pathlib
import tomllib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
REQUIRED_TASKS = [
    "ci", "test-ci", "test", "validate", "lint-writing",
    "lint-code", "lint-placeholders", "evals", "improvement-policy",
    "decision-policy", "task-graph-policy", "use-case-policy",
    "domain-research-policy", "mise-primitives-policy",
    "primitive-lifecycle-policy", "invocation-policy",
    "agentic-request",
    "mise-latest", "mise-primitives-update",
    "doctor", "new", "validate-target", "eval-target",
    "plan-standardize", "standardize-target", "refresh-registry-lineage",
    "source-corpus", "audit-source-corpus",
    "lineage", "refresh-lineage",
]
CHECK_JOBS = ["validate", "lint-writing", "lint-code",
              "lint-placeholders", "evals", "improvement-policy",
              "decision-policy"]
FACTORY_CI_JOBS = ["test"] + CHECK_JOBS + ["source-corpus", "lineage"]


def load_tasks(path):
    with open(path, "rb") as handle:
        data = tomllib.load(handle)
    return data.get("tasks", {})


class TestMiseTaskGraph(unittest.TestCase):
    def setUp(self):
        self.tasks = load_tasks(SKILL_DIR / "mise.toml")

    def test_required_tasks_exist(self):
        for name in REQUIRED_TASKS:
            self.assertIn(name, self.tasks, f"missing task: {name}")

    def test_ci_uses_dependency_edges(self):
        task = self.tasks["ci"]
        self.assertEqual(set(task["depends"]), set(FACTORY_CI_JOBS))
        self.assertNotIn("run", task)
        self.assertEqual(self.tasks["test"]["depends"], ["test-ci"])

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
                         "python3 scripts/check_target.py eval")

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
        self.assertEqual(set(task["depends"]), set(["test"] + CHECK_JOBS))
        self.assertNotIn("run", task)

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
