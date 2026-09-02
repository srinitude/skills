"""Test skill rules."""
import json
import re
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUIRED = {
    "assets/improvement-contract.json", "assets/use-case-contract.json",
    "assets/decision-records.json", "assets/invocation-receipt-template.json",
    "assets/mise-primitives.json", "assets/mise-primitives-catalog.json",
    "assets/primitive-lifecycle.json", "references/resource-and-experiment-design.md",
    "references/use-case-specificity.md",
}
POLICY_TASKS = {
    "improvement-policy", "domain-research-policy", "use-case-policy",
    "mise-primitives-policy", "primitive-lifecycle-policy",
    "task-graph-policy", "decision-policy", "invocation-policy",
    "agentic-request",
}


class FactoryUpdateContractTests(unittest.TestCase):
    def test_factory_owners_exist(self):
        missing = sorted(path for path in REQUIRED if not (ROOT / path).is_file())
        self.assertEqual(missing, [])

    def test_factory_policy_tasks_exist(self):
        with (ROOT / "mise.toml").open("rb") as handle:
            tasks = tomllib.load(handle).get("tasks", {})
        self.assertEqual(sorted(POLICY_TASKS - set(tasks)), [])

    def test_body_has_owned_ordered_workflow(self):
        body = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        section = body.split("## Ordered workflow", 1)[1]
        steps = re.findall(r"(?m)^\d+\. \*\*.+?\*\*", section)
        self.assertGreaterEqual(len(steps), 8)
        self.assertIn("Mise:", section)
        self.assertIn("Model:", section)

    def test_contract_identity_is_design_specific(self):
        data = json.loads((ROOT / "assets/use-case-contract.json").read_text())
        self.assertEqual(data["skill"], "design-like-im-5")
        self.assertIn("product design", " ".join(data["domain_terms"]).lower())


if __name__ == "__main__":
    unittest.main()
