"""Attack DTCG research currency and source-diversity claims."""
import pathlib
import tempfile
import unittest

from test_token_policy_fail_closed import (
    copy_policy_package,
    read_json,
    run_policy,
    write_json,
)


class ResearchPolicyFailClosedTests(unittest.TestCase):
    def run_attack(self, mutate):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            copy_policy_package(root)
            data = read_json(root, "use-case-contract.json")
            mutate(data)
            write_json(root, "use-case-contract.json", data)
            return run_policy("domain-research", root)

    def test_stale_research_receipt_is_rejected(self):
        result = self.run_attack(
            lambda data: data["research_receipts"][0].update(
                {"checked_at": "2020-01-01T00:00:00+00:00"}))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("not current", result.stdout)

    def test_one_repeated_web_host_is_not_heavy_research(self):
        def mutate(data):
            for index, receipt in enumerate(data["research_receipts"]):
                receipt["source"] = f"https://one.example.test/source-{index}"

        result = self.run_attack(mutate)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("two web hosts", result.stdout)

    def test_invalid_source_class_and_disposition_are_rejected(self):
        def mutate(data):
            data["research_receipts"][0]["source_class"] = "opinion"
            data["research_receipts"][0]["disposition"] = "trusted"

        result = self.run_attack(mutate)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("source_class", result.stdout)
        self.assertIn("disposition", result.stdout)


if __name__ == "__main__":
    unittest.main()
