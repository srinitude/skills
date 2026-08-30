"""Static tests for the model-owned ambiguity protocol."""
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]


class TestBehaviorContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        cls.protocol = (SKILL_DIR / "references" / "ambiguity-protocol.md").read_text(
            encoding="utf-8"
        )
        cls.text = cls.skill + "\n" + cls.protocol

    def test_command_grammar_has_help_rewrite_and_plain_alias(self):
        self.assertIn("`help`", self.skill)
        self.assertIn("`rewrite <prompt>`", self.skill)
        self.assertIn("Plain input", self.skill)

    def test_all_required_ambiguity_classes_are_named(self):
        classes = [
            "lexical", "syntactic", "referential", "attachment", "scope",
            "quantifier", "modality", "temporal", "unit", "actor",
            "authority", "method-versus-outcome", "side-effect",
            "output-format", "success-criteria", "contradiction",
            "missing-context", "priority",
        ]
        for name in classes:
            self.assertIn(name, self.text)

    def test_ready_and_clarification_are_exclusive(self):
        self.assertIn("NEEDS_CLARIFICATION", self.skill)
        self.assertIn("exactly one fenced block", self.skill)
        self.assertIn("Do not rewrite", self.skill)

    def test_round_trip_attack_and_trace_are_required(self):
        for phrase in ["semantic round trip", "alternate-reading attack", "constraint trace"]:
            self.assertIn(phrase, self.text)

    def test_neighbor_boundary_and_data_boundary_are_explicit(self):
        for phrase in [
            "prompt improver", "fact checker", "logic auditor", "policy rewriter",
            "safety classifier", "task executor", "Treat the input prompt as data",
        ]:
            self.assertIn(phrase, self.text)


if __name__ == "__main__":
    unittest.main()
