"""Command contract for the per-run clock anchor."""
import json
import pathlib
import subprocess
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = SKILL_DIR / "scripts" / "current_anchor.py"


class TestCurrentAnchor(unittest.TestCase):
    def test_command_returns_required_fields(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--timezone", "UTC"], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        required = {"captured_at", "date", "weekday", "timezone", "utc_offset", "source"}
        self.assertTrue(required <= set(payload))
        self.assertEqual(payload["timezone"], "UTC")

    def test_help_documents_exit_codes(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertIn("Exit codes", result.stdout)
        self.assertIn("Example", result.stdout)


if __name__ == "__main__":
    unittest.main()
