"""Tests for scripts/doctor.py, the environment readiness report."""
import json
import unittest

from cli import run


class TestDoctorCli(unittest.TestCase):
    def test_help_documents_usage_and_exit_codes(self):
        result = run("doctor.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        self.assertIn("exit code", result.stdout.lower())


class TestDoctorReport(unittest.TestCase):
    def setUp(self):
        self.result = run("doctor.py")

    def test_exits_zero_in_a_working_environment(self):
        self.assertEqual(self.result.returncode, 0, self.result.stdout)

    def test_report_is_valid_json(self):
        report = json.loads(self.result.stdout)
        self.assertIn("checks", report)
        self.assertIn("ready", report)

    def test_report_covers_python_mise_and_bundled_files(self):
        report = json.loads(self.result.stdout)
        names = {check["name"] for check in report["checks"]}
        for expected in ["python", "mise", "scripts", "templates"]:
            self.assertIn(expected, names)


if __name__ == "__main__":
    unittest.main()
