"""Lineage tests for the native-to-public timebox contract."""
import hashlib
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
EVIDENCE_PATHS = {
    "SKILL.md": "SKILL.native.md",
    "references/eval-cases.json": "references/eval-cases.json",
}


def load(relative):
    return json.loads((SKILL_DIR / relative).read_text(encoding="utf-8"))


class TestSourceLineage(unittest.TestCase):
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


class TestSourceMapping(unittest.TestCase):
    def test_mapping_has_no_loss_or_pending_review(self):
        entries = load("evals/source-mapping.json")["entries"]
        self.assertNotIn("drop", {entry["action"] for entry in entries})
        self.assertEqual({entry["review_state"] for entry in entries},
                         {"approved"})
        self.assertTrue(all(entry["evidence_target"] for entry in entries))

    def test_mapping_binds_native_lines_to_public_text(self):
        entries = load("evals/source-mapping.json")["entries"]
        native_root = SKILL_DIR.parents[1] / "evidence" / "ports" / "timebox" / "native"
        source_lines = {
            source: (native_root / EVIDENCE_PATHS[source]).read_text(encoding="utf-8").splitlines()
            for source in EXPECTED_FILES
        }
        for entry in entries:
            source = source_lines[entry["source_path"]][entry["source_line"] - 1]
            self.assertTrue(source.strip())
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(),
                             entry["source_text_sha256"])
            if entry["action"] == "clarify":
                self.assertEqual(entry["public_targets"], [])
                self.assertIn("portable omission", entry["preservation_judgment"])
                continue
            self.assertTrue(entry["public_targets"])
            self.assertTrue(entry["public_assertions"])
            for assertion in entry["public_assertions"]:
                self.assertIn(assertion["target"], entry["public_targets"])
                public = (SKILL_DIR / assertion["target"]).read_text(encoding="utf-8")
                self.assertIn(assertion["contains"], public)


class TestSourceCases(unittest.TestCase):
    def test_public_cases_preserve_native_acceptance(self):
        native = json.loads((SKILL_DIR.parents[1] / "evidence" / "ports" /
                             "timebox" / "native" / "references" /
                             "eval-cases.json").read_text(encoding="utf-8"))
        public = load("evals/cases.json")
        self.assertEqual(public["acceptance"], native["acceptance"])
        self.assertEqual(public["backlink"], native["backlink"])
        projected = [{"id": case["source_id"], "prompt": case["prompt"],
                      "required": case["required"], "forbidden": case["veto"]}
                     for case in public["cases"]]
        self.assertEqual(projected, native["cases"])


if __name__ == "__main__":
    unittest.main()
