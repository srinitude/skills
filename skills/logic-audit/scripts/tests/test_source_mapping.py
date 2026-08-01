"""Lineage tests for the native-to-port meaning contract."""
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
EXPECTED_FILES = {
    "SKILL.md": "30111ea612803022da7575bb6deaf5bf5b9a1d34325b6c873135777c4eab56bf",
    "references/check-catalog.md":
        "e9a7fe8dfa4f145fb61d3e82117bf3406d5cd95fd1ee95b774b35406b8b3360f",
    "references/eval-cases.json":
        "456c3019f38b2009aba52125efb7036ead79f382ec91c10262218a16d4d82af8",
}
EXPECTED_CASES = [
    "direct-contradiction",
    "temporal-non-contradiction",
    "quantifier-drift",
    "necessary-sufficient-reversal",
    "missing-case",
    "component-proof-gap",
    "authority-conflict",
    "current-web-claim",
    "web-tool-failure",
    "exact-method-preservation",
]
LINEAGE_CASES = [f"NLA-{number:03d}" for number in range(1, 11)]


def load(relative):
    return json.loads((SKILL_DIR / relative).read_text(encoding="utf-8"))


class TestSourceMapping(unittest.TestCase):
    def test_lineage_binds_every_native_file_and_case(self):
        lineage = load("evals/source-lineage.json")
        files = {
            entry["path"]: entry["sha256"]
            for entry in lineage["source_files"]
        }
        self.assertEqual(files, EXPECTED_FILES)
        self.assertEqual(lineage["source_case_ids"], LINEAGE_CASES)
        self.assertEqual(
            lineage["native_manifest_sha256"],
            "fe949512d2fd091a39606dab3e1644289032231d2ba27fc929a2efbb1fae8b18",
        )

    def test_mapping_covers_every_nonblank_line_without_drop(self):
        mapping = load("evals/source-mapping.json")
        entries = mapping["entries"]
        self.assertEqual(mapping["coverage"], {
            "source_nonblank_lines": 240,
            "mapped_nonblank_lines": 240,
            "ratio": 1.0,
        })
        self.assertEqual(len(entries), 240)
        self.assertNotIn("drop", {entry["action"] for entry in entries})
        self.assertTrue(all(
            entry["review_state"] == "approved" for entry in entries
        ))
        self.assertTrue(all(entry["public_target"] for entry in entries))
        self.assertTrue(all(entry["evidence_target"] for entry in entries))
        self.assertTrue(all("source_text" not in entry for entry in entries))

    def test_case_mapping_preserves_native_ids(self):
        mapping = load("evals/source-mapping.json")
        self.assertEqual(list(mapping["case_mapping"]), EXPECTED_CASES)
        expected = [
            {
                "lineage_source_id": source,
                "public_id": f"LA-{number:03d}",
            }
            for number, source in enumerate(LINEAGE_CASES, 1)
        ]
        self.assertEqual(list(mapping["case_mapping"].values()), expected)
        native_path = (
            SKILL_DIR.parents[1]
            / "evidence/ports/logic-audit/eval-cases.native.json"
        )
        native_cases = json.loads(native_path.read_text(encoding="utf-8"))["cases"]
        public_cases = {
            case["id"]: case for case in load("evals/cases.json")["cases"]
        }
        for source_case in native_cases:
            mapped = mapping["case_mapping"][source_case["id"]]
            public_case = public_cases[mapped["public_id"]]
            self.assertEqual(public_case["source_id"], mapped["lineage_source_id"])
            self.assertEqual(public_case["prompt"], source_case["input"])
            self.assertEqual(public_case["required"], source_case["expect"])
            self.assertEqual(public_case["veto"], source_case["forbid"])

    def test_portable_skill_preserves_required_order_and_boundaries(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        ordered = [
            "`always-current-datetime`",
            "`starting-point`",
            "`outcome-bounded-work`",
        ]
        positions = [skill.index(token) for token in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertLess(skill.index("Normalize terms"),
                        skill.index("dependency map"))
        self.assertIn("rendered browser capability", skill)
        self.assertNotIn("computer" + "-user", skill)


if __name__ == "__main__":
    unittest.main()
