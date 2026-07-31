"""Lineage tests for the source-to-port meaning contract."""
import hashlib
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
BASELINE_PUBLIC_SHA256 = "c1889016d6e33868f3346986336dd5938a089a8af96ffcc9cb9ee280a1766a16"
CURRENT_PUBLIC_VERSION = "0.2.2"
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


def load(relative: str) -> dict:
    return json.loads((SKILL_DIR / relative).read_text(encoding="utf-8"))


def assert_interval_coverage(test_case, intervals, valid_ids):
    test_case.assertEqual(intervals[0]["start_second"], 0)
    test_case.assertEqual(intervals[-1]["end_second_exclusive"], 3924)
    cursor = 0
    transcript_indices = set()
    for interval in intervals:
        test_case.assertEqual(interval["start_second"], cursor)
        test_case.assertGreater(interval["end_second_exclusive"], interval["start_second"])
        cursor = interval["end_second_exclusive"]
        test_case.assertIn(
            interval["classification"],
            {"operating", "claim_boundary", "mixed", "context_only"},
        )
        test_case.assertTrue(set(interval["learning_ids"]).issubset(valid_ids))
        if interval["classification"] == "context_only":
            test_case.assertEqual(interval["learning_ids"], [])
            test_case.assertTrue(interval["context_id"])
        else:
            test_case.assertTrue(interval["learning_ids"])
        transcript_indices.update(interval["transcript_segment_indices"])
    test_case.assertEqual(cursor, 3924)
    test_case.assertEqual(transcript_indices, set(range(1848)))


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

    def test_candidate_maps_every_baseline_rule_and_authorizes_each_loss(self):
        mapping = load("evals/centrality-mapping.json")
        entries = mapping["baseline_rules"]
        self.assertEqual(mapping["baseline_skill_sha256"], BASELINE_PUBLIC_SHA256)
        skill_bytes = (SKILL_DIR / "SKILL.md").read_bytes()
        self.assertEqual(mapping["candidate_skill_sha256"], hashlib.sha256(skill_bytes).hexdigest())
        self.assertEqual(mapping["coverage"]["ratio"], 1.0)
        self.assertEqual(mapping["coverage"]["unauthorized_drops"], 0)
        self.assertEqual(len(entries), mapping["coverage"]["baseline_rule_rows"])
        self.assertTrue(all(entry["review_status"] == "PASS" for entry in entries))
        dropped = [entry for entry in entries if entry["action"] == "approved_drop"]
        self.assertTrue(dropped)
        self.assertTrue(all(entry["approval_record"] for entry in dropped))
        retained = [entry for entry in entries if entry["action"] != "approved_drop"]
        self.assertTrue(all(entry["candidate_span"] != "planned" for entry in retained))

    def test_every_video_second_and_transcript_segment_is_classified(self):
        video = load("evals/video-learning-map.json")
        second_map = load("evals/video-second-map.json")
        self.assertEqual(second_map["schema"], "prime-vector-video-second-map-v1")
        self.assertEqual(second_map["video"]["video_id"], video["video"]["video_id"])
        self.assertEqual(
            second_map["video"]["transcript_full_text_sha256"],
            video["video"]["transcript_full_text_sha256"],
        )
        self.assertEqual(second_map["audit_summary"]["duration_seconds"], 3924)
        self.assertEqual(second_map["audit_summary"]["seconds_reviewed"], 3924)
        self.assertEqual(second_map["audit_summary"]["transcript_segments_reviewed"], 1848)
        self.assertEqual(second_map["audit_summary"]["material_clusters"], 25)
        self.assertEqual(second_map["audit_summary"]["unclassified_seconds"], 0)
        self.assertEqual(second_map["audit_summary"]["unclassified_segments"], 0)
        self.assertEqual(second_map["audit_summary"]["uncovered_material_segments"], 0)
        assert_interval_coverage(self, second_map["intervals"], set(video["candidate_map"]))

    def test_video_and_companion_contracts_are_fully_integrated(self):
        video = load("evals/video-learning-map.json")
        self.assertEqual(
            video["video"]["transcript_full_text_sha256"],
            "2ed6f87c5342ffd8ee1cee9cebbd7f6491b61d39acee301ca6e513947ae43ce3",
        )
        self.assertEqual(video["coverage"]["material_learning_clusters"], 25)
        self.assertEqual(video["coverage"]["missing_without_disposition"], 0)
        self.assertEqual(len(video["learnings"]), 25)
        self.assertEqual(video["candidate_coverage"], {
            "claim_boundary": 2,
            "integrated": 23,
            "missing": 0,
            "ratio": 1.0,
        })
        self.assertEqual(
            set(video["candidate_map"].values()),
            {"claim_boundary", "integrated"},
        )
        self.assertEqual(
            set(video["candidate_map"]),
            {entry["id"] for entry in video["learnings"]},
        )
        centrality = load("evals/centrality-mapping.json")
        self.assertEqual(centrality["coverage"]["video_learning_rows"], 25)
        self.assertEqual(centrality["coverage"]["companion_rows"], 9)
        self.assertTrue(all(
            row["required_disposition"] == "integrated"
            for row in centrality["companion_contract"]
        ))

    def test_public_skill_has_one_ordered_method_and_current_version(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        lineage = load("evals/source-lineage.json")
        self.assertIn(f"version: '{CURRENT_PUBLIC_VERSION}'", skill)
        self.assertEqual(lineage["public_version"], CURRENT_PUBLIC_VERSION)
        ordered = ["`starting-point`", "`always-current-date`", "`outcome-bounded-work`"]
        positions = [skill.index(token) for token in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("Workflow states are `FRAME | DRAFT | CHALLENGE | TEST | DECIDE`", skill)
        self.assertIn("Response statuses are `QUESTION | DRAFT | TEST | DONE | BLOCKED`", skill)


if __name__ == "__main__":
    unittest.main()
