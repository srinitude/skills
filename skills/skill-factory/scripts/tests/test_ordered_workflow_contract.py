"""Require an explicit ordered workflow in factory and generated skill bodies."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
OWNERS = [ROOT / "SKILL.md", ROOT / "assets" / "skill-template.md"]
ORDERED_CONCEPTS = ["outcome", "domain", "Mise", "RED", "GREEN",
                    "proof", "receipt", "maintenance"]
CONTROL_FLOW = ["Branch:", "If:", "For each:", "Repeat:", "Stop:"]


def workflow(text):
    start = text.index("## Ordered workflow")
    tail = text[start:].split("\n## ", 1)[0]
    return tail


def steps(section):
    return re.findall(r"(?ms)^(\d+)\. (.*?)(?=^\d+\. |\Z)", section)


def assert_mise_tasks(test, section):
    for number, body in steps(section):
        if "Mise:" in body:
            test.assertIn("`mise run", body,
                          f"step {number} does not invoke a task")


class TestOrderedWorkflowContract(unittest.TestCase):
    def test_factory_and_generated_body_have_numbered_workflow(self):
        for path in OWNERS:
            with self.subTest(path=path.name):
                section = workflow(path.read_text(encoding="utf-8"))
                numbers = [int(value) for value in re.findall(r"(?m)^(\d+)\. ",
                                                               section)]
                self.assertGreaterEqual(len(numbers), 8)
                self.assertEqual(numbers, list(range(1, len(numbers) + 1)))

    def test_every_step_names_mise_or_model_work(self):
        for path in OWNERS:
            with self.subTest(path=path.name):
                section = workflow(path.read_text(encoding="utf-8"))
                for number, body in steps(section):
                    self.assertTrue("Mise:" in body or "Model:" in body,
                                    f"step {number} has no execution owner")
                self.assertIn("Mise:", section)
                self.assertIn("Model:", section)

    def test_every_mise_owner_invokes_a_task(self):
        for path in OWNERS:
            with self.subTest(path=path.name):
                section = workflow(path.read_text(encoding="utf-8"))
                assert_mise_tasks(self, section)

    def test_workflow_keeps_the_full_acceptance_order(self):
        for path in OWNERS:
            with self.subTest(path=path.name):
                section = workflow(path.read_text(encoding="utf-8"))
                positions = [section.index(concept) for concept in ORDERED_CONCEPTS]
                self.assertEqual(positions, sorted(positions))

    def test_workflow_has_plain_control_flow(self):
        for path in OWNERS:
            with self.subTest(path=path.name):
                section = workflow(path.read_text(encoding="utf-8"))
                for marker in CONTROL_FLOW:
                    self.assertIn(marker, section)


if __name__ == "__main__":
    unittest.main()
