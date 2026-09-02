"""Tests for canonical factory support-file propagation."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_standardize_registry_skill import profile, write_target


class TestCanonicalCopy(unittest.TestCase):
    def test_apply_refreshes_the_writing_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            checker = root / "scripts/lint_writing.py"
            checker.write_text("print('stale')\n", encoding="utf-8")
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(profile()), encoding="utf-8")
            result = run("standardize_registry_skill.py", root, "--profile",
                         profile_path, "--apply")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("mise_section_lines", checker.read_text())


if __name__ == "__main__":
    unittest.main()
