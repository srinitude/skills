"""Tests for scripts/lint_writing.py against real markdown files."""
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR, run


class TestLintWritingCli(unittest.TestCase):
    def test_help_documents_usage_and_exit_codes(self):
        result = run("lint_writing.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        self.assertIn("exit code", result.stdout.lower())

    def test_missing_target_is_a_usage_error(self):
        result = run("lint_writing.py")
        self.assertEqual(result.returncode, 2)


class TestLintWritingRules(unittest.TestCase):
    def lint_text(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text(text, encoding="utf-8")
            return run("lint_writing.py", path)

    def test_clean_prose_passes(self):
        result = self.lint_text(
            "# How does the check work?\n\n"
            "Run the script on a folder. It reads every markdown file, "
            "then prints one line per problem. Short and blunt.\n"
        )
        self.assertEqual(result.returncode, 0)

    def test_em_dash_fails(self):
        result = self.lint_text("A pause \u2014 then the rest.\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("em dash", result.stdout)

    def test_banned_word_fails(self):
        result = self.lint_text("We delve into the details here.\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("delve", result.stdout)

    def test_banned_frame_fails(self):
        result = self.lint_text("It is important to note that tests run.\n")
        self.assertEqual(result.returncode, 1)

    def test_latin_abbreviation_fails(self):
        result = self.lint_text("Use plain words, e.g. this one.\n")
        self.assertEqual(result.returncode, 1)

    def test_deep_heading_fails(self):
        result = self.lint_text("#### Too deep a heading\n\nBody text.\n")
        self.assertEqual(result.returncode, 1)

    def test_report_names_file_and_line(self):
        result = self.lint_text("Line one is fine.\n\nWe delve here.\n")
        self.assertIn("doc.md:3", result.stdout)


class TestOneLineBlocks(unittest.TestCase):
    def lint_text(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.md"
            path.write_text(text, encoding="utf-8")
            return run("lint_writing.py", path)

    def test_hard_wrapped_paragraph_fails(self):
        result = self.lint_text("First half of a sentence\n"
                                "continues on a second line.\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("doc.md:2", result.stdout)
        self.assertIn("one line", result.stdout)

    def test_single_line_paragraph_of_any_length_passes(self):
        result = self.lint_text("word " * 80 + "end.\n")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_list_item_continuation_fails(self):
        result = self.lint_text("- A list item that\n"
                                "  continues on the next line.\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("doc.md:2", result.stdout)

    def test_separate_list_items_pass(self):
        result = self.lint_text("- First item, short.\n"
                                "- Second item, also short.\n")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_numbered_items_pass(self):
        result = self.lint_text("1. First step, run the check.\n"
                                "2. Second step, read the output.\n")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_blank_lines_between_blocks_pass(self):
        result = self.lint_text("Paragraph one stays whole.\n\n"
                                "Paragraph two stays whole.\n")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_frontmatter_is_exempt(self):
        text = ("---\nname: sample\ndescription: \"Use when testing.\"\n"
                "---\n\nBody sits on one line.\n")
        result = self.lint_text(text)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_headings_and_tables_are_exempt(self):
        text = ("# Title\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n"
                "| 3 | 4 |\n")
        result = self.lint_text(text)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_fenced_code_is_exempt(self):
        text = "```\ncode line one\ncode line two\ncode line three\n```\n"
        result = self.lint_text(text)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_indented_code_is_exempt(self):
        text = "A lead-in line stands alone.\n\n    code one\n    code two\n"
        result = self.lint_text(text)
        self.assertEqual(result.returncode, 0, result.stdout)


class TestOwnDocsPass(unittest.TestCase):
    def test_every_markdown_file_in_this_skill_passes(self):
        result = run("lint_writing.py", SKILL_DIR)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
