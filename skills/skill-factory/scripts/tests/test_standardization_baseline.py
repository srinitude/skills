"""Tests for explicit Git-baseline recovery before factory reapplication."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cli import SCRIPTS

sys.path.insert(0, str(SCRIPTS))
from standardization_baseline import restore_tracked_text


class TestBaselineRecovery(unittest.TestCase):
    def test_restores_markdown_and_mapping_without_touching_code(self):
        with tempfile.TemporaryDirectory() as temp:
            repo, target = Path(temp), Path(temp) / "skills" / "clock"
            target.mkdir(parents=True)
            (target / "evals").mkdir()
            (target / "SKILL.md").write_text("original\n")
            (target / "evals/source-mapping.json").write_text("{}\n")
            (target / "tool.py").write_text("original code\n")
            self.commit(repo)
            for path in [target / "SKILL.md", target / "evals/source-mapping.json",
                         target / "tool.py"]:
                path.write_text("changed\n")
            restore_tracked_text(target)
            self.assertEqual((target / "SKILL.md").read_text(), "original\n")
            self.assertEqual((target / "evals/source-mapping.json").read_text(), "{}\n")
            self.assertEqual((target / "tool.py").read_text(), "changed\n")

    def commit(self, repo):
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repo), "-c", "user.name=Test",
                        "-c", "user.email=test@example.com", "commit", "-qm", "base"], check=True)


if __name__ == "__main__":
    unittest.main()
