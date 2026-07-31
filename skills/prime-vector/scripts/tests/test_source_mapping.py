"""Lineage tests for the source-to-port meaning contract."""
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
EXPECTED_FILES = {
    "SKILL.md": "b358ac94da13b083a6459a76e8de0262f1cb4e7e0f6be6460e80d616b02b9816",
}
EXPECTED_CASES = [
    *[f"PV-{number:03d}" for number in range(1, 13)],
    "PVV-004",
    "PVV-008",
    "PVV-009",
    "PVV-013",
    "PVV-014",
    "PVV-015",
    "PVV-016",
    "PVV-017",
    "PVV-018",
    "PVV-019",
]


def load(relative):
    return json.loads((SKILL_DIR / relative).read_text(encoding="utf-8"))


class TestSourceMapping(unittest.TestCase):
    def test_lineage_binds_the_source_file_and_all_cases(self):
        lineage = load("evals/source-lineage.json")
        files = {entry["path"]: entry["sha256"] for entry in lineage["source_files"]}
        self.assertEqual(files, EXPECTED_FILES)
        self.assertEqual(lineage["source_case_ids"], EXPECTED_CASES)

    def test_mapping_covers_every_nonblank_line_without_drop(self):
        mapping = load("evals/source-mapping.json")
        entries = mapping["entries"]
        self.assertEqual(
            mapping["coverage"],
            {
                "source_nonblank_lines": 107,
                "mapped_nonblank_lines": 107,
                "ratio": 1.0,
            },
        )
        self.assertEqual(len(entries), 107)
        self.assertNotIn("drop", {entry["action"] for entry in entries})
        self.assertTrue(all(entry["review_state"] == "approved" for entry in entries))
        self.assertTrue(all(entry["public_target"] for entry in entries))
        self.assertTrue(all(entry["evidence_target"] for entry in entries))

    def test_video_map_has_no_unclassified_material_learning(self):
        video = load("evals/video-learning-map.json")
        self.assertEqual(video["coverage"]["material_learning_clusters"], 25)
        self.assertEqual(video["coverage"]["missing_without_disposition"], 0)
        self.assertEqual(video["coverage"]["strengthen"], 10)
        self.assertEqual(len(video["learnings"]), 25)


if __name__ == "__main__":
    unittest.main()
