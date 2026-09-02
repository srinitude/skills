"""Behavior tests for one acyclic default Mise dependency path."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run

TASK_NAMES = ["ci", "test", "domain-research-policy", "use-case-policy",
              "task-graph-policy", "decision-policy", "info",
              "invocation-policy"]


def operation(task):
    return {
        "task": task,
        "outcome": f"Release notes {task} produces one checked result.",
        "motivation": f"Release notes need one {task} entry path.",
        "why_default_path": f"Git history makes {task} reproducible.",
        "proof": f"Release notes {task} exits with a receipt.",
    }


def task_policy(task):
    return {
        "outcome": f"Release notes {task} advances the accepted result.",
        "motivation": f"Release notes need {task} on its default path.",
        "value": f"Git history evidence makes {task} useful progress.",
        "proof": f"Release notes {task} produces a checked receipt.",
        "applicability": f"Run {task} when release notes use its output.",
    }


def contract():
    return {
        "skill": "release-notes",
        "domain_terms": ["release notes", "git history", "change audience"],
        "task_graph": {
            "ci_task": "ci",
            "public_operations": [operation("info"),
                                  operation("invocation-policy")],
            "tasks": {name: task_policy(name) for name in TASK_NAMES},
        },
    }


TASK_FILE = """[tasks.ci]
description = "Release notes acceptance"
depends = ["test", "decision-policy"]
[tasks.test]
description = "Release notes tests"
depends = []
run = "python3 scripts/tests.py"
[tasks.domain-research-policy]
description = "Release notes research"
depends = []
run = "python3 scripts/research.py"
[tasks.use-case-policy]
description = "Release notes use case"
depends = ["domain-research-policy"]
run = "python3 scripts/use_case.py"
[tasks.task-graph-policy]
description = "Release notes task graph"
depends = ["use-case-policy"]
run = "python3 scripts/task_graph.py"
[tasks.decision-policy]
description = "Release notes decisions"
depends = ["task-graph-policy"]
run = "python3 scripts/decisions.py"
[tasks.info]
description = "Release notes information"
depends = []
run = "python3 scripts/info.py"
[tasks.invocation-policy]
description = "Release notes invocation receipt"
depends = []
run = "python3 scripts/invocation.py"
"""


def task_text(extra=""):
    return TASK_FILE + extra


def write_skill(root, graph=None, data=None):
    (root / "assets").mkdir()
    (root / "mise.toml").write_text(graph or task_text(), encoding="utf-8")
    payload = data or contract()
    (root / "assets/use-case-contract.json").write_text(
        json.dumps(payload), encoding="utf-8")


class TestTaskGraphPolicy(unittest.TestCase):
    def check(self, graph=None, data=None):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, graph, data)
            return run("check_task_graph.py", root)

    def test_acyclic_single_path_graph_passes(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_cycle_fails(self):
        graph = task_text().replace("depends = []\nrun = \"python3 scripts/tests.py\"",
                                    "depends = [\"ci\"]\nrun = \"python3 scripts/tests.py\"")
        result = self.check(graph)
        self.assertEqual(result.returncode, 1)
        self.assertIn("cycle", result.stdout)

    def test_post_dependency_cycle_fails(self):
        graph = task_text().replace(
            'depends = []\nrun = "python3 scripts/tests.py"',
            'depends = []\ndepends_post = ["ci"]\nrun = "python3 scripts/tests.py"')
        result = self.check(graph)
        self.assertEqual(result.returncode, 1)
        self.assertIn("cycle", result.stdout)

    def test_unknown_post_dependency_fails(self):
        graph = task_text().replace(
            'depends = []\nrun = "python3 scripts/tests.py"',
            'depends = []\ndepends_post = ["missing"]\nrun = "python3 scripts/tests.py"')
        result = self.check(graph)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown dependencies", result.stdout)

    def test_alternate_dependency_path_fails(self):
        graph = task_text().replace(
            'depends = ["test", "decision-policy"]',
            'depends = ["test", "decision-policy", "use-case-policy"]')
        result = self.check(graph)
        self.assertEqual(result.returncode, 1)
        self.assertIn("multiple dependency paths", result.stdout)

    def test_disconnected_task_fails(self):
        extra = "\n[tasks.orphan]\ndescription = \"Release notes orphan\"\ndepends = []\n"
        result = self.check(task_text(extra))
        self.assertEqual(result.returncode, 1)
        self.assertIn("no public operation reaches orphan", result.stdout)

    def test_public_operation_must_be_domain_specific(self):
        data = contract()
        data["task_graph"]["public_operations"][0]["motivation"] = "Useful."
        result = self.check(data=data)
        self.assertEqual(result.returncode, 1)
        self.assertIn("motivation", result.stdout)

    def test_every_task_needs_a_domain_specific_value_record(self):
        data = contract()
        data["task_graph"]["tasks"]["test"]["value"] = "Runs checks."
        result = self.check(data=data)
        self.assertEqual(result.returncode, 1)
        self.assertIn("tasks.test.value", result.stdout)

    def test_task_records_must_match_mise_tasks(self):
        data = contract()
        del data["task_graph"]["tasks"]["info"]
        result = self.check(data=data)
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing task records: info", result.stdout)

    def test_domain_term_must_not_match_inside_an_unrelated_word(self):
        data = contract()
        data["domain_terms"] = ["git"]
        data["task_graph"]["tasks"]["test"]["value"] = "Digital output exists."
        result = self.check(data=data)
        self.assertEqual(result.returncode, 1)
        self.assertIn("tasks.test.value", result.stdout)

    def test_domain_label_cannot_decorate_generic_task_scaffold(self):
        data = contract()
        record = data["task_graph"]["tasks"]["test"]
        record["outcome"] = (
            "The release notes operation advances or proves its named package state.")
        record["value"] = (
            "The release notes operation produces objective progress or a bounded failure.")
        record["proof"] = (
            "The release notes task exits with current parseable evidence.")
        result = self.check(data=data)
        self.assertEqual(result.returncode, 1)
        self.assertIn("generic scaffold language", result.stdout)


if __name__ == "__main__":
    unittest.main()
