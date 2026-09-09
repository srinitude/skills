"""Tests for repository-local formatting discovery."""
import tempfile
import unittest
from pathlib import Path
import shutil

from standardization_test_support import native_formatter

from standardization_format import formatter_command


class TestRepositoryFormat(unittest.TestCase):
    def test_uses_the_repository_local_prettier(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp).resolve()
            target = repo / "skills/example"
            target.mkdir(parents=True)
            script = native_formatter(repo)
            command = formatter_command(target)
            self.assertEqual(command[0], [
                shutil.which("node"), str(script), "--write", str(target.resolve())])
            self.assertEqual(command[1], repo.resolve())

    def test_skips_a_skill_without_a_repository_formatter(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "skill"
            target.mkdir()
            self.assertIsNone(formatter_command(target))


if __name__ == "__main__":
    unittest.main()
