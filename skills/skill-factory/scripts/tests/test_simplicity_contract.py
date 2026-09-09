"""Bounded documentation guards; plainness and meaning still need direct review."""
from pathlib import Path
import unittest

SKILL_DIR = Path(__file__).resolve().parents[2]


class TestSimplicityContract(unittest.TestCase):
    def read(self, relative):
        return (SKILL_DIR / relative).read_text(encoding="utf-8")

    def test_factory_names_simplicity_as_an_invariant(self):
        text = self.read("SKILL.md")
        self.assertIn("## Motivation", text)
        self.assertIn("smallest coherent structure", text)
        self.assertIn("same-meaning human review", text)

    def test_recursive_contract_preserves_plain_language_rules(self):
        text = self.read("references/generation-contract.md")
        for phrase in [
            "Preserve every accepted behavior",
            "one canonical rule owner",
            "Same-meaning human review",
            "references/writing-rules.md",
            "Never hide essential domain complexity",
        ]:
            self.assertIn(phrase, text)

    def test_generated_body_routes_to_the_language_owner(self):
        text = self.read("assets/skill-template.md")
        self.assertIn("## Motivation", text)
        self.assertIn("references/writing-rules.md", text)
        self.assertIn("one idea per sentence", text)

    def test_improvement_trials_cannot_trade_away_simplicity(self):
        text = self.read("scripts/check_improvement_contract.py")
        self.assertIn('"simplicity"', text)
        self.assertIn('"plain_language"', text)

    def test_portability_keeps_outcomes_fixed_and_adapters_replaceable(self):
        skill = self.read("SKILL.md")
        contract = self.read("references/generation-contract.md")
        for phrase in ["outcome", "proof", "boundaries", "forbidden outcomes",
                       "mandatory methods"]:
            self.assertIn(phrase, skill.lower())
            self.assertIn(phrase, contract.lower())
        self.assertIn("A source adapter is optional unless user-mandated", contract)
        self.assertIn("mise run audit-source-corpus", skill)


if __name__ == "__main__":
    unittest.main()
