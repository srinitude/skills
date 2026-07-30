"""Lineage tests for the native-to-port meaning contract."""
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
EXPECTED_FILES = {
    "SKILL.md": "7dd1bcbb16f862f426214b10b05e192413d6b7fcac3a9dced7ef272b25254204",
    "references/eval-contract.md": "efd3b5e05e68846e229bff376c71bf0081e831984bba1f199d7dc9578da46aa3",
    "references/eval-cases.json": "613c3c83e67f922dae4d8ed21bdd0055065cbbe42d98910b341272186866e20b",
    "scripts/current_anchor.py": "dc2e2ff4edc302ed26b2b194ab6db31c5a6badf2223f42efd2d9ef088819b68f",
}
EXPECTED_CASES = [f"ACD-{number:03d}" for number in range(1, 12)]


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
            "02a7d6cbd55194531fadde08495681fcb5f338034c19294df17424ea6b69d4c4",
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
