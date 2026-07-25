import unittest

import context  # noqa: F401
import font_rules
from google_fonts_api import FEED_URL


def rarity(**overrides):
    """Return a complete rarity record with optional overrides."""
    block = {"popularity_rank": 1700, "total_families": 1900,
             "rarity_percentile": 89.4, "trending_rank": 1200,
             "date_added": "2022-02-17", "variable": False,
             "source": FEED_URL, "retrieved_at": "2026-01-01"}
    block.update(overrides)
    return block


def candidate(**overrides):
    """Return a complete rare candidate entry with optional overrides."""
    entry = {"family": "Rubik Puddles", "google_fonts_family": True,
             "rarity": rarity(), "role": "display", "classification": "display",
             "fallback_stack": ["Georgia", "serif"], "pairs_well_with": ["Alkalami"],
             "visual_grounding": "Matches the poured letterform edges.",
             "rarity_reason": "Rank 1700 of 1900 places it outside common use.",
             "pairing_logic": "Display voice above a quieter text face.",
             "use_constraints": "Display sizes only.", "confidence": "medium",
             "inference_basis": "Ranked by the live catalog."}
    entry.update(overrides)
    return entry


def run(font_families, floor=70.0):
    """Return the static problems found in one font_families mapping."""
    errors = []
    font_rules.check_font_families({"font_families": font_families}, floor, errors)
    return errors


class AcceptanceTests(unittest.TestCase):
    def test_a_complete_candidate_passes(self):
        self.assertEqual(run({"rare_unique_candidates": [candidate()]}), [])

    def test_observed_families_carry_no_rarity_duty(self):
        families = {"rare_unique_candidates": [candidate()],
                    "observed_or_implied": [{"family": "Custom House Face"}]}
        self.assertEqual(run(families), [])


class RejectionTests(unittest.TestCase):
    def assert_rejects(self, entry, fragment):
        errors = run({"rare_unique_candidates": [entry]})
        self.assertTrue(any(fragment in item for item in errors), errors)

    def test_a_missing_candidate_list_is_rejected(self):
        self.assertTrue(run({}))

    def test_a_common_default_is_rejected(self):
        self.assert_rejects(candidate(family="Inter"), "common default")

    def test_an_undeclared_google_family_is_rejected(self):
        self.assert_rejects(candidate(google_fonts_family=False), "google_fonts_family")

    def test_a_popular_percentile_is_rejected(self):
        self.assert_rejects(candidate(rarity=rarity(rarity_percentile=12.0)), "floor is 70.0")

    def test_a_foreign_rarity_source_is_rejected(self):
        self.assert_rejects(candidate(rarity=rarity(source="https://example.com")),
                            "rarity.source must be")

    def test_a_missing_rarity_block_is_rejected(self):
        self.assert_rejects(candidate(rarity="very rare"), "rarity must be a mapping")

    def test_a_non_numeric_percentile_is_rejected(self):
        self.assert_rejects(candidate(rarity=rarity(rarity_percentile="high")),
                            "must be a number")

    def test_a_missing_use_constraint_is_rejected(self):
        entry = candidate()
        del entry["use_constraints"]
        self.assert_rejects(entry, "missing required field: use_constraints")

    def test_an_empty_fallback_stack_is_rejected(self):
        self.assert_rejects(candidate(fallback_stack=[]), "fallback_stack")

    def test_a_primary_slot_needs_the_same_proof(self):
        errors = run({"primary": {"family": "Rubik Puddles"},
                      "rare_unique_candidates": [candidate()]})
        self.assertTrue(any("primary" in item for item in errors), errors)


class LiveComparisonTests(unittest.TestCase):
    def setUp(self):
        from google_fonts_api import load_catalog

        self.catalog = load_catalog()

    def test_a_stale_rank_is_reported(self):
        entries = [("primary", candidate(rarity=rarity(popularity_rank=2)), True)]
        errors = []
        font_rules.verify_live(entries, self.catalog, 70.0, errors)
        self.assertTrue(any("stale" in item for item in errors), errors)

    def test_an_invented_family_is_reported(self):
        entries = [("primary", candidate(family="Not A Real Family"), True)]
        errors = []
        font_rules.verify_live(entries, self.catalog, 70.0, errors)
        self.assertTrue(any("absent from the live catalog" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
