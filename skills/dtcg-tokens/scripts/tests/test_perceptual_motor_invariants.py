import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "assets" / "perceptual-motor-invariant-catalog.json"


class PerceptualMotorInvariantTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        self.invariants = self.catalog["invariants"]

    def test_required_domains_and_minimum_surface(self):
        self.assertEqual(
            set(self.catalog["domains"]),
            {"visual_perception", "cognitive_comprehension", "motor_touch", "cross_context"},
        )
        self.assertGreaterEqual(len(self.invariants), 36)

    def test_each_invariant_checks_tokens_and_render(self):
        required = {
            "id",
            "domain",
            "invariant",
            "applies_when",
            "token_feasibility_check",
            "render_check",
            "pass_condition",
            "failure_condition",
            "allowed_exception",
            "required_evidence",
        }
        ids = [item["id"] for item in self.invariants]
        self.assertEqual(len(ids), len(set(ids)))
        for item in self.invariants:
            self.assertEqual(required, set(item))
            self.assertIn(item["domain"], self.catalog["domains"])
            self.assertTrue(item["token_feasibility_check"])
            self.assertTrue(item["render_check"])
            self.assertTrue(item["required_evidence"])

    def test_core_eye_brain_touch_invariants_are_present(self):
        ids = {item["id"] for item in self.invariants}
        self.assertTrue(
            {
                "VP-CONTRAST-001",
                "VP-FIGURE-GROUND-001",
                "VP-GROUPING-001",
                "VP-HIERARCHY-001",
                "CC-MAPPING-001",
                "CC-STATE-UNAMBIGUITY-001",
                "CC-ERROR-PRIORITY-001",
                "MT-TARGET-SIZE-001",
                "MT-TARGET-SPACING-001",
                "MT-FOCUS-001",
                "XC-REFLOW-001",
                "XC-REDUCED-MOTION-001",
                "X-UNKNOWN-INVARIANT-001",
            }.issubset(ids)
        )

    def test_catalog_does_not_impose_a_house_style(self):
        policy = self.catalog["decision_policy"]
        self.assertEqual(policy["scope"], "minimum_relational_invariants")
        self.assertTrue(policy["style_neutral"])
        self.assertTrue(policy["contextual_values_required"])
        self.assertFalse(policy["token_file_alone_can_pass"])
        self.assertTrue(policy["experimental_branches_allowed"])
        self.assertTrue(policy["invariants_gate_published_use_not_token_existence"])
        self.assertEqual(
            set(self.catalog["creative_exception_protocol"]),
            {
                "preserve_intent",
                "name_experiment",
                "prove_equivalent_access",
                "test_real_render",
                "record_tradeoff",
                "retain_unknowns",
            },
        )


if __name__ == "__main__":
    unittest.main()
