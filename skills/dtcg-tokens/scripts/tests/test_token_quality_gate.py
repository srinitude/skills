"""Token-local quality gate behavior."""

import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CATALOG = ROOT / "assets" / "judgment-review-catalog.json"
sys.path.insert(0, str(ROOT / "scripts"))
from lib import review  # noqa: E402


class TokenQualityGateTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))

    def test_contract_is_token_local_and_noncompensating(self):
        self.assertIn("token_quality_gate", self.catalog)
        gate = self.catalog["token_quality_gate"]
        self.assertEqual(gate["scope"], "token_and_proof_only")
        self.assertFalse(gate["whole_product_quality_allowed"])
        self.assertTrue(gate["noncompensating"])
        self.assertEqual(
            gate["gate_ids"],
            [
                "source_fidelity", "semantic_role", "accessible_range",
                "spacing_relationships", "responsive_behavior", "familiarity",
                "standards", "uniqueness", "rendered_proof",
            ],
        )
        self.assertEqual(
            gate["spacing_roles"],
            ["related_item", "inset", "group", "section", "shell", "wide_aperture"],
        )

    def test_mechanical_check_rejects_one_failed_gate_despite_other_passes(self):
        checker = getattr(review, "check_token_quality_gate", None)
        self.assertTrue(callable(checker), "token quality gate checker is missing")
        gate_ids = self.catalog["token_quality_gate"]["gate_ids"]
        record = {
            "scope": "token_and_proof_only",
            "status": "pass",
            "diagnosis": "PASS",
            "whole_product_quality_proved": False,
            "gates": [
                {"id": gate_id, "status": "pass", "evidence": "current rendered evidence"}
                for gate_id in gate_ids
            ],
        }
        record["gates"][5]["status"] = "fail"
        errors = []
        checker(record, self.catalog["token_quality_gate"], errors, final=True)
        self.assertTrue(any("familiarity" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
