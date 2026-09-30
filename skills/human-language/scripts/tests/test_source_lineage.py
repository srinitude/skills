"""Lineage tests: every public file and case traces to its native source."""
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", ".claude", ".markdown-chain", ".artifacts", ".venv", "__pycache__"}
SKIP_FILES = {".DS_Store", ".gitattributes", ".gitignore", "markdown-chain.yml"}


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def package_files():
    found = []
    for path in sorted(ROOT.rglob("*")):
        parts = set(path.relative_to(ROOT).parts)
        if path.is_file() and not parts & SKIP_DIRS and path.name not in SKIP_FILES and path.suffix != ".pyc":
            found.append(str(path.relative_to(ROOT)))
    return found


class TestSourceLineage(unittest.TestCase):
    def test_every_public_file_has_lineage(self):
        listed = [entry["path"] for entry in load("evals/source-lineage.json")["public_files"]]
        expected = [path for path in package_files() if path != "evals/source-lineage.json"]
        self.assertEqual(sorted(listed), expected)

    def test_case_ids_match_cases(self):
        lineage = load("evals/source-lineage.json")
        ids = [case["id"] for case in load("evals/cases.json")["cases"]]
        self.assertEqual(lineage["active_case_ids"], ids)
        self.assertEqual(lineage["source_case_ids"], ids)

    def test_native_sources_are_hashed(self):
        lineage = load("evals/source-lineage.json")
        for entry in lineage["source_files"]:
            self.assertRegex(entry["sha256"], "^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
