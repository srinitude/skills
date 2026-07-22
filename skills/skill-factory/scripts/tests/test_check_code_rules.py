"""Tests for scripts/check_code_rules.py against real code files."""
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR, run


class TestCheckCodeRulesCli(unittest.TestCase):
    def test_help_documents_usage_and_exit_codes(self):
        result = run("check_code_rules.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        self.assertIn("exit code", result.stdout.lower())

    def test_missing_target_is_a_usage_error(self):
        result = run("check_code_rules.py")
        self.assertEqual(result.returncode, 2)


class TestCheckCodeRules(unittest.TestCase):
    def check_source(self, source, suffix=".py"):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / f"sample{suffix}"
            path.write_text(source, encoding="utf-8")
            return run("check_code_rules.py", path)

    def test_own_code_passes(self):
        result = run("check_code_rules.py", SKILL_DIR)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_small_clean_file_passes(self):
        result = self.check_source("def add(a, b):\n    return a + b\n")
        self.assertEqual(result.returncode, 0)

    def test_file_over_200_loc_fails(self):
        source = "\n".join(f"x{i} = {i}" for i in range(201)) + "\n"
        result = self.check_source(source)
        self.assertEqual(result.returncode, 1)
        self.assertIn("200", result.stdout)

    def test_function_over_30_loc_fails(self):
        lines = [f"    y{i} = {i}" for i in range(31)]
        source = "def big():\n" + "\n".join(lines) + "\n    return y0\n"
        result = self.check_source(source)
        self.assertEqual(result.returncode, 1)
        self.assertIn("big", result.stdout)

    def test_nesting_over_three_fails(self):
        source = (
            "def deep(rows):\n"
            "    for row in rows:\n"
            "        if row:\n"
            "            for cell in row:\n"
            "                if cell:\n"
            "                    print(cell)\n"
        )
        result = self.check_source(source)
        self.assertEqual(result.returncode, 1)
        self.assertIn("nesting", result.stdout)

    def test_placeholder_marker_fails(self):
        marker = "TO" + "DO"
        result = self.check_source(f"# {marker}: finish later\nx = 1\n")
        self.assertEqual(result.returncode, 1)

    def test_shell_file_over_200_loc_fails(self):
        source = "\n".join(f"echo {i}" for i in range(201)) + "\n"
        result = self.check_source(source, suffix=".sh")
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
