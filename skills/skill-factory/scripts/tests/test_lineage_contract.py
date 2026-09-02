"""Tests for current, deterministic source-lineage evidence."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR, run


class TestLineageContract(unittest.TestCase):
    def test_help_documents_usage_and_exit_codes(self):
        result = run("check_lineage.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        self.assertIn("exit code", result.stdout.lower())

    def test_refreshed_lineage_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evals").mkdir()
            (root / "SKILL.md").write_text(
                "---\nname: sample\ndescription: \"Use when testing.\"\n"
                "metadata:\n  version: \"1.0.0\"\n---\n", encoding="utf-8")
            cases = {"cases": [{"id": "CASE-1", "source_id": "CASE-1"}]}
            (root / "evals" / "cases.json").write_text(
                json.dumps(cases), encoding="utf-8")
            refreshed = run("check_lineage.py", root, "--write")
            result = run("check_lineage.py", root)
        self.assertEqual(refreshed.returncode, 0, refreshed.stdout)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_stale_public_version_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evals").mkdir()
            (root / "SKILL.md").write_text(
                "---\nname: sample\ndescription: \"Use when testing.\"\n"
                "metadata:\n  version: \"2.0.0\"\n---\n", encoding="utf-8")
            lineage = {
                "schema_version": 1,
                "public_version": "1.0.0",
                "native_version": "1.0.0",
                "native_manifest_sha256": "0" * 64,
                "public_files": [],
                "source_files": [],
                "source_case_ids": ["CASE-1"],
            }
            path = root / "evals" / "source-lineage.json"
            path.write_text(json.dumps(lineage), encoding="utf-8")
            cases = {"cases": [{"id": "CASE-1", "source_id": "CASE-1"}]}
            (root / "evals" / "cases.json").write_text(
                json.dumps(cases), encoding="utf-8")
            result = run("check_lineage.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("public_version", result.stdout)

    def test_generation_contract_uses_portable_name_grammar(self):
        contract = (SKILL_DIR / "references" / "generation-contract.md")
        text = contract.read_text(encoding="utf-8")
        self.assertIn("^[a-z0-9]+(?:-[a-z0-9]+)*$", text)
        self.assertNotIn("[a-z0-9._-]*", text)

    def test_runtime_trees_are_excluded_from_lineage(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_minimum(root)
            for relative in [".mise/state.json", "node_modules/pkg/index.js"]:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("runtime", encoding="utf-8")
            result = run("check_lineage.py", root, "--write")
            lineage = json.loads(
                (root / "evals/source-lineage.json").read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stdout)
        paths = [item["path"] for item in lineage["source_files"]]
        self.assertFalse(any(path.startswith((".mise/", "node_modules/"))
                             for path in paths))

    def test_lineage_rejects_external_file_symlinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "sample"
            root.mkdir()
            self.write_minimum(root)
            external = base / "private.txt"
            external.write_text("private", encoding="utf-8")
            (root / "linked.txt").symlink_to(external)
            result = run("check_lineage.py", root, "--write")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("linked.txt", result.stdout)

    def test_lineage_rejects_a_symlinked_skill_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "sample"
            root.mkdir()
            self.write_minimum(root)
            linked = base / "linked-sample"
            linked.symlink_to(root, target_is_directory=True)
            result = run("check_lineage.py", linked, "--write")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("symlink", result.stdout.lower())

    def write_minimum(self, root):
        (root / "evals").mkdir()
        (root / "SKILL.md").write_text(
            "---\nname: sample\ndescription: \"Use when testing.\"\n"
            "metadata:\n  version: \"1.0.0\"\n---\n", encoding="utf-8")
        cases = {"cases": [{"id": "CASE-1", "source_id": "CASE-1"}]}
        (root / "evals/cases.json").write_text(
            json.dumps(cases), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
