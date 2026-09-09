"""Check audience and reading declarations; no audience suitability claim."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_use_case_contract import contract, write_skill


class TestUseCaseAcceptance(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "release-notes"
        self.root.mkdir()
        self.data = contract()
        write_skill(self.root, self.data)
        self.path = self.root / "assets/use-case-contract.json"

    def check(self, accept=False):
        self.path.write_text(json.dumps(self.data))
        return run("check_use_case_contract.py", self.root, *(["--accept"] if accept else []))

    def test_legacy_inspection_does_not_assign_or_accept_missing_audience(self):
        self.assertEqual(self.check().returncode, 0)
        blocked = self.check(accept=True)
        self.assertEqual(blocked.returncode, 1, blocked.stdout + blocked.stderr)
        self.assertIn("audience", blocked.stdout)
        self.assertNotIn("audience", json.loads(self.path.read_text()))
        self.data["audience"] = {"primary": "human", "secondary": ["release editor"]}
        self.data["initial_context"] = [{"id": "ledger", "role": "ledger",
                                        "binding": "invocation", "depends_on": []}]
        recovered = self.check(accept=True)
        self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)

    def test_present_audience_types_and_enum_are_checked_during_inspection(self):
        for audience in [None, [], "human", {}, {"primary": True}, {"primary": []},
                         {"primary": "person"}, {"primary": "agent", "secondary": {}}]:
            with self.subTest(audience=audience):
                self.data["audience"] = audience
                result = self.check()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("audience", result.stdout)
                self.assertNotIn("Traceback", result.stderr)

    def test_duplicate_json_and_wrong_document_shape_fail_cleanly(self):
        original = json.dumps(self.data)
        for raw in ["[]", "null", '{"skill":"wrong",' + original[1:]]:
            with self.subTest(raw=raw[:30]):
                self.path.write_text(raw)
                result = run("check_use_case_contract.py", self.root)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("FAIL", result.stdout)
                self.assertNotIn("Traceback", result.stderr)

    def test_present_reading_graph_cannot_silently_pass(self):
        for value in [None, [], [{"id": "ledger", "role": "ledger",
                                 "binding": "invocation", "depends_on": ["ledger"]}]]:
            with self.subTest(value=value):
                self.data["initial_context"] = value
                result = self.check()
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("context", result.stdout)


if __name__ == "__main__":
    unittest.main()
