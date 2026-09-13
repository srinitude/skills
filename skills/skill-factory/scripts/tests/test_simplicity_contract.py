"""Bounded documentation guards; plainness and meaning still need direct review."""
from pathlib import Path
import unittest

SKILL_DIR = Path(__file__).resolve().parents[2]


def _TestSimplicityContract_read(self, relative):
    return (SKILL_DIR / relative).read_text(encoding="utf-8")

def _TestSimplicityContract_test_factory_names_simplicity_as_an_invariant(self):
    text = self.read("SKILL.md")
    self.assertIn("## Motivation", text)
    for phrase in ["Simple means clear and complete under the contract",
                   "Keep one owner for each meaning, one stable term and one default route per real choice",
                   "Reuse existing code, native tools and accepted structures before adding dependencies",
                   "Fewer files, lines, connectors, tokens or seconds cannot justify lost rules",
                   "They cannot cut domain complexity, safety, privacy, accessibility, authority or proof",
                   "Human same-meaning review checks clarity and completeness"]:
        self.assertIn(phrase, text)

def _TestSimplicityContract_test_recursive_contract_preserves_plain_language_rules(self):
    text = self.read("references/generation-contract.md")
    for phrase in [
        "Preserve every accepted behavior",
        "one canonical rule owner",
        "Same-meaning human review",
        "references/writing-rules.md",
        "Never hide essential domain complexity",
    ]:
        self.assertIn(phrase, text)

def _TestSimplicityContract_test_generated_body_routes_to_the_language_owner(self):
    text = self.read("assets/skill-template.md")
    self.assertIn("## Motivation", text)
    self.assertIn("references/writing-rules.md", text)
    self.assertIn("one idea per sentence", text)

def _TestSimplicityContract_test_improvement_trials_cannot_trade_away_simplicity(self):
    text = self.read("scripts/check_improvement_contract.py")
    self.assertIn('"simplicity"', text)
    self.assertIn('"plain_language"', text)

def _TestSimplicityContract_test_portability_keeps_outcomes_fixed_and_adapters_replaceable(self):
    skill = self.read("SKILL.md")
    contract = self.read("references/generation-contract.md")
    for phrase in ["outcome", "proof", "boundaries", "forbidden outcomes",
                   "mandatory methods"]:
        self.assertIn(phrase, skill.lower())
        self.assertIn(phrase, contract.lower())
    self.assertIn("A source adapter is optional unless user-mandated", contract)
    self.assertIn("mise run audit-source-corpus", skill)


class TestSimplicityContract(unittest.TestCase):
    read = _TestSimplicityContract_read
    test_factory_names_simplicity_as_an_invariant = _TestSimplicityContract_test_factory_names_simplicity_as_an_invariant
    test_recursive_contract_preserves_plain_language_rules = _TestSimplicityContract_test_recursive_contract_preserves_plain_language_rules
    test_generated_body_routes_to_the_language_owner = _TestSimplicityContract_test_generated_body_routes_to_the_language_owner
    test_improvement_trials_cannot_trade_away_simplicity = _TestSimplicityContract_test_improvement_trials_cannot_trade_away_simplicity
    test_portability_keeps_outcomes_fixed_and_adapters_replaceable = _TestSimplicityContract_test_portability_keeps_outcomes_fixed_and_adapters_replaceable


if __name__ == "__main__":
    unittest.main()
