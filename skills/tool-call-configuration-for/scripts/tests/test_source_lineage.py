"""Current-byte source-lineage checks for this package."""
import hashlib
import json
import pathlib
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[2]
LINEAGE = SKILL / "evals" / "source-lineage.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_paths():
    return sorted(path.relative_to(SKILL).as_posix() for path in SKILL.rglob("*")
                  if path.is_file() and path != LINEAGE
                  and "__pycache__" not in path.parts and path.name != ".DS_Store")


class TestSourceLineage(unittest.TestCase):
    def test_lineage_matches_current_public_bytes_and_cases(self):
        data = json.loads(LINEAGE.read_text(encoding="utf-8"))
        paths = public_paths()
        public = [row["path"] for row in data["public_files"]]
        sources = {row["path"]: row["sha256"] for row in data["source_files"]}
        self.assertEqual(public, paths)
        self.assertEqual(sorted(sources), paths)
        self.assertEqual(sources, {name: digest(SKILL / name) for name in paths})
        cases = json.loads((SKILL / "evals" / "cases.json").read_text())
        self.assertEqual(data["source_case_ids"],
                         sorted(case["id"] for case in cases["cases"]))
        self.assertEqual(data["public_version"], "0.1.0")
        payload = "".join(f"{row['path']}\0{row['sha256']}\n"
                          for row in data["source_files"])
        self.assertEqual(data["native_manifest_sha256"],
                         hashlib.sha256(payload.encode()).hexdigest())


if __name__ == "__main__":
    unittest.main()
