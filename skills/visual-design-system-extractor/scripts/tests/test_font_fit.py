import unittest

import context  # noqa: F401
import font_fit
from google_fonts_api import build_catalog


def entry(name, **extra):
    """Return one feed shaped entry with usable style metadata."""
    base = {"family": name, "category": "Serif", "stroke": "Serif",
            "popularity": 1800, "trending": 900, "dateAdded": "2024-01-01",
            "subsets": ["menu", "latin"], "designers": ["Someone"], "axes": [],
            "isNoto": False, "primaryScript": "Latn",
            "fonts": {"400": {"width": 6, "thickness": 5, "lineHeight": 1.4},
                      "700": {"width": 6, "thickness": 8, "lineHeight": 1.4}}}
    base.update(extra)
    return base


def record(name, **extra):
    """Return one normalized catalog record."""
    catalog = build_catalog([entry(name, **extra)], retrieved_at="2026-01-01")
    return catalog["families"][0]


class RecordTests(unittest.TestCase):
    def test_the_record_carries_available_weights(self):
        self.assertEqual(record("Face")["weights"], [400, 700])

    def test_the_record_flags_italic_availability(self):
        italic = record("Face", fonts={"400": {}, "400i": {}})
        self.assertTrue(italic["italic"])

    def test_a_variable_weight_axis_widens_the_weight_range(self):
        variable = record("Face", axes=[{"tag": "wght", "min": 300, "max": 800}])
        self.assertEqual(variable["weight_range"], [300, 800])


class FitTests(unittest.TestCase):
    def test_a_matching_skeleton_scores_higher_than_a_mismatch(self):
        wanted = font_fit.target(skeleton="Serif")
        serif = font_fit.score(record("Serif Face"), wanted)
        sans = font_fit.score(record("Sans Face", category="Sans Serif",
                                     stroke="Sans Serif"), wanted)
        self.assertGreater(serif["fit_score"], sans["fit_score"])

    def test_a_missing_script_subset_fails_the_fit(self):
        wanted = font_fit.target(skeleton="Serif", scripts=["latin-ext"])
        self.assertEqual(font_fit.score(record("Face"), wanted)["fit_score"], 0.0)

    def test_missing_weights_lower_the_fit(self):
        wanted = font_fit.target(weights=[400, 700, 900])
        self.assertLess(font_fit.score(record("Face"), wanted)["fit_score"], 1.0)

    def test_a_variable_axis_covers_the_needed_weights(self):
        wanted = font_fit.target(weights=[400, 700, 900])
        variable = record("Face", axes=[{"tag": "wght", "min": 300, "max": 900}])
        self.assertEqual(font_fit.score(variable, wanted)["weight_score"], 1.0)


class LegibilityTests(unittest.TestCase):
    def test_a_handwriting_face_fails_the_text_floor(self):
        hand = record("Loopy", category="Handwriting", stroke=None)
        result = font_fit.score(hand, font_fit.target(role="text"))
        self.assertLess(result["legibility_score"], font_fit.ROLE_FLOORS["text"])
        self.assertFalse(result["passes"])

    def test_the_same_face_can_serve_a_display_role(self):
        hand = record("Loopy", category="Handwriting", stroke=None)
        result = font_fit.score(hand, font_fit.target(role="display", skeleton=None))
        self.assertTrue(result["passes"], result)

    def test_no_flag_lowers_the_hard_legibility_floor(self):
        self.assertEqual(font_fit.floor_for("text", 0.0), font_fit.HARD_FLOOR)

    def test_a_non_latin_primary_script_costs_legibility(self):
        latin = record("Face")["family"]
        other = record("Face", primaryScript="Syrc")
        self.assertLess(
            font_fit.score(other, font_fit.target())["legibility_score"],
            font_fit.score(record(latin), font_fit.target())["legibility_score"])


class CommonFaceTests(unittest.TestCase):
    def test_a_common_default_is_marked(self):
        self.assertTrue(font_fit.is_common("Roboto"))

    def test_a_rare_family_is_not_marked(self):
        self.assertFalse(font_fit.is_common("Idiqlat"))


if __name__ == "__main__":
    unittest.main()
