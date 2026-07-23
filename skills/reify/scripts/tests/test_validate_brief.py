import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/validate_brief.py"
VALID = {
    "outcome": "Ship a portable reification skill.",
    "done_means": "Every local and remote check passes.",
    "first_milestone": "The registry validates the skill.",
    "next_action": "Run the local CI task.",
}


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
        self.assertIn("validate_brief.py BRIEF.json", result.stdout)


if __name__ == "__main__":
    unittest.main()
