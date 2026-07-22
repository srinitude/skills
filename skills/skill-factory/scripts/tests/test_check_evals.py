"""Tests for scripts/check_evals.py against real eval files."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR, run

GOOD_CASE = {
    "id": 1,
    "prompt": "Run the sample check on data.csv and report failures.",
    "expected_output": "A list of failing rows with reasons.",
    "assertions": ["The reply lists each failing row."],
}
GOOD_QUERIES = [
    {"query": "run the sample check", "should_trigger": True},
    {"query": "what time is it", "should_trigger": False},
]


def write_evals(root, evals_doc, queries):
    evals_dir = Path(root) / "evals"
    evals_dir.mkdir()
    (evals_dir / "evals.json").write_text(json.dumps(evals_doc))
    if queries is not None:
        text = json.dumps(queries)
        (evals_dir / "trigger-queries.json").write_text(text)
    return root


class TestCheckEvalsCli(unittest.TestCase):
    def test_help_documents_usage_and_exit_codes(self):
        result = run("check_evals.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        self.assertIn("exit code", result.stdout.lower())

    def test_missing_target_is_a_usage_error(self):
        result = run("check_evals.py")
        self.assertEqual(result.returncode, 2)


class TestCheckEvalsRules(unittest.TestCase):
    def test_this_skills_evals_pass(self):
        result = run("check_evals.py", SKILL_DIR)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_valid_minimal_evals_pass(self):
        doc = {"skill_name": "sample", "evals": [GOOD_CASE]}
        with tempfile.TemporaryDirectory() as tmp:
            write_evals(tmp, doc, GOOD_QUERIES)
            result = run("check_evals.py", tmp, "--min-cases", "1",
                         "--min-queries", "2")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_case_missing_expected_output_fails(self):
        bad = {k: v for k, v in GOOD_CASE.items() if k != "expected_output"}
        doc = {"skill_name": "sample", "evals": [bad]}
        with tempfile.TemporaryDirectory() as tmp:
            write_evals(tmp, doc, GOOD_QUERIES)
            result = run("check_evals.py", tmp, "--min-cases", "1",
                         "--min-queries", "2")
        self.assertEqual(result.returncode, 1)
        self.assertIn("expected_output", result.stdout)

    def test_missing_trigger_queries_file_fails(self):
        doc = {"skill_name": "sample", "evals": [GOOD_CASE]}
        with tempfile.TemporaryDirectory() as tmp:
            write_evals(tmp, doc, None)
            result = run("check_evals.py", tmp, "--min-cases", "1")
        self.assertEqual(result.returncode, 1)
        self.assertIn("trigger-queries.json", result.stdout)

    def test_queries_need_both_labels(self):
        doc = {"skill_name": "sample", "evals": [GOOD_CASE]}
        one_sided = [{"query": "x", "should_trigger": True}] * 4
        with tempfile.TemporaryDirectory() as tmp:
            write_evals(tmp, doc, one_sided)
            result = run("check_evals.py", tmp, "--min-cases", "1")
        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
