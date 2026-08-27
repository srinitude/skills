"""Deterministic tests for the public mobile-first package."""
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


class TestCommands(unittest.TestCase):
    def run_script(self, *parts):
        return subprocess.run(
            [sys.executable, *parts], cwd=ROOT, capture_output=True, text=True,
            check=False,
        )

    def test_package_check_passes(self):
        result = self.run_script("scripts/check_package.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_eval_check_passes(self):
        result = self.run_script("scripts/check_evals.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_failure_fixture_fails_closed(self):
        result = self.run_script(
            "scripts/validate_packet.py", "assets/fixtures/fail-performance.json"
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["status"], "BLOCKED_PERFORMANCE")


if __name__ == "__main__":
    unittest.main()
