"""Check the same owned surface without interpreting dependency/cache content."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from variant_fixtures import package
from skill_package import inventory

CHECKERS = ["check_code_rules.py", "lint_writing.py", "check_placeholders.py"]


class TestOwnedCollection(unittest.TestCase):
    def test_dependency_and_runtime_files_are_outside_owned_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            (root / "README.md").write_text("# Example\n")
            (root / "operation.py").write_text("print(1)\n")
            before = inventory(root)
            for name in ["node_modules/vendor", ".venv/lib/vendor", ".artifacts/run", ".git/objects"]:
                folder = root / name
                folder.mkdir(parents=True)
                (folder / "bad.py").write_text("def invalid(:\n")
                (folder / "bad.md").write_text("Fo" + "ster\n")
                (folder / "bad.json").write_text('{"value": "SCAFFOLD-' + 'PLACEHOLDER"}')
            self.assertEqual(inventory(root), before)
            for checker in CHECKERS:
                result = run(checker, root)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_owned_symlinks_reject_before_external_content_is_read(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            root = base / "owned"
            root.mkdir()
            external = base / "external.md"
            external.write_text("PRIVATE_CANARY_NOT_AUTHORIZED\n")
            (root / "link.md").symlink_to(external)
            for checker in CHECKERS:
                result = run(checker, root)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("symlink", result.stdout + result.stderr)
                self.assertNotIn("PRIVATE_CANARY_NOT_AUTHORIZED", result.stdout + result.stderr)

    def test_lineage_does_not_capture_runtime_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = package(Path(temp).resolve() / "file-inventory", "user")
            artifact = root / ".artifacts" / "private-result.json"
            artifact.parent.mkdir()
            artifact.write_text('{"local": true}')
            result = run("check_lineage.py", root, "--write")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads((root / "evals/source-lineage.json").read_text())
            self.assertFalse(any(item["path"].startswith(".artifacts/") for item in data["source_files"]))


if __name__ == "__main__":
    unittest.main()
