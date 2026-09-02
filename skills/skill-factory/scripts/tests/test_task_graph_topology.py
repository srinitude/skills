"""Behavior tests for the complete skill-factory Mise dependency graph."""
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CI_JOBS = ["test", "validate", "lint-writing", "lint-code",
           "lint-placeholders", "evals", "improvement-policy",
           "decision-policy", "source-corpus", "lineage"]
ACCEPTANCE_JOBS = [job for job in CI_JOBS if job != "lineage"]
EXPECTED = {
    "ci": CI_JOBS,
    "test-ci": [],
    "test": ["test-ci"],
    "validate": [],
    "lint-writing": [],
    "lint-code": [],
    "lint-placeholders": [],
    "evals": [],
    "improvement-policy": [],
    "use-case-policy": ["domain-research-policy"],
    "mise-primitives-policy": ["use-case-policy"],
    "primitive-lifecycle-policy": ["mise-primitives-policy"],
    "task-graph-policy": ["primitive-lifecycle-policy"],
    "domain-research-policy": [],
    "decision-policy": ["task-graph-policy"],
    "invocation-policy": [],
    "agentic-request": [],
    "mise-latest": [],
    "mise-primitives-update": ["mise-latest"],
    "source-corpus": [],
    "lineage": [],
    "refresh-lineage": ACCEPTANCE_JOBS,
    "audit-source-corpus": ["doctor", "source-corpus"],
    "doctor": [],
    "new": ["doctor"],
    "validate-target": ["doctor"],
    "eval-target": ["doctor"],
    "plan-standardize": ["doctor", "source-corpus"],
}


def tasks():
    with (ROOT / "mise.toml").open("rb") as handle:
        return tomllib.load(handle)["tasks"]


class TestTaskGraphTopology(unittest.TestCase):
    def setUp(self):
        self.tasks = tasks()

    def test_every_task_has_an_explicit_dependency_set(self):
        self.assertEqual(set(self.tasks), set(EXPECTED))
        for name, expected in EXPECTED.items():
            self.assertEqual(self.tasks[name].get("depends"), expected, name)

    def test_dependencies_resolve_to_declared_tasks(self):
        declared = set(self.tasks)
        for name, task in self.tasks.items():
            self.assertTrue(set(task["depends"]) <= declared, name)

    def test_catalog_update_runs_primitive_policy_after_refresh(self):
        self.assertEqual(self.tasks["mise-primitives-update"]["depends_post"],
                         ["refresh-lineage"])

    def test_run_commands_do_not_reinvoke_mise(self):
        for name, task in self.tasks.items():
            self.assertNotIn("mise run", task.get("run", ""), name)

    def test_refresh_lineage_waits_for_every_acceptance_gate(self):
        self.assertEqual(self.tasks["refresh-lineage"]["depends"],
                         ACCEPTANCE_JOBS)


if __name__ == "__main__":
    unittest.main()
