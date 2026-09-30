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
REQUIRED_TASKS = ["ci", "info", "test", "setup-graph-renderer", "render-file-graph"] + CHECK_JOBS
REQUIRED_TASKS += ["task-graph-policy", "use-case-policy",
                   "domain-research-policy", "mise-primitives-policy",
                   "primitive-lifecycle-policy", "invocation-policy",
                   "agentic-request",
                   "mise-latest", "mise-primitives-plan", "mise-primitives-update"]
CACHEABLE = ["validate", "lint-writing", "lint-code",
             "lint-placeholders", "evals", "improvement-policy"]


def load_tasks(path):
    with open(path, "rb") as handle:
        return tomllib.load(handle).get("tasks", {})


def load_config(path):
    with open(path, "rb") as handle:
        return tomllib.load(handle)


def _TestTaskGraph_setUp(self):
    self.config = load_config(SKILL_DIR / "mise.toml")
    self.tasks = self.config["tasks"]

def _TestTaskGraph_test_every_required_task_exists(self):
    for name in REQUIRED_TASKS:
        self.assertIn(name, self.tasks, f"missing task: {name}")

def _TestTaskGraph_test_ci_invokes_every_check_job(self):
    task = self.tasks["ci"]
    self.assertEqual(set(task["depends"]),
                     set(["test"] + [job for job in CHECK_JOBS if job != "lint-code"]))
    self.assertNotIn("run", task)
    self.assertEqual(self.tasks["test"]["depends"], ["setup-graph-renderer"])
    self.assertEqual(self.tasks["setup-graph-renderer"]["depends"], ["lint-code"])
    self.assertEqual(self.tasks["render-file-graph"]["depends"], ["setup-graph-renderer"])

def _TestTaskGraph_test_every_task_has_a_description(self):
    for name, task in self.tasks.items():
        self.assertTrue(task.get("description"), f"{name} needs one")

def _TestTaskGraph_test_each_check_job_runs_one_command(self):
    for job in CHECK_JOBS:
        run = self.tasks[job]["run"]
        self.assertIsInstance(run, str, f"{job} must run one command")
        self.assertIn("scripts/", run)
        self.assertNotIn("mise run", run)

def _TestTaskGraph_test_use_case_gate_waits_for_domain_research(self):
    self.assertEqual(
        self.tasks["use-case-policy"]["depends"],
        ["domain-research-policy"])

def _TestTaskGraph_test_decision_gate_waits_for_task_graph_policy(self):
    self.assertEqual(
        self.tasks["decision-policy"]["depends"],
        ["task-graph-policy"])

def _TestTaskGraph_test_task_graph_gate_waits_for_lifecycle_policy(self):
    self.assertEqual(
        self.tasks["task-graph-policy"]["depends"],
        ["primitive-lifecycle-policy"])

def _TestTaskGraph_test_domain_policy_chain_is_serial(self):
    self.assertEqual(self.tasks["mise-primitives-policy"]["depends"],
                     ["use-case-policy"])
    self.assertEqual(self.tasks["primitive-lifecycle-policy"]["depends"],
                     ["mise-primitives-policy"])

def _TestTaskGraph_test_catalog_update_follows_self_update(self):
    task = self.tasks["mise-primitives-update"]
    self.assertEqual(task["depends"], ["mise-latest"])
    self.assertEqual(task["depends_post"], ["mise-primitives-policy"])
    self.assertEqual(task["usage"], 'flag "--review <path>" required=#true')
    self.assertIn('--review "${usage_review?}"', task["run"])
    self.assertEqual(self.tasks["mise-primitives-plan"]["depends"], [])
    self.assertIn('--plan', self.tasks["mise-primitives-plan"]["run"])

def _TestTaskGraph_test_bounded_concurrency_and_safe_caching_are_enabled(self):
    self.assertTrue(self.config["settings"]["experimental"])
    self.assertGreater(self.config["settings"]["jobs"], 1)
    for name in CACHEABLE:
        task = self.tasks[name]
        self.assertTrue(task["cache"]["enabled"], name)
        self.assertTrue(task["sources"], name)
        self.assertEqual(task["outputs"], [], name)

def _TestTaskGraph_test_live_tests_are_not_cached(self):
    self.assertNotIn("cache", self.tasks["test"])


class TestTaskGraph(unittest.TestCase):
    setUp = _TestTaskGraph_setUp
    test_every_required_task_exists = _TestTaskGraph_test_every_required_task_exists
    test_ci_invokes_every_check_job = _TestTaskGraph_test_ci_invokes_every_check_job
    test_every_task_has_a_description = _TestTaskGraph_test_every_task_has_a_description
    test_each_check_job_runs_one_command = _TestTaskGraph_test_each_check_job_runs_one_command
    test_use_case_gate_waits_for_domain_research = _TestTaskGraph_test_use_case_gate_waits_for_domain_research
    test_decision_gate_waits_for_task_graph_policy = _TestTaskGraph_test_decision_gate_waits_for_task_graph_policy
    test_task_graph_gate_waits_for_lifecycle_policy = _TestTaskGraph_test_task_graph_gate_waits_for_lifecycle_policy
    test_domain_policy_chain_is_serial = _TestTaskGraph_test_domain_policy_chain_is_serial
    test_catalog_update_follows_self_update = _TestTaskGraph_test_catalog_update_follows_self_update
    test_bounded_concurrency_and_safe_caching_are_enabled = _TestTaskGraph_test_bounded_concurrency_and_safe_caching_are_enabled
    test_live_tests_are_not_cached = _TestTaskGraph_test_live_tests_are_not_cached


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
