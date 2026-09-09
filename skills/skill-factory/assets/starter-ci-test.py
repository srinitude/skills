"""Contract tests that pin this skill's task graph and CI workflow.

Each test names the contract it pins:
  1. every task the pipeline needs exists in mise.toml
  2. the ci task depends on every check job
  3. every task carries a description a reader can act on
  4. the CI workflow runs the same single command as a local run
"""
import pathlib
import tomllib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
CHECK_JOBS = ["validate", "lint-writing", "lint-code",
              "lint-placeholders", "evals", "improvement-policy",
              "decision-policy"]
REQUIRED_TASKS = ["ci", "info", "test"] + CHECK_JOBS
REQUIRED_TASKS += ["task-graph-policy", "use-case-policy",
                   "domain-research-policy", "mise-primitives-policy",
                   "primitive-lifecycle-policy", "invocation-policy",
                   "agentic-request",
                   "mise-latest", "mise-primitives-update"]
CACHEABLE = ["validate", "lint-writing", "lint-code",
             "lint-placeholders", "evals", "improvement-policy"]


def load_tasks(path):
    with open(path, "rb") as handle:
        return tomllib.load(handle).get("tasks", {})


def load_config(path):
    with open(path, "rb") as handle:
        return tomllib.load(handle)


class TestTaskGraph(unittest.TestCase):
    def setUp(self):
        self.config = load_config(SKILL_DIR / "mise.toml")
        self.tasks = self.config["tasks"]

    def test_every_required_task_exists(self):
        for name in REQUIRED_TASKS:
            self.assertIn(name, self.tasks, f"missing task: {name}")

    def test_ci_invokes_every_check_job(self):
        task = self.tasks["ci"]
        self.assertEqual(set(task["depends"]),
                         set(["test"] + CHECK_JOBS))
        self.assertNotIn("run", task)

    def test_every_task_has_a_description(self):
        for name, task in self.tasks.items():
            self.assertTrue(task.get("description"), f"{name} needs one")

    def test_each_check_job_runs_one_command(self):
        for job in CHECK_JOBS:
            run = self.tasks[job]["run"]
            self.assertIsInstance(run, str, f"{job} must run one command")
            self.assertIn("scripts/", run)
            self.assertNotIn("mise run", run)

    def test_use_case_gate_waits_for_domain_research(self):
        self.assertEqual(
            self.tasks["use-case-policy"]["depends"],
            ["domain-research-policy"])

    def test_decision_gate_waits_for_task_graph_policy(self):
        self.assertEqual(
            self.tasks["decision-policy"]["depends"],
            ["task-graph-policy"])

    def test_task_graph_gate_waits_for_lifecycle_policy(self):
        self.assertEqual(
            self.tasks["task-graph-policy"]["depends"],
            ["primitive-lifecycle-policy"])

    def test_domain_policy_chain_is_serial(self):
        self.assertEqual(self.tasks["mise-primitives-policy"]["depends"],
                         ["use-case-policy"])
        self.assertEqual(self.tasks["primitive-lifecycle-policy"]["depends"],
                         ["mise-primitives-policy"])

    def test_catalog_update_follows_self_update(self):
        task = self.tasks["mise-primitives-update"]
        self.assertEqual(task["depends"], ["mise-latest"])
        self.assertEqual(task["depends_post"], ["mise-primitives-policy"])

    def test_bounded_concurrency_and_safe_caching_are_enabled(self):
        self.assertTrue(self.config["settings"]["experimental"])
        self.assertGreater(self.config["settings"]["jobs"], 1)
        for name in CACHEABLE:
            task = self.tasks[name]
            self.assertTrue(task["cache"]["enabled"], name)
            self.assertTrue(task["sources"], name)
            self.assertEqual(task["outputs"], [], name)

    def test_live_tests_are_not_cached(self):
        self.assertNotIn("cache", self.tasks["test"])


class TestWorkflow(unittest.TestCase):
    def setUp(self):
        path = SKILL_DIR / ".github" / "workflows" / "ci.yml"
        self.assertTrue(path.is_file(), "missing .github/workflows/ci.yml")
        self.text = path.read_text(encoding="utf-8")

    def test_workflow_runs_only_the_single_entry_point(self):
        run_lines = [line.strip() for line in self.text.splitlines()
                     if line.strip().startswith("- run:")]
        self.assertEqual(run_lines, ["- run: mise run ci"])

    def test_workflow_triggers_on_push_and_pull_request(self):
        self.assertIn("push:", self.text)
        self.assertIn("pull_request:", self.text)


if __name__ == "__main__":
    unittest.main()
