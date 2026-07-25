import unittest

import context  # noqa: F401
import font_selection as sel
from google_fonts_api import build_catalog


def entry(name, popularity, **extra):
    """Return one feed shaped entry for catalog construction."""
    base = {"family": name, "category": "Serif", "popularity": popularity,
            "trending": popularity, "dateAdded": "2020-01-01",
            "subsets": ["menu", "latin"], "designers": ["Someone"],
            "axes": [], "isNoto": False}
    base.update(extra)
    return base


def catalog_of(*entries):
    """Return a catalog snapshot built from feed shaped entries."""
    return build_catalog(list(entries), retrieved_at="2026-01-01")


class CriteriaTests(unittest.TestCase):
    def test_defaults_keep_the_rarest_third(self):
        self.assertEqual(sel.default_criteria()["min_percentile"], 70.0)

    def test_unknown_criteria_are_rejected(self):
        with self.assertRaises(ValueError):
            sel.build_criteria(colour="blue")

    def test_none_overrides_keep_the_default(self):
        self.assertEqual(sel.build_criteria(category=None)["min_percentile"], 70.0)


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.catalog = catalog_of(
            entry("Common Face", 1),
            entry("Middle Face", 2),
            entry("Rare Noto", 3, isNoto=True),
            entry("Rare Display", 4, category="Display", axes=[{"tag": "wght"}]),
            entry("Rare Serif", 5, subsets=["menu", "latin", "latin-ext"]),
        )

    def test_popular_families_are_dropped(self):
        chosen = sel.select(self.catalog, sel.build_criteria())
        self.assertNotIn("Common Face", [item["family"] for item in chosen])

    def test_results_rank_rarest_first(self):
        chosen = sel.select(self.catalog, sel.build_criteria())
        self.assertEqual(chosen[0]["family"], "Rare Serif")

    def test_noto_families_are_excluded_by_default(self):
        chosen = sel.select(self.catalog, sel.build_criteria())
        self.assertNotIn("Rare Noto", [item["family"] for item in chosen])

    def test_category_filter_narrows_the_list(self):
        chosen = sel.select(self.catalog, sel.build_criteria(category="display"))
        self.assertEqual([item["family"] for item in chosen], ["Rare Display"])

    def test_variable_only_requires_axes(self):
        chosen = sel.select(self.catalog, sel.build_criteria(variable_only=True))
        self.assertEqual([item["family"] for item in chosen], ["Rare Display"])

    def test_subset_filter_ignores_the_menu_subset(self):
        chosen = sel.select(self.catalog, sel.build_criteria(subset="latin-ext"))
        self.assertEqual([item["family"] for item in chosen], ["Rare Serif"])

    def test_limit_truncates_the_ranked_list(self):
        chosen = sel.select(self.catalog, sel.build_criteria(limit=1))
        self.assertEqual(len(chosen), 1)

    def test_raising_the_floor_can_empty_the_list(self):
        self.assertEqual(sel.select(self.catalog, sel.build_criteria(min_percentile=100.5)), [])


if __name__ == "__main__":
    unittest.main()
