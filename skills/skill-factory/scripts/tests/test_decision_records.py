"""Behavior tests for motivated skill decision records."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run


def record(kind="deterministic"):
    return {
        "id": f"release-notes-source-order-{kind.replace('_', '-')}",
        "kind": kind,
        "outcome": "Release notes reflect git history for the change audience.",
        "motivation": "Git history prevents invented release notes claims.",
        "why_this_path": "A commit receipt links release notes to git history.",
        "owner": "mise" if kind == "deterministic" else "model",
        "inputs": ["git history", "change audience"],
        "expected_effect": "Release notes state only shipped changes.",
        "proof": "A git history receipt supports each release notes claim.",
        "falsifier": "A release notes claim has no matching git history entry.",
        "failure_branch": "Block release notes and report the missing change.",
    }


def write_package(root, records, terms=None):
    (root / "assets").mkdir()
    domain_terms = terms or ["release notes", "git history", "change audience"]
    use_case = {"domain_terms": domain_terms}
    (root / "assets" / "use-case-contract.json").write_text(
        json.dumps(use_case), encoding="utf-8")
    data = {"version": "1.0.0", "skill": root.name, "records": records}
    (root / "assets" / "decision-records.json").write_text(
        json.dumps(data), encoding="utf-8")


class TestDecisionRecords(unittest.TestCase):
    def test_help_documents_usage_and_exit_codes(self):
        result = run("check_decision_records.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("exit code", result.stdout.lower())

    def test_deterministic_and_model_owned_decisions_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_package(root, [record(), record("model_owned")])
            result = run("check_decision_records.py", root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_motivation_fails(self):
        item = record()
        del item["motivation"]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_package(root, [item])
            result = run("check_decision_records.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("motivation", result.stdout)

    def test_generic_reason_without_domain_term_fails(self):
        item = record()
        item["why_this_path"] = "This is the normal option."
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_package(root, [item])
            result = run("check_decision_records.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("why_this_path", result.stdout)

    def test_domain_label_cannot_decorate_generic_decision(self):
        item = record()
        item["why_this_path"] = (
            "Release notes operation produces objective progress or a bounded failure.")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_package(root, [item])
            result = run("check_decision_records.py", root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("generic scaffold language", result.stdout)

    def test_decision_kind_controls_owner(self):
        item = record("model_owned")
        item["owner"] = "mise"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_package(root, [item])
            result = run("check_decision_records.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("owner", result.stdout)

    def test_domain_term_must_not_match_inside_an_unrelated_word(self):
        item = record()
        item["why_this_path"] = "A digital output is available."
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_package(root, [item], ["git"])
            result = run("check_decision_records.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("why_this_path", result.stdout)


if __name__ == "__main__":
    unittest.main()
