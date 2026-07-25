import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/validate_brief.py"
VALID = {
    "signal": "Ship a portable reification skill.",
    "outcome": "Ship a portable reification skill.",
    "done_means": "Every local and remote check passes.",
    "first_milestone": "The registry validates the skill.",
    "next_action": "Run the local CI task.",
    "constraints": ["No external publish before review."],
    "sources_checked": ["skills/reify: reachable"],
    "decisions": [
        {
            "id": "D-001",
            "choice": "Ship one brief schema.",
            "reason": "Three schemas disagreed.",
            "dependents": ["D-002"],
            "reversible": True,
        }
    ],
    "open_questions": [],
    "status": "active",
}


def brief(**overrides):
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


class ValidateBriefTests(unittest.TestCase):
    def test_accepts_a_complete_brief(self):
        result = run_validator(VALID)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"errors": [], "status": "PASS"})

    def test_accepts_a_scrapped_brief_with_no_decisions(self):
        result = run_validator(brief(status="scrapped", decisions=[]))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_rejects_missing_or_empty_fields(self):
        result = run_validator({"outcome": "", "next_action": "Act."})
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(
            report["errors"],
            [
                "done_means must be a non-empty string",
                "first_milestone must be a non-empty string",
                "outcome must be a non-empty string",
                "signal must be a non-empty string",
                "constraints must be a list",
                "decisions must be a list",
                "open_questions must be a list",
                "sources_checked must be a list",
                "status must be one of active, finalized, scrapped",
            ],
        )

    def test_rejects_an_unknown_status(self):
        result = run_validator(brief(status="done"))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            json.loads(result.stdout)["errors"],
            ["status must be one of active, finalized, scrapped"],
        )

    def test_rejects_a_decision_that_is_not_a_full_entry(self):
        result = run_validator(brief(decisions=["D-001 pick one schema"]))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            json.loads(result.stdout)["errors"],
            ["decisions[1] must be an object"],
        )

    def test_rejects_a_bad_decision_id_and_missing_decision_fields(self):
        result = run_validator(brief(decisions=[{"id": "D-1", "choice": "x"}]))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            json.loads(result.stdout)["errors"],
            [
                "decisions[1].id must match ^D-[0-9]{3}$",
                "decisions[1].reason must be a non-empty string",
                "decisions[1].dependents must be a list",
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
        self.assertIn('validate_brief.py" ./BRIEF.json', result.stdout)

    def test_missing_file_reports_exit_1_not_a_crash(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "no-such-brief.json"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
