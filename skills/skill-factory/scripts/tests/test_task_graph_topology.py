"""Behavior tests for the complete skill-factory Mise dependency graph."""
import json
import tomllib
import unittest
import test_task_graph_policy as policy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CI_JOBS = ["test", "validate", "lint-writing",
           "lint-placeholders", "evals", "improvement-policy",
           "decision-policy", "source-corpus", "lineage"]
ACCEPTANCE_JOBS = [job for job in CI_JOBS if job != "lineage"]
EXPECTED = {
    "ci": CI_JOBS,
    "test-ci": [],
    "test": ["test-ci", "lint-code"],
    "validate": [],
    "lint-writing": [],
    "setup-runtime": [],
    "check-runtime": ["setup-runtime"],
    "ledger": ["check-runtime"],
    "lint-code": ["check-runtime"],
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
    "mise-primitives-plan": [],
    "mise-primitives-update": ["mise-latest"],
    "source-corpus": [],
    "lineage": [],
    "refresh-lineage": ACCEPTANCE_JOBS,
    "audit-source-corpus": ["doctor", "source-corpus"],
    "doctor": [],
    "new": ["doctor"],
    "resolve-scope": ["doctor"],
    "variant": ["doctor", "check-runtime"],
    "validate-target": ["doctor", "check-runtime"],
    "eval-target": ["doctor"],
    "plan-standardize": ["doctor", "source-corpus"],
    "standardization-usage": [],
    "standardize-target": ["doctor", "source-corpus", "check-runtime"],
    "refresh-registry-lineage": ["doctor", "check-runtime"],
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

    def test_deep_dependencies_accept_valid_graph_and_reject_cycle_without_recursion(self):
        data = policy.contract()
        graph = policy.task_text().replace('depends = ["test", "decision-policy"]',
                                   'depends = ["test", "decision-policy", "deep-1499"]', 1)
        for n in reversed(range(1500)):
            name = f'deep-{n}'
            prior = [f'deep-{n-1}'] if n else []
            graph += f'\n[tasks.{name}]\ndescription = "Release notes prerequisite"\ndepends = {json.dumps(prior)}\n'
            data['task_graph']['tasks'][name] = policy.task_policy(name)
        for cyclic in [False, True]:
            with self.subTest(cyclic=cyclic):
                selected = graph.replace('[tasks.deep-0]\ndescription = "Release notes prerequisite"\ndepends = []',
                                         '[tasks.deep-0]\ndescription = "Release notes prerequisite"\ndepends = ["deep-1499"]') if cyclic else graph
                result = policy.TestTaskGraphPolicy().check(selected, data)
                self.assertEqual(result.returncode, 1 if cyclic else 0, result.stderr)
                self.assertNotIn('Traceback', result.stderr)
                self.assertIn('cycle' if cyclic else '0 problems', result.stdout)

    def test_dependencies_resolve_to_declared_tasks(self):
        declared = set(self.tasks)
        for name, task in self.tasks.items():
            self.assertTrue(set(task["depends"]) <= declared, name)

    def test_catalog_update_runs_primitive_policy_after_refresh(self):
        self.assertEqual(self.tasks["mise-primitives-update"]["depends_post"],
                         [{"task": "refresh-lineage", "args": ["--review", "{{usage.lineage_review}}"]}])

    def test_run_commands_do_not_reinvoke_mise(self):
        for name, task in self.tasks.items():
            self.assertNotIn("mise run", task.get("run", ""), name)

    def test_refresh_lineage_waits_for_every_acceptance_gate(self):
        self.assertEqual(self.tasks["refresh-lineage"]["depends"],
                         ACCEPTANCE_JOBS)
        task = self.tasks["refresh-lineage"]
        self.assertEqual(task["usage"], 'flag "--review <path>" required=#true')
        self.assertIn('--review "${usage_review?}"', task["run"])


if __name__ == "__main__":
    unittest.main()
