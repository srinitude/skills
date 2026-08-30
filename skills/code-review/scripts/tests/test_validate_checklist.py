import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/validate_checklist.py"
VALID = {
    "target": "src/parser.py",
    "contract": "The parser must round-trip every fixture.",
    "verdict": "",
    "next_check": "Rerun the suite after the fix lands.",
    "findings": [
        {
            "id": "F-001",
            "severity": "major",
            "file": "src/parser.py",
            "line": "42",
            "clause": "round-trip",
            "evidence": "fixture quoted.csv fails on trailing comma",
            "suggestion": "Strip the trailing comma before split.",
            "state": "open",
        }
    ],
    "decisions": [
        {
            "id": "D-001",
            "finding": "F-001",
            "choice": "Accept the fix plan.",
            "reason": "It restores round-trip.",
            "reversible": True,
        }
    ],
    "status": "active",
}


def checklist(**overrides):
    payload = json.loads(json.dumps(VALID))
    payload.update(overrides)
    return payload


def run_validator(payload):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
        json.dump(payload, handle)
        path = Path(handle.name)
    try:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        path.unlink(missing_ok=True)


class ValidateChecklistTests(unittest.TestCase):
    def test_accepts_a_complete_checklist(self):
        result = run_validator(VALID)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"errors": [], "status": "PASS"})

    def test_accepts_a_finalized_checklist_with_no_findings(self):
        payload = checklist(verdict="sign-off", findings=[], decisions=[], status="finalized")
        result = run_validator(payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_rejects_missing_or_empty_fields(self):
        result = run_validator({"target": "src/p.py", "verdict": ""})
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(
            report["errors"],
            [
                "contract must be a non-empty string",
                "next_check must be a non-empty string",
                "decisions must be a list",
                "findings must be a list",
                "status must be one of active, blocked, finalized",
            ],
        )

    def test_rejects_an_unknown_status(self):
        result = run_validator(checklist(status="done"))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            json.loads(result.stdout)["errors"],
            ["status must be one of active, blocked, finalized"],
        )

    def test_rejects_an_unknown_verdict(self):
        result = run_validator(checklist(verdict="approve"))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            json.loads(result.stdout)["errors"],
            ["verdict must be one of , sign-off, block"],
        )

    def test_rejects_a_finding_that_is_not_a_full_entry(self):
        result = run_validator(checklist(findings=["F-001 trailing comma"]))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            json.loads(result.stdout)["errors"],
            ["findings[1] must be an object"],
        )

    def test_rejects_a_bad_finding_id_and_missing_finding_fields(self):
        result = run_validator(checklist(findings=[{"id": "F-1", "severity": "x"}]))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            json.loads(result.stdout)["errors"],
            [
                "findings[1].id must match ^F-[0-9]{3}$",
                "findings[1].severity must be one of blocker, major, minor, nit",
                "findings[1].evidence must be a non-empty string",
                "findings[1].file must be a non-empty string",
                "findings[1].suggestion must be a non-empty string",
                "findings[1].state must be one of open, resolved, unverified",
            ],
        )

    def test_rejects_a_bad_decision_id_and_missing_decision_fields(self):
        result = run_validator(checklist(decisions=[{"id": "D-1", "choice": "x"}]))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            json.loads(result.stdout)["errors"],
            [
                "decisions[1].id must match ^D-[0-9]{3}$",
                "decisions[1].reason must be a non-empty string",
                "decisions[1].finding must be a non-empty string",
                "decisions[1].reversible must be true or false",
            ],
        )

    def test_help_documents_usage_and_exit_codes(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Exit codes", result.stdout)
        self.assertIn('validate_checklist.py" ./CHECKLIST.json', result.stdout)

    def test_missing_file_reports_exit_1_not_a_crash(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "no-such-checklist.json"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "FAIL")

    def test_rejects_a_sign_off_with_an_open_blocker(self):
        blocker = {
            "id": "F-001",
            "severity": "blocker",
            "file": "src/parser.py",
            "line": "42",
            "clause": "round-trip",
            "evidence": "quoted.csv fails on trailing comma",
            "suggestion": "Strip the trailing comma before split.",
            "state": "open",
        }
        result = run_validator(checklist(
            verdict="sign-off", status="finalized", findings=[blocker], decisions=[]))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            json.loads(result.stdout)["errors"],
            ["findings[1] open blocker conflicts with sign-off verdict"],
        )

    def test_rejects_blocked_status_without_block_verdict(self):
        result = run_validator(checklist(verdict="", status="blocked"))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            json.loads(result.stdout)["errors"],
            ["status blocked requires verdict block"],
        )

    def test_accepts_a_blocked_record_with_block_verdict(self):
        result = run_validator(checklist(verdict="block", status="blocked"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
