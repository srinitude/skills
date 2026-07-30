"""Lineage tests for the native-to-port meaning contract."""
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
EXPECTED_FILES = {
    "SKILL.md": "c11d50e7a48723c89702af27e198676528c0679578c9e000aac6e5c929bd5153",
    "references/eval-contract.md": "4d9547ebcd41ea83187c4379b2958cc01785e43d227d606fedbe03f48a3a6e05",
    "references/eval-cases.json": "4341b1d29523bb349abd31d45afcfa7f245fe0ad75c62ce88e62a0694bc516d5",
    "scripts/current_anchor.py": "dc2e2ff4edc302ed26b2b194ab6db31c5a6badf2223f42efd2d9ef088819b68f",
}
EXPECTED_CASES = [f"ACD-{number:03d}" for number in range(1, 11)]


def load(relative):
    return json.loads((SKILL_DIR / relative).read_text(encoding="utf-8"))


class TestSourceMapping(unittest.TestCase):
    def test_lineage_binds_every_native_file_and_case(self):
        lineage = load("evals/source-lineage.json")
        files = {entry["path"]: entry["sha256"]
                 for entry in lineage["source_files"]}
        self.assertEqual(files, EXPECTED_FILES)
        self.assertEqual(lineage["source_case_ids"], EXPECTED_CASES)
        self.assertEqual(
            lineage["native_manifest_sha256"],
            "682512a523d7e5a7e2ebf4b8a4854d1067957575c37ff29a456c8331821c773b",
        )

    def test_mapping_has_no_drop_and_covers_every_source_section(self):
        mapping = load("evals/source-mapping.json")
        self.assertEqual(mapping["source_files"], list(EXPECTED_FILES))
        self.assertEqual(mapping["source_case_ids"], EXPECTED_CASES)
        self.assertEqual(mapping["coverage"], 1.0)
        self.assertNotIn("drop", {entry["action"] for entry in mapping["clauses"]})
        covered = {entry["source_path"] for entry in mapping["clauses"]}
        self.assertEqual(covered, set(EXPECTED_FILES))


if __name__ == "__main__":
    unittest.main()
