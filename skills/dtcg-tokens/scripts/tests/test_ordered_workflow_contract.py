"""Require an executable ordered workflow in the DTCG skill body."""
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]


def workflow_steps():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    parts = text.split("## Ordered workflow\n", 1)
    body = parts[1].split("\n## ", 1)[0] if len(parts) == 2 else ""
    return [line for line in body.splitlines() if re.match(r"^\d+\. ", line)]


class OrderedWorkflowTests(unittest.TestCase):
    def test_workflow_has_consecutive_steps(self):
        steps = workflow_steps()
        self.assertGreaterEqual(len(steps), 8)
        numbers = [int(re.match(r"^(\d+)\.", step).group(1)) for step in steps]
        self.assertEqual(numbers, list(range(1, len(steps) + 1)))

    def test_each_step_has_a_real_owner(self):
        for step in workflow_steps():
            self.assertTrue("Mise:" in step or "Model:" in step, step)
            if "Mise:" in step:
                self.assertIn("mise run", step, step)

    def test_control_flow_changes_execution(self):
        joined = "\n".join(workflow_steps())
        for marker in ["Branch:", "If:", "For each:", "Repeat:", "Stop:"]:
            self.assertIn(marker, joined)
        for concept in ["source", "experiment", "lock", "author", "proof"]:
            self.assertIn(concept, joined.lower())


if __name__ == "__main__":
    unittest.main()
