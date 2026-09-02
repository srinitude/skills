"""Tests for the Mise-owned existing-skill target checks."""
import tempfile
import unittest
from pathlib import Path

from cli import run


class TestCheckTargetCli(unittest.TestCase):
    def test_help_documents_usage_and_exit_codes(self):
        result = run("check_target.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        self.assertIn("exit code", result.stdout.lower())

    def test_missing_target_is_usage_error(self):
        result = run("check_target.py", "validate")
        self.assertEqual(result.returncode, 2)

    def test_unknown_mode_is_usage_error(self):
        result = run("check_target.py", "unknown", ".")
        self.assertEqual(result.returncode, 2)


class TestCheckTargetBehavior(unittest.TestCase):
    def test_validate_runs_every_static_contract(self):
        result = run("check_target.py", "validate", Path(__file__).parents[2])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in ["validate_skill", "lint_writing", "check_code_rules",
                     "check_placeholders", "check_improvement_contract"]:
            self.assertIn(name, result.stdout)

    def test_eval_runs_schema_contract(self):
        result = run("check_target.py", "eval", Path(__file__).parents[2])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("check_evals", result.stdout)

    def test_non_skill_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            result = run("check_target.py", "validate", temp)
        self.assertEqual(result.returncode, 1)

    def test_target_symlink_fails_before_any_checker_runs(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            target = base / "sample"
            target.mkdir()
            (target / "SKILL.md").write_text("external", encoding="utf-8")
            linked = base / "linked"
            linked.symlink_to(target, target_is_directory=True)
            result = run("check_target.py", "validate", linked)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("symlink", result.stdout.lower())
        self.assertNotIn("[validate_skill]", result.stdout)


if __name__ == "__main__":
    unittest.main()
