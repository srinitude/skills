"""Behavior tests for the Mise-owned domain research gate."""
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_use_case_contract import contract, write_skill


class TestDomainResearch(unittest.TestCase):
    def check(self, data):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, data)
            return run("check_domain_research.py", root)

    def test_help_documents_usage_and_exit_codes(self):
        result = run("check_domain_research.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("exit code", result.stdout.lower())

    def test_current_source_backed_research_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, contract())
            result = run("check_domain_research.py", root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_one_web_host_is_not_heavy_research(self):
        data = contract()
        for receipt in data["research_receipts"]:
            receipt["source"] = "https://one.example.org/source"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, data)
            result = run("check_domain_research.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("two web hosts", result.stdout)

    def test_receipts_must_cover_every_domain_dimension(self):
        data = contract()
        for receipt in data["research_receipts"]:
            receipt["dimensions"] = ["actors"]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, data)
            result = run("check_domain_research.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("dimension coverage", result.stdout)

    def test_disconfirming_search_is_required(self):
        data = contract()
        data["disconfirmation"] = []
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, data)
            result = run("check_domain_research.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("disconfirmation", result.stdout)

    def test_receipt_text_and_disposition_are_valid(self):
        cases = [("claim", ""), ("limitations", " "),
                 ("disposition", "unknown")]
        for field, value in cases:
            with self.subTest(field=field):
                data = contract()
                data["research_receipts"][0][field] = value
                result = self.check(data)
                self.assertEqual(result.returncode, 1)
                self.assertIn(field, result.stdout)

    def test_receipt_dimensions_need_known_names(self):
        data = contract()
        data["research_receipts"][0]["dimensions"] = ["actors", "mystery"]
        result = self.check(data)
        self.assertEqual(result.returncode, 1)
        self.assertIn("dimensions", result.stdout)

    def test_disconfirmation_needs_web_source_and_text(self):
        data = contract()
        data["disconfirmation"][0]["source"] = "memory"
        data["disconfirmation"][0]["result"] = ""
        result = self.check(data)
        self.assertEqual(result.returncode, 1)
        self.assertIn("source", result.stdout)
        self.assertIn("result", result.stdout)


if __name__ == "__main__":
    unittest.main()
