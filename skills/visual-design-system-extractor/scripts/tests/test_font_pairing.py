import unittest

import context  # noqa: F401
import font_pairing
from google_fonts_api import build_catalog


def entry(name, **extra):
    """Return one feed shaped entry with usable pairing metadata."""
    base = {"family": name, "category": "Sans Serif", "stroke": "Sans Serif",
            "popularity": 1800, "trending": 900, "dateAdded": "2024-01-01",
            "subsets": ["menu", "latin"], "designers": ["Someone"], "axes": [],
            "isNoto": False, "primaryScript": "Latn",
            "fonts": {"400": {"width": 6, "thickness": 5, "lineHeight": 1.4},
                      "500": {"width": 6, "thickness": 6, "lineHeight": 1.4},
                      "700": {"width": 6, "thickness": 8, "lineHeight": 1.4}}}
    base.update(extra)
    return base


def record(name, **extra):
    """Return one normalized catalog record."""
    return build_catalog([entry(name, **extra)], retrieved_at="2026-01-01")["families"][0]


def cut(**extra):
    """Return one cut mapping with the given metrics."""
    base = {"width": 6, "thickness": 5, "lineHeight": 1.4}
    base.update(extra)
    return base


class SetShapeTests(unittest.TestCase):
    def test_a_single_face_set_passes(self):
        members = [{"role": "text", "record": record("Only Face")}]
        self.assertTrue(font_pairing.check_set(members)["passes"])

    def test_every_dimension_is_reported_by_name(self):
        members = [{"role": "display", "record": record("Head Face")},
                   {"role": "text", "record": record("Body Face",
                                                     category="Serif",
                                                     stroke="Serif")}]
        names = [item["dimension"] for item in
                 font_pairing.check_set(members)["dimensions"]]
        self.assertEqual(sorted(names), sorted(font_pairing.DIMENSIONS))


class TooSimilarTests(unittest.TestCase):
    def test_two_near_duplicate_faces_fail_role_distinction(self):
        members = [{"role": "display", "record": record("Twin One")},
                   {"role": "text", "record": record("Twin Two")}]
        result = font_pairing.check_set(members)
        self.assertFalse(result["passes"])
        self.assertIn("role_distinction", result["failed_dimensions"])
        self.assertTrue(result["failures"][0]["reason"])


class ClashTests(unittest.TestCase):
    def test_mismatched_vertical_proportion_fails(self):
        tall = record("Tall Face", category="Serif", stroke="Serif",
                      fonts={"400": cut(lineHeight=2.4), "700": cut(lineHeight=2.4)})
        members = [{"role": "display", "record": record("Head Face")},
                   {"role": "text", "record": tall}]
        result = font_pairing.check_set(members)
        self.assertIn("vertical_proportion", result["failed_dimensions"])

    def test_mismatched_width_fails(self):
        narrow = record("Narrow Face", category="Serif", stroke="Serif",
                        fonts={"400": cut(width=1), "700": cut(width=1)})
        members = [{"role": "display", "record": record("Head Face")},
                   {"role": "text", "record": narrow}]
        self.assertIn("width_compatibility",
                      font_pairing.check_set(members)["failed_dimensions"])

    def test_mismatched_stroke_modulation_fails(self):
        heavy = record("Heavy Face", category="Serif", stroke="Serif",
                       fonts={"400": cut(thickness=1), "700": cut(thickness=1)})
        members = [{"role": "display", "record": record("Head Face")},
                   {"role": "text", "record": heavy}]
        self.assertIn("stroke_modulation",
                      font_pairing.check_set(members)["failed_dimensions"])

    def test_a_text_face_without_hierarchy_weights_fails(self):
        thin = record("Thin Face", category="Serif", stroke="Serif",
                      fonts={"400": cut()})
        members = [{"role": "text", "record": thin}]
        self.assertIn("weight_capacity",
                      font_pairing.check_set(members)["failed_dimensions"])

    def test_two_display_faces_clash_on_skeleton_relationship(self):
        members = [{"role": "display", "record": record("Loud One",
                                                        category="Display",
                                                        stroke=None)},
                   {"role": "accent", "record": record("Loud Two",
                                                       category="Handwriting",
                                                       stroke=None)}]
        self.assertIn("skeleton_relationship",
                      font_pairing.check_set(members)["failed_dimensions"])


class GoodSetTests(unittest.TestCase):
    def test_a_deliberately_contrasted_pair_passes(self):
        serif = record("Body Serif", category="Serif", stroke="Serif",
                       fonts={"300": cut(thickness=4, lineHeight=1.5),
                              "400": cut(thickness=5, lineHeight=1.5),
                              "700": cut(thickness=7, lineHeight=1.5)})
        members = [{"role": "display", "record": record("Head Sans")},
                   {"role": "text", "record": serif}]
        result = font_pairing.check_set(members)
        self.assertTrue(result["passes"], result["failures"])


if __name__ == "__main__":
    unittest.main()
