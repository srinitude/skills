"""Semantic Markdown grouping tests."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[2]


def run(path):
    return subprocess.run(
        [sys.executable, str(SKILL / "scripts" / "lint_writing.py"),
         str(path)], capture_output=True, text=True, timeout=120)


class TestMarkdownSemantics(unittest.TestCase):
    def test_stacked_rule_paragraphs_need_a_semantic_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "stacked.md"
            path.write_text(
                "# Rules\n\nRead the source.\n\nKeep its scope.\n\nSave proof.\n",
                encoding="utf-8")
            result = run(path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("stacked one-sentence paragraphs", result.stdout)

    def test_parallel_rules_pass_as_bullets(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "grouped.md"
            path.write_text(
                "# Rules\n\n- Read the source.\n- Keep its scope.\n- Save proof.\n",
                encoding="utf-8")
            result = run(path)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
