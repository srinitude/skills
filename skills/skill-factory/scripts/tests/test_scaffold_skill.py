"""Tests for scripts/scaffold_skill.py: scaffolds must pass every check."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cli import run

DESCRIPTION = "Use when a demo skill is needed for scaffold tests."


def scaffold(dest, name="demo-skill", description=DESCRIPTION, *extra):
    return run("scaffold_skill.py", "--name", name,
               "--description", description, "--dest", dest, *extra)


class TestScaffoldCli(unittest.TestCase):
    def test_help_documents_usage_and_exit_codes(self):
        result = run("scaffold_skill.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        self.assertIn("exit code", result.stdout.lower())

    def test_invalid_name_is_an_input_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = scaffold(tmp, name="Bad_Name")
        self.assertEqual(result.returncode, 2)
        self.assertIn("name", result.stdout.lower())

    def test_description_must_state_when_to_use(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = scaffold(tmp, description="Formats reports.")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Use when", result.stdout)

    def test_existing_target_without_force_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "demo-skill").mkdir()
            result = scaffold(tmp)
        self.assertEqual(result.returncode, 1)


class TestScaffoldOutput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        result = scaffold(cls.tmp.name)
        assert result.returncode == 0, result.stdout + result.stderr
        cls.skill = Path(cls.tmp.name) / "demo-skill"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_layout_is_complete(self):
        for rel in ["SKILL.md", "mise.toml", ".github/workflows/ci.yml",
                    "references/generation-contract.md", "assets",
                    "scripts/skill_info.py", "scripts/tests/test_scripts.py",
                    "scripts/tests/test_ci_contract.py",
                    "examples/example-first-run.md",
                    "scripts/check_placeholders.py",
                    "evals/evals.json", "evals/trigger-queries.json"]:
            self.assertTrue((self.skill / rel).exists(), f"missing {rel}")

    def test_body_points_at_examples_with_a_load_condition(self):
        body = (self.skill / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("examples/", body)
        self.assertIn("examples/example-first-run.md", body)

    def test_untouched_scaffold_fails_the_placeholder_gate(self):
        result = run("check_placeholders.py", self.skill)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("SKILL.md", result.stdout)
        self.assertIn("examples/example-first-run.md", result.stdout)
        self.assertIn("evals.json", result.stdout)

    def test_seed_evals_do_not_assert_scaffolder_behavior(self):
        text = (self.skill / "evals" / "evals.json").read_text(
            encoding="utf-8").lower()
        for leftover in ["skill_info.py", "help, info, and check"]:
            self.assertNotIn(leftover, text)

    def test_generated_skill_passes_validation(self):
        result = run("validate_skill.py", self.skill)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_generated_docs_pass_the_writing_lint(self):
        result = run("lint_writing.py", self.skill)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_generated_code_passes_code_rules(self):
        result = run("check_code_rules.py", self.skill)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_generated_evals_pass_schema_checks(self):
        result = run("check_evals.py", self.skill)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_generated_tests_pass(self):
        cmd = [sys.executable, "-m", "unittest", "discover",
               "-s", "scripts/tests", "-p", "test_*.py"]
        proc = subprocess.run(cmd, cwd=self.skill, capture_output=True,
                              text=True, timeout=180)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_no_platform_or_model_names_in_output(self):
        blob = ""
        for path in sorted(self.skill.rglob("*")):
            if path.is_file():
                blob += path.read_text(encoding="utf-8", errors="ignore")
        halves = [("her", "mes"), ("cla", "ude"), ("co", "dex"),
                  ("openc", "ode"),
                  ("copi", "lot"), ("cur", "sor"), ("gem", "ini"),
                  ("g", "pt"), ("anthro", "pic"), ("open", "ai"),
                  ("perple", "xity")]
        for head, tail in halves:
            word = head + tail
            self.assertNotIn(word, blob.lower(), f"found {word}")


if __name__ == "__main__":
    unittest.main()
