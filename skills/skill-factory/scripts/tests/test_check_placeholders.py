"""Tests for scripts/check_placeholders.py, the scaffold sentinel gate."""
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR, run

TOKEN = "SCAFFOLD-" + "PLACEHOLDER"


def write(root, name, text):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class TestCheckPlaceholdersCli(unittest.TestCase):
    def test_help_documents_usage_and_exit_codes(self):
        result = run("check_placeholders.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        self.assertIn("exit code", result.stdout.lower())

    def test_missing_target_is_a_usage_error(self):
        result = run("check_placeholders.py")
        self.assertEqual(result.returncode, 2)

    def test_nonexistent_target_is_an_input_error(self):
        result = run("check_placeholders.py", "/no/such/skill-dir")
        self.assertEqual(result.returncode, 2)


class TestCheckPlaceholdersRules(unittest.TestCase):
    def test_this_skill_passes(self):
        result = run("check_placeholders.py", SKILL_DIR)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_sentinel_token_in_markdown_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, "SKILL.md", "Intro line.\n\n" + TOKEN + " rewrite me.\n")
            result = run("check_placeholders.py", tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("SKILL.md:3", result.stdout)

    def test_sentinel_inside_a_code_fence_passes(self):
        text = "A worked example quotes real output.\n\n```\n" + TOKEN + \
            " SKILL.md:14\n```\n"
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, "examples/example-one.md", text)
            result = run("check_placeholders.py", tmp)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_sentinel_in_json_fails(self):
        body = '{"evals": [{"prompt": "' + TOKEN + ' real request"}]}\n'
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, "evals/evals.json", body)
            result = run("check_placeholders.py", tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("evals.json:1", result.stdout)

    def test_unfilled_template_token_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, "SKILL.md", "The {{NAME}} skill counts lines.\n")
            result = run("check_placeholders.py", tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("{{NAME}}", result.stdout)

    def test_named_redaction_placeholder_passes(self):
        text = "Replace the secret with a named placeholder like {{API_KEY}}.\n"
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, "SKILL.md", text)
            result = run("check_placeholders.py", tmp)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_boilerplate_sentence_fails(self):
        text = "Replace this paragraph with two sentences on the result.\n"
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, "SKILL.md", text)
            result = run("check_placeholders.py", tmp)
        self.assertEqual(result.returncode, 1)

    def test_assets_templates_are_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, "assets/skill-template.md", TOKEN + " stays here.\n")
            result = run("check_placeholders.py", tmp)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_authored_skill_passes(self):
        text = "# line-budget\n\nThe skill counts lines and names the file.\n"
        with tempfile.TemporaryDirectory() as tmp:
            write(tmp, "SKILL.md", text)
            write(tmp, "evals/evals.json", '{"skill_name": "line-budget"}\n')
            result = run("check_placeholders.py", tmp)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("0 placeholders", result.stdout)


if __name__ == "__main__":
    unittest.main()
