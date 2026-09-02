"""Tests for repository-local formatting discovery."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from standardization_format import formatter_command


class TestRepositoryFormat(unittest.TestCase):
    def test_uses_the_repository_local_prettier(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            target = repo / "skills/example"
            script = repo / "node_modules/prettier/bin/prettier.cjs"
            target.mkdir(parents=True)
            script.parent.mkdir(parents=True)
            script.write_text("", encoding="utf-8")
            (repo / ".git").mkdir()
            (repo / ".prettierrc.json").write_text("{}", encoding="utf-8")
            with patch("shutil.which", return_value="/bin/node"):
                command = formatter_command(target)
            self.assertEqual(command[0], [
                "/bin/node", str(script.resolve()), "--write", str(target.resolve())])
            self.assertEqual(command[1], repo.resolve())

    def test_skips_a_skill_without_a_repository_formatter(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "skill"
            target.mkdir()
            self.assertIsNone(formatter_command(target))


if __name__ == "__main__":
    unittest.main()
