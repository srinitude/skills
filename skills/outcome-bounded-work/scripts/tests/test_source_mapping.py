"""Lineage tests for the native-to-port meaning contract."""
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
EXPECTED_FILES = {
    "SKILL.md": "4f9b92967f57925205ece279186616cb417cc060b89ffbedafc70dffd77a8a79",
    "references/eval-cases.json": "3bab97f9a03a07e97c544113f8ada34ea699d209d74481f53e48a30f82918aa3",
}
EXPECTED_CASES = [
    "conversation-candidate-path",
    "exact-method-is-deliverable",
    "imperative-method-ambiguous",
    "better-route-drops-scope",
    "safety-rule-sounds-procedural",
    "evidence-not-recipe",
    "privacy-forbidden-outcome",
    "simple-request-no-meta-work",
    "audit-does-not-mutate",
    "mode-consistency",
]
LINEAGE_CASES = [f"NOBW-{number:03d}" for number in range(1, 11)]


def load(relative):
    return json.loads((SKILL_DIR / relative).read_text(encoding="utf-8"))


class TestSourceMapping(unittest.TestCase):
    def test_lineage_binds_every_native_file_and_case(self):
        lineage = load("evals/source-lineage.json")
        files = {entry["path"]: entry["sha256"] for entry in lineage["source_files"]}
        self.assertEqual(files, EXPECTED_FILES)
        self.assertEqual(lineage["source_case_ids"], LINEAGE_CASES)
        self.assertEqual(
            lineage["native_manifest_sha256"],
            "75d2a9fad3962caf9f1f1e05f8783522c3481e8a9c2c2d36a75899762e61a2f2",
        )

    def test_mapping_covers_every_nonblank_line_without_drop(self):
        mapping = load("evals/source-mapping.json")
        entries = mapping["entries"]
        self.assertEqual(mapping["coverage"], {
            "source_nonblank_lines": 228,
            "mapped_nonblank_lines": 228,
            "ratio": 1.0,
        })
        self.assertEqual(len(entries), 228)
        self.assertNotIn("drop", {entry["action"] for entry in entries})
        self.assertTrue(all(entry["review_state"] == "approved" for entry in entries))
        self.assertTrue(all(entry["public_target"] for entry in entries))
        self.assertTrue(all(entry["evidence_target"] for entry in entries))

    def test_case_mapping_preserves_native_ids(self):
        mapping = load("evals/source-mapping.json")
        self.assertEqual(list(mapping["case_mapping"]), EXPECTED_CASES)
        self.assertEqual(
            list(mapping["case_mapping"].values()),
            [
                {"lineage_source_id": source, "public_id": f"OBW-{number:03d}"}
                for number, source in enumerate(LINEAGE_CASES, 1)
            ],
        )


if __name__ == "__main__":
    unittest.main()
