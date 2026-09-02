"""Attack the standalone DTCG invocation receipt boundary."""
import json
import pathlib
import subprocess
import sys
import tempfile
import tomllib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_token_invocation.py"


def receipt_entries(reason, proof):
    with (ROOT / "mise.toml").open("rb") as handle:
        tasks = set(tomllib.load(handle)["tasks"]) - {"invocation-policy"}
    return [
        {"task": task, "status": "run", "applicability_reason": reason,
         "proof": proof}
        for task in sorted(tasks)
    ]


def run_receipt(document):
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "receipt.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(ROOT), str(path)],
            capture_output=True, text=True, timeout=30,
        )


class InvocationPolicyFailClosedTests(unittest.TestCase):
    def test_domain_label_cannot_decorate_generic_receipt_prose(self):
        generic = "DTCG token operation produces objective progress or a bounded failure."
        document = {"skill": "dtcg-tokens", "operation": "review",
                    "entries": receipt_entries(generic, generic)}
        result = run_receipt(document)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("generic scaffold language", result.stdout)

    def test_domain_term_cannot_match_inside_an_unrelated_word(self):
        document = {"skill": "dtcg-tokens", "operation": "review",
                    "entries": receipt_entries("DTCG token review ran.",
                                               "pretoken proof exists.")}
        result = run_receipt(document)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("needs a DTCG token term", result.stdout)

    def test_malformed_entry_types_fail_without_traceback(self):
        entries = receipt_entries("DTCG token review ran.",
                                  "DTCG token task exited zero.")
        entries[0]["task"] = ["ci"]
        entries[0]["status"] = ["run"]
        entries[0]["proof"] = {"DTCG token": True}
        document = {"skill": "dtcg-tokens", "operation": "review",
                    "entries": entries}
        result = run_receipt(document)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIn("entries.0", result.stdout)


if __name__ == "__main__":
    unittest.main()
