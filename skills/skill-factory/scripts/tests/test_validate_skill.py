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

    def test_opening_frontmatter_fence_must_occupy_its_line(self):
        malformed = GOOD_HEADER.replace("---\n", "---junk\n", 1)
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", malformed + "Body.\n")
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("frontmatter", result.stdout.lower())

    def test_name_directory_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "other-name", GOOD_HEADER + "Body.\n")
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1)
        self.assertIn("name", result.stdout.lower())

    def test_name_uses_portable_hyphen_only_grammar(self):
        for name in ["sample_skill", "sample.skill", "sample--skill"]:
            header = GOOD_HEADER.replace("sample-skill", name)
            with tempfile.TemporaryDirectory() as tmp:
                skill = write_skill(tmp, name, header + "Body.\n")
                result = run("validate_skill.py", skill)
            self.assertEqual(result.returncode, 1, name)
            self.assertIn("lowercase", result.stdout.lower())

    def test_unknown_top_level_field_fails(self):
        header = GOOD_HEADER.replace("license: MIT", "owner: someone")
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", header + "Body.\n")
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1)
        self.assertIn("owner", result.stdout)

    def test_malformed_yaml_frontmatter_fails(self):
        header = GOOD_HEADER.replace(
            "license: MIT", 'metadata:\n  version: ["unclosed"')
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", header + self.body())
            self.add_layout(skill)
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("yaml", result.stdout.lower())

    def test_duplicate_frontmatter_keys_fail(self):
        header = GOOD_HEADER.replace(
            "description:", "description: \"Use when wrong.\"\ndescription:")
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", header + self.body())
            self.add_layout(skill)
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("duplicate", result.stdout.lower())

    def test_non_string_name_fails_without_traceback(self):
        header = GOOD_HEADER.replace("name: sample-skill", "name: 12")
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", header + self.body())
            self.add_layout(skill)
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("name", result.stdout.lower())

    def test_unhashable_yaml_key_fails_without_traceback(self):
        header = GOOD_HEADER.replace("license: MIT", "? [bad, key]\n: value")
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", header + self.body())
            self.add_layout(skill)
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("yaml", result.stdout.lower())

    def test_missing_support_directories_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", GOOD_HEADER + "Body.\n")
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1)
        for missing in ["references", "assets", "examples", "scripts",
                        "evals", "scripts/tests"]:
            self.assertIn(missing, result.stdout)

    def test_scripts_without_tests_directory_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", GOOD_HEADER + "Body.\n")
            (skill / "scripts").mkdir()
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1)
        self.assertIn("scripts/tests", result.stdout)

    def test_body_need_not_reference_implementation_directories(self):
        body = ("Read references/ and assets/ and examples/ and evals/ and\n"
                "run the checks in scripts/ when anything changes.\n")
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", GOOD_HEADER + body)
            for name in ["references", "assets", "examples", "scripts",
                         "scripts/tests", "evals"]:
                (skill / name).mkdir(parents=True, exist_ok=True)
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("body never references scripts", result.stdout)

    def test_missing_examples_directory_is_reported(self):
        body = ("Read references/ and assets/ and evals/ and run the\n"
                "checks in scripts/tests/ and scripts/ when anything changes.\n")
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", GOOD_HEADER + body)
            for name in ["references", "assets", "scripts",
                         "scripts/tests", "evals"]:
                (skill / name).mkdir(parents=True, exist_ok=True)
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1)
        self.assertIn("examples/", result.stdout)

    def test_deep_relative_path_in_body_fails(self):
        body = "Read references/a/b/c.md for details.\n"
        with tempfile.TemporaryDirectory() as tmp:
            skill = write_skill(tmp, "sample-skill", GOOD_HEADER + body)
            result = run("validate_skill.py", skill)
        self.assertEqual(result.returncode, 1)
        self.assertIn("references/a/b/c.md", result.stdout)

    def body(self):
        return "Read references/, assets/, examples/, and evals/.\n"

    def add_layout(self, skill):
        for name in ["references", "assets", "examples", "scripts/tests",
                     "evals"]:
            (skill / name).mkdir(parents=True, exist_ok=True)
        (skill / "evals/evals.json").write_text("{}", encoding="utf-8")
        (skill / "mise.toml").write_text("", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
