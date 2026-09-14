"""Behavior tests for complete per-invocation Mise task disposition."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run


def task_file():
    return """[tasks.ci]
description = "Release notes CI"
depends = ["test"]
[tasks.test]
description = "Release notes test"
depends = []
run = "python3 scripts/test.py"
[tasks.info]
description = "Release notes info"
depends = []
run = "python3 scripts/info.py"
[tasks.invocation-policy]
description = "Release notes invocation"
depends = []
run = "python3 scripts/check.py ."
"""


def receipt(entries=None):
    return {
        "skill": "release-notes",
        "operation": "update release notes",
        "entries": entries or [
            {"task": "ci", "status": "run",
             "applicability_reason": "Release notes need integrated CI.",
             "proof": "Release notes CI exited 0."},
            {"task": "test", "status": "run",
             "applicability_reason": "Release notes behavior changed.",
             "proof": "Release notes tests exited 0."},
            {"task": "info", "status": "inapplicable",
             "applicability_reason": "Release notes metadata did not change.",
             "proof": "The release notes diff contains no metadata."},
        ],
    }


def write_case(root, data, terms=None):
    (root / "assets").mkdir()
    (root / "mise.toml").write_text(task_file(), encoding="utf-8")
    use_case = {"domain_terms": terms or ["release notes", "git history"]}
    (root / "assets/use-case-contract.json").write_text(
        json.dumps(use_case), encoding="utf-8")
    path = root / "receipt.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _TestInvocationReceipt_check(self, data, terms=None):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "release-notes"
        root.mkdir()
        path = write_case(root, data, terms)
        return run("check_invocation_receipt.py", root, path)

def _TestInvocationReceipt_test_every_task_is_run_or_justified_inapplicable(self):
    result = self.check(receipt())
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

def _TestInvocationReceipt_test_missing_task_fails(self):
    data = receipt()
    data["entries"] = data["entries"][:-1]
    result = self.check(data)
    self.assertEqual(result.returncode, 1)
    self.assertIn("missing tasks: info", result.stdout)

def _TestInvocationReceipt_test_generic_inapplicable_reason_fails(self):
    data = receipt()
    data["entries"][2]["applicability_reason"] = "Not needed."
    result = self.check(data)
    self.assertEqual(result.returncode, 1)
    self.assertIn("applicability_reason", result.stdout)

def _TestInvocationReceipt_test_domain_label_cannot_decorate_generic_receipt_prose(self):
    data = receipt()
    generic = "Release notes operation produces objective progress or a bounded failure."
    data["entries"][0]["applicability_reason"] = generic
    data["entries"][0]["proof"] = generic
    result = self.check(data)
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.assertIn("generic scaffold language", result.stdout)

def _TestInvocationReceipt_test_validator_accounts_for_its_own_execution(self):
    names = [item["task"] for item in receipt()["entries"]]
    self.assertNotIn("invocation-policy", names)
    self.assertEqual(self.check(receipt()).returncode, 0)

def _TestInvocationReceipt_test_domain_term_must_not_match_inside_an_unrelated_word(self):
    data = receipt()
    data["entries"][0]["proof"] = "Digital output exists."
    result = self.check(data, ["git"])
    self.assertEqual(result.returncode, 1)
    self.assertIn("entries.0.proof", result.stdout)

def _TestInvocationReceipt_test_malformed_entry_types_fail_without_traceback(self):
    data = receipt()
    data["entries"][0]["task"] = ["ci"]
    data["entries"][0]["status"] = ["run"]
    data["entries"][0]["proof"] = {"release notes": True}
    result = self.check(data)
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.assertNotIn("Traceback", result.stderr)
    self.assertIn("entries.0", result.stdout)


class TestInvocationReceipt(unittest.TestCase):
    check = _TestInvocationReceipt_check
    test_every_task_is_run_or_justified_inapplicable = _TestInvocationReceipt_test_every_task_is_run_or_justified_inapplicable
    test_missing_task_fails = _TestInvocationReceipt_test_missing_task_fails
    test_generic_inapplicable_reason_fails = _TestInvocationReceipt_test_generic_inapplicable_reason_fails
    test_domain_label_cannot_decorate_generic_receipt_prose = _TestInvocationReceipt_test_domain_label_cannot_decorate_generic_receipt_prose
    test_validator_accounts_for_its_own_execution = _TestInvocationReceipt_test_validator_accounts_for_its_own_execution
    test_domain_term_must_not_match_inside_an_unrelated_word = _TestInvocationReceipt_test_domain_term_must_not_match_inside_an_unrelated_word
    test_malformed_entry_types_fail_without_traceback = _TestInvocationReceipt_test_malformed_entry_types_fail_without_traceback


if __name__ == "__main__":
    unittest.main()
