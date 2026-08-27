import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "assets" / "visual-defect-catalog.json"


class VisualDefectCatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        self.markers = self.catalog["markers"]

    def test_catalog_covers_the_review_surface(self):
        required_families = {
            "render-integrity",
            "layout-geometry",
            "typography-readability",
            "color-contrast",
            "interaction-accessibility",
            "responsive-adaptation",
            "information-architecture",
            "design-coherence",
            "source-specificity",
            "proof-integrity",
            "technical-integrity",
            "content-integrity",
            "corpus-distinctiveness",
            "state-coverage",
            "production-readiness",
            "temporal-integrity",
        }
        self.assertGreaterEqual(len(self.markers), 120)
        self.assertTrue(required_families.issubset({m["family"] for m in self.markers}))

    def test_every_marker_is_operational(self):
        required = {
            "id",
            "family",
            "scope",
            "severity",
            "basis",
            "marker",
            "inspection",
            "fail_when",
            "allowed_exception",
            "required_evidence",
        }
        ids = [m["id"] for m in self.markers]
        self.assertEqual(len(ids), len(set(ids)))
        for marker in self.markers:
            self.assertEqual(required, set(marker))
            self.assertIn(marker["scope"], {"source", "artifact", "both"})
            self.assertIn(marker["severity"], {"veto", "major", "warning"})
            self.assertIn(marker["basis"], {"machine", "vision", "hybrid"})
            for field in required - {"severity"}:
                self.assertTrue(marker[field])

    def test_known_hard_failures_are_named(self):
        ids = {m["id"] for m in self.markers}
        expected = {
            "RI-OVERLAP-001",
            "RI-CLIP-001",
            "RI-OVERFLOW-001",
            "CR-TEXT-CONTRAST-001",
            "IA-PREMATURE-VERDICT-001",
            "DC-DECORATION-WITHOUT-MEANING-001",
            "SS-NOUN-SUBSTITUTION-001",
            "PI-UNSUPPORTED-PASS-001",
            "CD-LAYOUT-SKELETON-001",
            "PR-PLACEHOLDER-001",
            "TI-STALE-CLAIM-001",
            "X-UNKNOWN-DEFECT-001",
        }
        self.assertTrue(expected.issubset(ids))

    def test_vetoes_are_decidable_and_exceptions_are_bounded(self):
        for marker in self.markers:
            if marker["severity"] != "veto":
                continue
            self.assertNotIn("looks bad", marker["fail_when"].lower())
            self.assertGreaterEqual(len(marker["inspection"]), 20)
            self.assertGreaterEqual(len(marker["required_evidence"]), 15)
            self.assertNotEqual(marker["allowed_exception"].strip().lower(), "context dependent")

    def test_catalog_forbids_blended_scores_and_requires_unknown_defect_capture(self):
        self.assertEqual(self.catalog["decision_policy"]["aggregation"], "no_blended_score")
        self.assertTrue(self.catalog["decision_policy"]["unknown_marker_required"])
        self.assertIn("allowed_exception", self.catalog["decision_policy"]["exception_rule"])


if __name__ == "__main__":
    unittest.main()
