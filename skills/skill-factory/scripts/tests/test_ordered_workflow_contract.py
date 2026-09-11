"""Guard the factory/template document structure, not semantic or runtime acceptance."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
OWNERS = [ROOT / "SKILL.md", ROOT / "assets" / "skill-template.md"]
SECTIONS = ["Outcome", "Motivation", "Evidence", "Mise task graph",
            "Steps", "Assets", "Evals"]
LEDGER_ANCHORS = {
    "SKILL.md": ["Read this complete body first.",
                 "The ledger must retain every governing rule and source detail",
                 "Relationships have stable IDs, typed directed endpoints",
                 "Discover prerequisites backward from the promised outcome"],
    "skill-template.md": ["**Start here.**", "**Reusable ledger artifact, owned here.**",
                          "**Relationship records.**", "**Dependency contract.**"],
}


def section(text, name):
    match = re.search(rf"(?ms)^## {re.escape(name)}\n(.*?)(?=^## |\Z)", text)
    return match.group(1) if match else ""


def steps(text):
    return re.findall(r"(?ms)^(\d+)\. (.*?)(?=^\d+\. |\Z)", text)


class TestOrderedWorkflowContract(unittest.TestCase):
    def test_intent_evidence_execution_and_acceptance_have_the_required_order(self):
        for path in OWNERS:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(re.findall(r"(?m)^## (.+)$", text), SECTIONS)

    def test_steps_are_one_numbered_workflow_without_a_competing_copy(self):
        for path in OWNERS:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                workflow = steps(section(text, "Steps"))
                numbers = [int(number) for number, _ in workflow]
                self.assertTrue(numbers, "the Steps section has no workflow")
                self.assertEqual(numbers, list(range(1, len(numbers) + 1)))
                self.assertEqual(len(steps(text)), len(workflow),
                                 "numbered work exists outside its owning section")

    def test_steps_name_the_reader_or_execution_owner_and_public_tasks(self):
        for path in OWNERS:
            with self.subTest(path=path.name):
                workflow = section(path.read_text(encoding="utf-8"), "Steps")
                for number, body in steps(workflow):
                    self.assertRegex(body, r"^\*\*[^*]+\*\* (?:Model(?: and \[Mise\]\[mise\])?:|Mise:|Mastra:|Human:|Host:|\[Mastra\]\[mastra\] executes)",
                                     f"step {number} has no named owner")
                    self.assertTrue("Mise:" not in body or "`mise run" in body,
                                    f"step {number} names no public task")
                self.assertIn("`mise run", workflow)

    def test_the_reusable_ledger_has_one_body_owner_before_its_consumers(self):
        for path in OWNERS:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                positions = []
                for anchor in LEDGER_ANCHORS[path.name]:
                    self.assertEqual(text.count(anchor), 1, anchor)
                    positions.append(text.index(anchor))
                self.assertEqual(positions, sorted(positions))
                self.assertLess(positions[-1], text.index("1. **"))

    def test_outer_and_inner_owners_do_not_compete(self):
        for path in OWNERS:
            with self.subTest(path=path.name):
                graph = section(path.read_text(encoding="utf-8"), "Mise task graph")
                if path.name == "SKILL.md":
                    self.assertIn("[Mise][mise] owns public commands", graph)
                    self.assertIn("[Mastra][mastra] owns substantive domain control", graph)
                    self.assertIn("Existing tested scripts perform repeatable leaves", graph)
                    self.assertIn("with explicit handoffs", graph)
                    self.assertIn("Never add competing recursive [Mise][mise] graphs", graph)
                else:
                    self.assertIn("Mise invokes Mastra once at an explicit boundary", graph)
                    self.assertIn("Mastra directly invokes existing scripts or authorized runners", graph)
                self.assertNotIn("Mise owns every deterministic command", graph)


if __name__ == "__main__":
    unittest.main()
