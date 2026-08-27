"""Contracts for live uncommon Google Font selection and offline proof use."""
import json
import pathlib
import sys
import unittest
from datetime import datetime, timezone


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))


def catalog_fixture():
    families = []
    for rank, family in enumerate(["Common One", "Common Two", "Median", "Rare One", "Rare Two", "Rare Three"], start=1):
        families.append({"family": family, "popularity": rank, "category": "Serif", "subsets": ["latin"], "fonts": {"400": {}}, "axes": [], "isOpenSource": True, "isBrandFont": False})
    return {"familyMetadataList": families}


class GoogleFontPolicyTests(unittest.TestCase):
    def test_policy_excludes_the_live_catalogs_most_popular_half(self):
        path = ROOT / "assets" / "google-font-policy.json"
        self.assertTrue(path.is_file())
        policy = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(policy["uncommon_threshold"]["excluded_top_fraction"], 0.5)
        self.assertEqual(
            policy["uncommon_threshold"]["eligible_when"],
            "popularity_rank > floor(total_families * excluded_top_fraction)",
        )

    def test_skill_routes_selection_to_one_procedure_and_script(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/google-font-selection.md", skill)
        self.assertIn("scripts/prepare_google_fonts.py", skill)
        self.assertIn("outside the most popular 50%", skill)

    def test_rank_three_is_excluded_and_rank_four_is_eligible(self):
        from lib.google_fonts import evaluate_candidates

        result = evaluate_candidates(catalog_fixture(), ["Median", "Rare One", "Rare Two", "Rare Three"], ["Rare One"], {"excluded_top_fraction": 0.5}, ["latin"])
        by_name = {item["family"]: item for item in result["candidates"]}
        self.assertFalse(by_name["Median"]["eligible"])
        self.assertTrue(by_name["Rare One"]["eligible"])
        self.assertEqual(result["cutoff_rank"], 3)

    def test_inline_css_embeds_exact_woff2_bytes(self):
        from lib.google_fonts import inline_font_css

        source = "https://fonts.gstatic.com/s/rare/v1/rare.woff2"
        css = "@font-face{font-family:'Rare One';font-style:normal;font-weight:400;src:url(%s) format('woff2')}" % source
        font = b"wOF2" + bytes(124)
        rendered, assets = inline_font_css(css, {source: font})
        self.assertIn("data:font/woff2;base64,", rendered)
        self.assertNotIn(source, rendered)
        self.assertEqual(assets[0]["family"], "Rare One")
        self.assertEqual(assets[0]["bytes"], 128)

    def test_catalog_date_must_match_the_run_and_be_fresh(self):
        from lib.google_fonts import validate_catalog_response_date

        now = datetime(2026, 8, 27, 17, 30, tzinfo=timezone.utc)
        self.assertEqual(
            validate_catalog_response_date(
                "Thu, 27 Aug 2026 17:29:30 GMT",
                "2026-08-27",
                now=now,
                maximum_age_seconds=600,
            ),
            "2026-08-27",
        )
        with self.assertRaisesRegex(ValueError, "E_FONT_CURRENT"):
            validate_catalog_response_date(
                "Thu, 27 Aug 2026 16:00:00 GMT",
                "2026-08-27",
                now=now,
                maximum_age_seconds=600,
            )


if __name__ == "__main__":
    unittest.main()
