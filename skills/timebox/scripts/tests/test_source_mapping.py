"""Lineage tests for the native-to-public timebox contract."""
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
EXPECTED_FILES = {
    "SKILL.md": "08109011d0ab6b98102768e4e9644059bf3aad8c600391715b5d03d1a025ae40",
    "references/eval-cases.json": "9f341462234e7365ac5f4895881035df07d0e7a8912aab7153788b27ca95a82f",
}
EXPECTED_CASES = [f"TB-{number:03d}" for number in range(1, 7)]
EXPECTED_PACKET = "b2c2f242431a613f7001db2e9fef5d72e24b8899bceddb39e2452ad3d96994d5"


def load(relative):
    return json.loads((SKILL_DIR / relative).read_text(encoding="utf-8"))


class TestSourceMapping(unittest.TestCase):
    def test_lineage_binds_every_native_file_and_case(self):
        lineage = load("evals/source-lineage.json")
        files = {entry["path"]: entry["sha256"]
                 for entry in lineage["source_files"]}
        self.assertEqual(files, EXPECTED_FILES)
        self.assertEqual(lineage["source_case_ids"], EXPECTED_CASES)
        self.assertEqual(lineage["native_manifest_sha256"], EXPECTED_PACKET)

    def test_mapping_covers_every_nonblank_line(self):
        mapping = load("evals/source-mapping.json")
        self.assertEqual(mapping["source_files"], list(EXPECTED_FILES))
        self.assertEqual(mapping["source_case_ids"], EXPECTED_CASES)
        self.assertEqual(mapping["coverage"], {
            "source_nonblank_lines": 159,
            "mapped_nonblank_lines": 159,
            "ratio": 1,
        })
        self.assertEqual(len(mapping["entries"]), 159)

    def test_mapping_has_no_loss_or_pending_review(self):
        entries = load("evals/source-mapping.json")["entries"]
        self.assertNotIn("drop", {entry["action"] for entry in entries})
        self.assertEqual({entry["review_state"] for entry in entries},
                         {"approved"})
        self.assertTrue(all(entry["public_targets"] for entry in entries))
        self.assertTrue(all(entry["evidence_target"] for entry in entries))


if __name__ == "__main__":
    unittest.main()
