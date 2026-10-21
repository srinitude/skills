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

def _TestLintWritingRules_lint_text(self, text):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "doc.md"
        path.write_text(text, encoding="utf-8")
        return run("lint_writing.py", path)

def check_text(self, text, expected):
    result = self.lint_text(text)
    self.assertEqual(result.returncode, expected, result.stdout)

def _TestLintWritingRules_test_clean_prose_passes(self):
    self.check_text('# How does the check work?\n\nRun the script on a folder. It reads every markdown file, then prints one line per problem. Short and blunt.\n', 0)

def _TestLintWritingRules_test_em_dash_fails(self):
    result = self.lint_text("A pause \u2014 then the rest.\n")
    self.assertEqual(result.returncode, 1)
    self.assertIn("em dash", result.stdout)

def _TestLintWritingRules_test_banned_word_fails(self):
    result = self.lint_text("We delve into the details here.\n")
    self.assertEqual(result.returncode, 1)
    self.assertIn("delve", result.stdout)

def _TestLintWritingRules_test_banned_frame_fails(self):
    self.check_text('It is important to note that tests run.\n', 1)

def _TestLintWritingRules_test_phrase_boundaries_preserve_words_and_reject_actual_frames(self):
    for text in ['Unknown causality does not justify adoption.', 'The knot justifies inspection.']:
        result = self.lint_text(text + "\n")
        self.assertEqual(result.returncode, 0, result.stdout)
    for text in ['Not just speed matters.', 'It is NOT JUST speed.', 'Certainly!', '(not only) speed.']:
        result = self.lint_text(text + "\n")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("banned frame", result.stdout)

def _TestLintWritingRules_test_latin_abbreviation_fails(self):
    self.check_text('Use plain words, e.g. this one.\n', 1)

def _TestLintWritingRules_test_deep_heading_fails(self):
    self.check_text('#### Too deep a heading\n\nBody text.\n', 1)

def _TestLintWritingRules_test_report_names_file_and_line(self):
    result = self.lint_text("Line one is fine.\n\nWe delve here.\n")
    self.assertIn("doc.md:3", result.stdout)

def _TestLintWritingRules_test_markdown_cannot_reference_script_paths(self):
    result = self.lint_text("Open scripts/check.py and run it.\n")
    self.assertEqual(result.returncode, 1)
    self.assertIn("Mise task", result.stdout)

def _TestLintWritingRules_test_linked_implementation_owner_preserves_public_route(self):
    self.check_text('Run `mise run validate`.\n\nInspect [the validator](scripts/check.py) for its predicate.\n', 0)

def _TestLintWritingRules_test_linked_owner_does_not_hide_a_direct_command(self):
    result = self.lint_text('See [the owner](scripts/check.py), then run `python3 scripts/check.py`.\n')
    self.assertEqual(result.returncode, 1)
    self.assertIn("Mise task", result.stdout)

def _TestLintWritingRules_test_linked_implementation_owner_still_needs_public_route(self):
    result = self.lint_text("Inspect [the owner](scripts/check.py).\n")
    self.assertEqual(result.returncode, 1)
    self.assertIn("owning Mise task", result.stdout)

def _TestLintWritingRules_test_markdown_can_reference_owning_mise_task(self):
    self.check_text('Run `mise run validate`.\n', 0)

def _TestLintWritingRules_test_package_resource_requires_owning_mise_task(self):
    roots = ['references', 'assets', 'examples', 'evals', 'fixtures', 'schemas', 'templates', 'data', 'config', 'docs', 'tests', '.github', '.agents']
    for root in roots:
        with self.subTest(root=root):
            result = self.lint_text(f"Read {root}/proof.json.\n")
            self.assertEqual(result.returncode, 1)
            self.assertIn("owning Mise task", result.stdout)

def _TestLintWritingRules_test_package_resource_can_share_a_line_with_mise_task(self):
    self.check_text('Read assets/policy.json through `mise run policy`.\n', 0)

def _TestLintWritingRules_test_fenced_resource_can_share_a_block_with_mise_task(self):
    self.check_text('```text\n$ mise run budget -- evals/case.json\nchecked evals/case.json\n```\n', 0)

def _TestLintWritingRules_test_resource_can_share_a_heading_section_with_mise_task(self):
    self.check_text('## Evidence\n\nRun `mise run validate`.\n\n```text\nassets/result.json\n```\n', 0)

def _TestLintWritingRules_test_script_path_stays_forbidden_when_task_is_named(self):
    result = self.lint_text('Run scripts/check.py through `mise run validate`.\n')
    self.assertEqual(result.returncode, 1)
    self.assertIn("not scripts/", result.stdout)

class TestLintWritingRules(unittest.TestCase):
    check_text = check_text
    lint_text = _TestLintWritingRules_lint_text
    test_clean_prose_passes = _TestLintWritingRules_test_clean_prose_passes
    test_em_dash_fails = _TestLintWritingRules_test_em_dash_fails
    test_banned_word_fails = _TestLintWritingRules_test_banned_word_fails
    test_banned_frame_fails = _TestLintWritingRules_test_banned_frame_fails
    test_phrase_boundaries_preserve_words_and_reject_actual_frames = _TestLintWritingRules_test_phrase_boundaries_preserve_words_and_reject_actual_frames
    test_latin_abbreviation_fails = _TestLintWritingRules_test_latin_abbreviation_fails
    test_deep_heading_fails = _TestLintWritingRules_test_deep_heading_fails
    test_report_names_file_and_line = _TestLintWritingRules_test_report_names_file_and_line
    test_markdown_cannot_reference_script_paths = _TestLintWritingRules_test_markdown_cannot_reference_script_paths
    test_linked_implementation_owner_preserves_public_route = _TestLintWritingRules_test_linked_implementation_owner_preserves_public_route
    test_linked_owner_does_not_hide_a_direct_command = _TestLintWritingRules_test_linked_owner_does_not_hide_a_direct_command
    test_linked_implementation_owner_still_needs_public_route = _TestLintWritingRules_test_linked_implementation_owner_still_needs_public_route
    test_markdown_can_reference_owning_mise_task = _TestLintWritingRules_test_markdown_can_reference_owning_mise_task
    test_package_resource_requires_owning_mise_task = _TestLintWritingRules_test_package_resource_requires_owning_mise_task
    test_package_resource_can_share_a_line_with_mise_task = _TestLintWritingRules_test_package_resource_can_share_a_line_with_mise_task
    test_fenced_resource_can_share_a_block_with_mise_task = _TestLintWritingRules_test_fenced_resource_can_share_a_block_with_mise_task
    test_resource_can_share_a_heading_section_with_mise_task = _TestLintWritingRules_test_resource_can_share_a_heading_section_with_mise_task
    test_script_path_stays_forbidden_when_task_is_named = _TestLintWritingRules_test_script_path_stays_forbidden_when_task_is_named


def _TestOneLineBlocks_test_hard_wrapped_paragraph_passes(self):
    result = self.lint_text('First half of a sentence\ncontinues on a second line.\n')
    self.assertEqual(result.returncode, 0, result.stdout)

def _TestOneLineBlocks_test_single_line_paragraph_of_any_length_passes(self):
    self.check_text('word ' * 80 + 'end.\n', 0)

def _TestOneLineBlocks_test_list_item_continuation_passes(self):
    result = self.lint_text('- A list item that\n  continues on the next line.\n')
    self.assertEqual(result.returncode, 0, result.stdout)

def _TestOneLineBlocks_test_separate_list_items_pass(self):
    self.check_text('- First item, short.\n- Second item, also short.\n', 0)

def _TestOneLineBlocks_test_numbered_items_pass(self):
    self.check_text('1. First step, run the check.\n2. Second step, read the output.\n', 0)

def _TestOneLineBlocks_test_blank_lines_between_blocks_pass(self):
    self.check_text('Paragraph one stays whole.\n\nParagraph two stays whole.\n', 0)

def _TestOneLineBlocks_test_reference_definitions_are_separate_markdown_blocks(self):
    self.check_text('Use [first] and [second].\n\n[first]: https://example.com/one\n[second]: https://example.com/two\n', 0)

def _TestOneLineBlocks_test_reference_definition_cannot_interrupt_prose(self):
    result = self.lint_text('A paragraph is still open.\n[reference]: https://example.com/one\n')
    self.assertEqual(result.returncode, 1)
    self.assertIn("reference definition cannot interrupt prose", result.stdout)

def _TestOneLineBlocks_test_frontmatter_is_exempt(self):
    self.check_text('---\nname: sample\ndescription: "Use when testing."\n---\n\nBody sits on one line.\n', 0)

def _TestOneLineBlocks_test_headings_and_tables_are_exempt(self):
    self.check_text('# Title\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n| 3 | 4 |\n', 0)

def _TestOneLineBlocks_test_execution_card_labels_are_block_boundaries(self):
    self.check_text('**Input**\nThe current source bytes.\n\n**Action**\nRun the owning Mise task.\n\n**Pass**\nThe task exits zero.\n', 0)

def _TestOneLineBlocks_test_fenced_code_is_exempt(self):
    self.check_text('```\ncode line one\ncode line two\ncode line three\n```\n', 0)

def _TestOneLineBlocks_test_indented_code_is_exempt(self):
    self.check_text('A lead-in line stands alone.\n\n    code one\n    code two\n', 0)

class TestOneLineBlocks(unittest.TestCase):
    check_text = check_text
    lint_text = _TestLintWritingRules_lint_text
    test_hard_wrapped_paragraph_passes = _TestOneLineBlocks_test_hard_wrapped_paragraph_passes
    test_single_line_paragraph_of_any_length_passes = _TestOneLineBlocks_test_single_line_paragraph_of_any_length_passes
    test_list_item_continuation_passes = _TestOneLineBlocks_test_list_item_continuation_passes
    test_separate_list_items_pass = _TestOneLineBlocks_test_separate_list_items_pass
    test_numbered_items_pass = _TestOneLineBlocks_test_numbered_items_pass
    test_blank_lines_between_blocks_pass = _TestOneLineBlocks_test_blank_lines_between_blocks_pass
    test_reference_definitions_are_separate_markdown_blocks = _TestOneLineBlocks_test_reference_definitions_are_separate_markdown_blocks
    test_reference_definition_cannot_interrupt_prose = _TestOneLineBlocks_test_reference_definition_cannot_interrupt_prose
    test_frontmatter_is_exempt = _TestOneLineBlocks_test_frontmatter_is_exempt
    test_headings_and_tables_are_exempt = _TestOneLineBlocks_test_headings_and_tables_are_exempt
    test_execution_card_labels_are_block_boundaries = _TestOneLineBlocks_test_execution_card_labels_are_block_boundaries
    test_fenced_code_is_exempt = _TestOneLineBlocks_test_fenced_code_is_exempt
    test_indented_code_is_exempt = _TestOneLineBlocks_test_indented_code_is_exempt

class TestOwnDocsPass(unittest.TestCase):
    def test_every_markdown_file_in_this_skill_passes(self):
        result = run("lint_writing.py", SKILL_DIR)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

if __name__ == "__main__":
    unittest.main()
