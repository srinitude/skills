"""Coverage-manifest contracts for every DTCG type and finite permutation."""
import json
import pathlib
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = SKILL_DIR / "evals" / "files"
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from lib.coverage import analyze_coverage


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class TestCoverageManifest(unittest.TestCase):
    def test_sample_covers_every_token_and_type_status(self):
        manifest, errors = analyze_coverage(load("sample.tokens.json"), load("sample.evidence.json"))
        self.assertEqual(errors, [])
        self.assertEqual(len(manifest["type_coverage"]), 13)
        self.assertEqual(manifest["totals"]["tokens_expected"], manifest["totals"]["tokens_rendered"])
        self.assertEqual(manifest["totals"]["unexplained_skips"], 0)
        self.assertEqual(manifest["status"], "pass")

    def test_all_types_fixture_supplies_every_standard_type(self):
        manifest, errors = analyze_coverage(load("all-types.tokens.json"), load("all-types.evidence.json"))
        self.assertEqual(errors, [])
        supplied = {item["type"] for item in manifest["type_coverage"] if item["supplied"]}
        self.assertEqual(len(supplied), 13)
        self.assertTrue(all(item["rendered"] == item["supplied"] for item in manifest["type_coverage"]))

    def test_two_axis_group_expands_full_cartesian_product(self):
        manifest, errors = analyze_coverage(load("sample.tokens.json"), load("sample.evidence.json"))
        self.assertEqual(errors, [])
        group = next(item for item in manifest["variant_groups"] if item["id"] == "surface-states")
        self.assertEqual(group["expected"], 4)
        self.assertEqual(group["rendered"], 4)
        self.assertEqual(len(group["cells"]), 4)

    def test_unknown_exclusion_cell_blocks(self):
        evidence = load("sample.evidence.json")
        evidence["permutation_space"]["exclusions"].append({"cell": "surface-states|missing|cell", "reason": "Bad cell", "evidence": "No source location"})
        _, errors = analyze_coverage(load("sample.tokens.json"), evidence)
        self.assertIn("unknown permutation exclusion", " | ".join(errors))


if __name__ == "__main__":
    unittest.main()
