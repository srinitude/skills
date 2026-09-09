"""Keep installed dependencies outside owned checks without hiding owned faults."""
import tempfile
import unittest
from pathlib import Path

from cli import run


class TestCheckerOwnership(unittest.TestCase):
    def test_document_checkers_exclude_dependencies_and_keep_owned_faults(self):
        for script in ["lint_writing.py", "check_placeholders.py"]:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                dependency = root / "node_modules/package"
                dependency.mkdir(parents=True)
                bad = "Delve into SCAFFOLD-" + "PLACEHOLDER.\n"
                (dependency / "README.md").write_text(bad)
                owned = root / "SKILL.md"
                owned.write_text("# Owned rule\n\nKeep its meaning.\n")
                result = run(script, root)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("checked 1 files", result.stdout)
                owned.write_text(bad)
                self.assertEqual(run(script, root).returncode, 1)

    def test_owned_document_symlink_is_rejected(self):
        for script in ["lint_writing.py", "check_placeholders.py"]:
            with self.subTest(script=script), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                (root / "real.md").write_text("# Actual file\n")
                (root / "alias.md").symlink_to(root / "real.md")
                result = run(script, root)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("unsupported package entry", result.stderr)


if __name__ == "__main__":
    unittest.main()
