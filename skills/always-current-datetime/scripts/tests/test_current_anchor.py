"""Behavior tests for the bundled current-date anchor script."""
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = SKILL_DIR / "scripts" / "current_anchor.py"


def run_anchor(*arguments, timezone_marker="missing", command=None, cwd=None):
    environment = os.environ.copy()
    environment.pop("PROFILE_TIMEZONE", None)
    if timezone_marker != "missing":
        environment["PROFILE_TIMEZONE"] = timezone_marker
    return subprocess.run(
        [*(command or [sys.executable, str(SCRIPT)]), *arguments],
        capture_output=True,
        check=False,
        env=environment,
        text=True,
        cwd=cwd,
    )


class TestCurrentAnchor(unittest.TestCase):
    run_anchor = staticmethod(run_anchor)

    def test_help_is_available_without_emitting_json(self):
        result = self.run_anchor("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)
        self.assertNotIn('"captured_at"', result.stdout)

    def test_profile_timezone_produces_one_complete_utc_record(self):
        result = self.run_anchor(timezone_marker="UTC")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.rstrip("\n").splitlines()), 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["source"], "profile-environment")
        self.assertEqual(payload["timezone"], "UTC")
        self.assertEqual(payload["utc_offset"], "+00:00")
        anchor = date.fromisoformat(payload["date"])
        self.assertEqual(payload["yesterday"], (anchor - timedelta(days=1)).isoformat())
        self.assertEqual(payload["tomorrow"], (anchor + timedelta(days=1)).isoformat())

    def test_explicit_timezone_overrides_profile_environment(self):
        result = self.run_anchor("--timezone", "UTC", timezone_marker="Asia/Tokyo")
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["source"], "argument")
        self.assertEqual(payload["timezone"], "UTC")

    def test_system_local_timezone_is_the_final_fallback(self):
        result = self.run_anchor()
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload["source"], "system-local")
        self.assertTrue(payload["timezone"])
        self.assertTrue(payload["zone_abbreviation"])

    def test_invalid_timezone_fails_without_stdout(self):
        result = self.run_anchor(timezone_marker="Not/A_Zone")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("current_anchor_error: ZoneInfoNotFoundError:", result.stderr)
        self.assertIn("Not/A_Zone", result.stderr)

    def test_record_contains_the_full_temporal_schema(self):
        result = self.run_anchor(timezone_marker="UTC")
        payload = json.loads(result.stdout)
        expected = {
            "captured_at", "date", "source", "time", "timezone",
            "tomorrow", "utc_offset", "weekday", "yesterday",
            "zone_abbreviation",
        }
        self.assertEqual(set(payload), expected)
        self.assertRegex(payload["date"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(payload["time"], r"^\d{2}:\d{2}:\d{2}$")


class TestInlineAnchor(TestCurrentAnchor):
    @staticmethod
    def run_anchor(*arguments, **options):
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        match = re.search(r"```python\n(.*?)\n```", text, re.DOTALL)
        if match is None:
            raise AssertionError("missing self-contained clock fallback")
        return run_anchor(*arguments, command=[sys.executable, "-c", match[1]], **options)

    def test_clock_runs_from_an_empty_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_anchor("--timezone", "Asia/Kathmandu", cwd=directory)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["utc_offset"], "+05:45")

    def test_blank_profile_uses_system_local(self):
        result = self.run_anchor(timezone_marker="  ")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["source"], "system-local")


if __name__ == "__main__":
    unittest.main()

