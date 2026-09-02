"""Contracts for domain-complete instructions with bounded context cost."""
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]


class TestTokenEfficiencyContract(unittest.TestCase):
    def setUp(self):
        self.body = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.contract = (SKILL_DIR / "references/generation-contract.md").read_text(
            encoding="utf-8")
        self.template = (SKILL_DIR / "assets/skill-template.md").read_text(
            encoding="utf-8")
        self.improvement = json.loads(
            (SKILL_DIR / "assets/improvement-contract.json").read_text("utf-8"))

    def test_factory_and_generated_skill_bound_context(self):
        for text in [self.body, self.contract, self.template]:
            lowered = text.lower()
            self.assertIn("context budget", lowered)
            self.assertIn("canonical owner", lowered)
            self.assertIn("digest", lowered)

    def test_token_efficiency_cannot_remove_domain_judgment(self):
        for text in [self.body, self.contract, self.template]:
            lowered = text.lower()
            self.assertIn("token efficiency", lowered)
            self.assertIn("model-owned", lowered)
            self.assertIn("domain", lowered)

    def test_token_efficiency_is_a_protected_dimension(self):
        protected = self.improvement["protected_dimensions"]
        self.assertIn("token_efficiency", protected)
        self.assertIn("semantic_judgment", protected)
        self.assertIn("current_skill_contract", protected)


if __name__ == "__main__":
    unittest.main()
