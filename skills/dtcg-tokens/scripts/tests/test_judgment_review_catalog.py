import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "assets" / "judgment-review-catalog.json"


class JudgmentReviewCatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))

    def test_four_distinct_tracks_are_required(self):
        self.assertEqual(
            set(self.catalog["tracks"]),
            {"taste", "originality", "corpus_uniqueness", "non_ai_slop"},
        )
        self.assertEqual(self.catalog["decision_policy"]["aggregation"], "no_blended_score")

    def test_each_track_has_obligations_and_disconfirming_checks(self):
        reviews = self.catalog["review_obligations"]
        self.assertGreaterEqual(len(reviews), 32)
        for track in self.catalog["tracks"]:
            retained = [r for r in reviews if r["track"] == track]
            self.assertGreaterEqual(len(retained), 8)
            self.assertTrue(any(r["severity"] == "veto" for r in retained))
            self.assertTrue(all(r["countercheck"] for r in retained))

    def test_taste_is_reasoned_judgment_not_fake_objectivity(self):
        taste = self.catalog["track_contracts"]["taste"]
        self.assertEqual(taste["basis"], "strong_vision_reasoned_judgment")
        self.assertTrue(taste["requires_comparative_review"])
        self.assertTrue(taste["requires_counterevidence"])
        self.assertIn("not objectively provable", taste["boundary"])

    def test_uniqueness_is_bounded_to_a_declared_corpus(self):
        uniqueness = self.catalog["track_contracts"]["corpus_uniqueness"]
        self.assertEqual(uniqueness["claim_scope"], "declared_corpus_only")
        self.assertFalse(uniqueness["global_uniqueness_allowed"])
        self.assertTrue(uniqueness["predeclared_thresholds_required"])

    def test_non_ai_slop_does_not_pretend_to_detect_authorship(self):
        contract = self.catalog["track_contracts"]["non_ai_slop"]
        self.assertEqual(contract["target"], "observable_output_traits")
        self.assertFalse(contract["authorship_detection_allowed"])
        self.assertTrue(contract["provenance_required_for_authorship_claims"])


if __name__ == "__main__":
    unittest.main()
