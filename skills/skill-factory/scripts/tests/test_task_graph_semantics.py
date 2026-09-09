"""Check explicit task topology beyond a plain dependency-name array."""
import tempfile
import tomllib
import unittest
import sys
from pathlib import Path

from cli import SCRIPTS, run
from test_task_graph_policy import TASK_FILE, write_skill
sys.path.insert(0, str(SCRIPTS))
from mise_text import value


def check(changes):
    tasks = tomllib.loads(TASK_FILE)["tasks"]
    for name, fields in changes.items():
        tasks[name].update(fields)
    graph = "\n".join(f'[tasks.{value(name)}]\n' + "\n".join(
        f"{value(key)} = {value(item)}" for key, item in task.items())
        for name, task in tasks.items())
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        write_skill(root, graph)
        return run("check_task_graph.py", root)


class TestTaskGraphSemantics(unittest.TestCase):
    def test_structured_dependency_retains_a_real_edge(self):
        result = check({"ci": {"depends": [{"task": "test", "args": ["a b", ""],
                                            "env": {"ZONE": "UTC"}}, "decision-policy"]}})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_wait_for_cannot_schedule_an_orphan(self):
        result = check({"ci": {"depends": ["decision-policy"], "wait_for": ["test"]}})
        self.assertEqual(result.returncode, 1)
        self.assertIn("no public operation reaches test", result.stdout)

    def test_wait_for_cycle_among_scheduled_tasks_is_rejected(self):
        result = check({"test": {"wait_for": ["decision-policy"]},
                        "decision-policy": {"wait_for": ["test"]}})
        self.assertEqual(result.returncode, 1)
        self.assertIn("cycle", result.stdout)

    def test_post_order_is_not_a_prerequisite_edge(self):
        result = check({"info": {"depends_post": ["invocation-policy"]},
                        "invocation-policy": {"wait_for": ["info"]}})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        blocked = check({"info": {"depends_post": ["invocation-policy"],
                                   "wait_for": ["invocation-policy"]}})
        self.assertEqual(blocked.returncode, 1)
        self.assertIn("cycle", blocked.stdout)

    def test_run_entries_have_dependency_guards(self):
        allowed = check({"ci": {"depends": ["decision-policy"],
                                 "run": [{"task": "test", "args": ["a b"]}]}})
        self.assertEqual(allowed.returncode, 0, allowed.stdout + allowed.stderr)
        for entry, message in [("missing", "unknown dependencies"),
                               ("ci", "cycle"), ("use-case-policy", "multiple dependency paths")]:
            with self.subTest(entry=entry):
                rejected = check({"ci": {"run": [{"tasks": [entry]}]}})
                self.assertEqual(rejected.returncode, 1)
                self.assertIn(message, rejected.stdout)

    def test_windows_cannot_hide_a_recursive_mise_call(self):
        result = check({"test": {"run_windows": "mise run ci"}})
        self.assertEqual(result.returncode, 1)
        self.assertIn("must not invoke Mise", result.stdout)

    def test_platform_alternatives_are_not_duplicate_calls(self):
        result = check({"ci": {"depends": ["decision-policy"],
                                "run": [{"task": "test"}], "run_windows": [{"task": "test"}]}})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_invalid_dependency_is_a_validation_failure(self):
        for item in [2, {}, {"task": ["test"]}, ["test", 2], {"task": "test", "optional": "yes"}]:
            with self.subTest(item=item):
                result = check({"ci": {"depends": [item]}})
                self.assertEqual(result.returncode, 1)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
