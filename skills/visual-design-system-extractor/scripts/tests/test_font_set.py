import unittest

import context  # noqa: F401
import font_selection as sel
from google_fonts_api import build_catalog


def cut(**extra):
    """Return one cut mapping with the given metrics."""
    base = {"width": 6, "thickness": 5, "lineHeight": 1.4}
    base.update(extra)
    return base


def entry(name, popularity, **extra):
    """Return one feed shaped entry with style metadata."""
    base = {"family": name, "category": "Sans Serif", "stroke": "Sans Serif",
            "popularity": popularity, "trending": popularity,
            "dateAdded": "2024-01-01", "subsets": ["menu", "latin"],
            "designers": ["Someone"], "axes": [], "isNoto": False,
            "primaryScript": "Latn",
            "fonts": {"400": cut(), "500": cut(thickness=6), "700": cut(thickness=7)}}
    base.update(extra)
    return base


def catalog_of(*entries):
    """Return a catalog snapshot built from feed shaped entries."""
    return build_catalog(list(entries), retrieved_at="2026-01-01")


class RankTests(unittest.TestCase):
    def setUp(self):
        self.catalog = catalog_of(
            entry("Fitting Sans", 1900),
            entry("Rarer Serif", 1990, category="Serif", stroke="Serif"),
            entry("Rarest Loop", 2000, category="Handwriting", stroke=None),
            entry("Rarer Sans", 1950),
        )

    def test_a_better_fit_outranks_a_rarer_poor_fit(self):
        ranked = sel.rank(self.catalog, sel.build_criteria(skeleton="Sans Serif"))
        self.assertEqual(ranked[0]["family"], "Rarer Sans")

    def test_rarity_breaks_a_tie_between_equal_fits(self):
        ranked = sel.rank(self.catalog, sel.build_criteria(skeleton="Sans Serif"))
        names = [item["family"] for item in ranked]
        self.assertEqual(names[:2], ["Rarer Sans", "Fitting Sans"])

    def test_an_illegible_face_is_dropped_with_a_named_reason(self):
        ranked = sel.rank(self.catalog, sel.build_criteria(skeleton="Sans Serif"))
        self.assertNotIn("Rarest Loop", [item["family"] for item in ranked])
        rejected = sel.rejected(self.catalog, sel.build_criteria(skeleton="Sans Serif"))
        reasons = {item["family"]: item["reject_reason"] for item in rejected}
        self.assertIn("legibility", reasons["Rarest Loop"])

    def test_every_ranked_row_carries_its_fit_verdict(self):
        ranked = sel.rank(self.catalog, sel.build_criteria(skeleton="Sans Serif"))
        self.assertIn("fit_score", ranked[0]["fit"])

    def test_a_common_default_is_excluded_until_a_reason_is_stated(self):
        catalog = catalog_of(entry("Roboto", 1))
        criteria = sel.build_criteria(min_percentile=0.0)
        self.assertEqual(sel.rank(catalog, criteria), [])
        allowed = sel.build_criteria(min_percentile=0.0, allow_common=True,
                                    common_reason="the reference renders Roboto")
        self.assertEqual(len(sel.rank(catalog, allowed)), 1)

    def test_allowing_a_common_default_without_a_reason_raises(self):
        with self.assertRaises(ValueError):
            sel.build_criteria(allow_common=True)


class ChooseSetTests(unittest.TestCase):
    def setUp(self):
        serif = {"category": "Serif", "stroke": "Serif"}
        self.catalog = catalog_of(
            entry("Head Sans", 1980),
            entry("Twin Sans", 1990),
            entry("Body Serif", 1900, **serif),
        )

    def test_pairing_vetoes_the_top_candidate_and_takes_the_next(self):
        briefs = [{"role": "display", "criteria": sel.build_criteria(skeleton="Sans Serif")},
                  {"role": "text", "criteria": sel.build_criteria()}]
        result = sel.choose_set(self.catalog, briefs)
        chosen = {item["role"]: item["family"] for item in result["chosen"]}
        self.assertEqual(chosen["display"], "Twin Sans")
        self.assertEqual(chosen["text"], "Body Serif")

    def test_the_veto_is_reported_with_the_failing_dimension(self):
        briefs = [{"role": "display", "criteria": sel.build_criteria(skeleton="Sans Serif")},
                  {"role": "text", "criteria": sel.build_criteria()}]
        vetoes = sel.choose_set(self.catalog, briefs)["vetoes"]
        self.assertEqual(vetoes[0]["family"], "Head Sans")
        self.assertIn("role_distinction", vetoes[0]["failed_dimensions"])

    def test_the_chosen_set_passes_the_pairing_check(self):
        briefs = [{"role": "display", "criteria": sel.build_criteria(skeleton="Sans Serif")},
                  {"role": "text", "criteria": sel.build_criteria()}]
        self.assertTrue(sel.choose_set(self.catalog, briefs)["pairing"]["passes"])

    def test_an_unfillable_role_is_reported_rather_than_forced(self):
        briefs = [{"role": "text", "criteria": sel.build_criteria(skeleton="Monospace")}]
        result = sel.choose_set(self.catalog, briefs)
        self.assertEqual(result["chosen"], [])
        self.assertEqual(result["unfilled"][0]["role"], "text")


if __name__ == "__main__":
    unittest.main()
