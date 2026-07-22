"""Tests for scripts/validate_skill.py against real skill directories."""
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR, run

GOOD_HEADER = (
    '---\nname: sample-skill\n'
    'description: "Use when testing the validator."\n'
    'license: MIT\n---\n'
)


def write_skill(root, name, content):
    skill = Path(root) / name
    skill.mkdir()
    (skill / "SKILL.md").write_text(content, encoding="utf-8")
    return skill


class TestValidateSkillCli(unittest.TestCase):
    def test_help_documents_usage_and_exit_codes(self):
        result = run("validate_skill.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        self.assertIn("exit code", result.stdout.lower())

    def test_missing_path_is_a_usage_error(self):
        result = run("validate_skill.py")
        self.assertEqual(result.returncode, 2)

    def test_nonexistent_directory_is_an_input_error(self):
        result = run("validate_skill.py", "/no/such/skill-dir")
        self.assertEqual(result.returncode, 2)


class TestValidateSkillRules(unittest.TestCase):
    def test_this_skill_passes(self):
        result = run("validate_skill.py", SKILL_DIR)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_content_before_frontmatter_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", "intro\n" + GOOD_HEADER)
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1)
        self.assertIn("frontmatter", result.stdout.lower())

    def test_name_directory_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "other-name", GOOD_HEADER + "Body.\n")
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1)
        self.assertIn("name", result.stdout.lower())

    def test_unknown_top_level_field_fails(self):
        header = GOOD_HEADER.replace("license: MIT", "owner: someone")
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", header + "Body.\n")
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1)
        self.assertIn("owner", result.stdout)

    def test_missing_support_directories_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", GOOD_HEADER + "Body.\n")
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1)
        for missing in ["references", "assets", "scripts", "evals",
                        "scripts/tests"]:
            self.assertIn(missing, result.stdout)

    def test_scripts_without_tests_directory_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", GOOD_HEADER + "Body.\n")
            (skill / "scripts").mkdir()
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1)
        self.assertIn("scripts/tests", result.stdout)

    def test_body_must_reference_scripts_tests(self):
        body = ("Read references/ and assets/ and evals/ and run the\n"
                "checks in scripts/ when anything changes.\n")
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", GOOD_HEADER + body)
            for name in ["references", "assets", "scripts",
                         "scripts/tests", "evals"]:
                (skill / name).mkdir(parents=True, exist_ok=True)
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1)
        self.assertIn("scripts/tests/", result.stdout)

    def test_deep_relative_path_in_body_fails(self):
        body = "Read references/a/b/c.md for details.\n"
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", GOOD_HEADER + body)
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1)
        self.assertIn("references/a/b/c.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
