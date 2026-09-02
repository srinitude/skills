"""Tests for scripts/doctor.py, the environment readiness report."""
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path

from cli import run

SHIM = "#!/bin/sh\necho 0.0.0\n"


def env_with_path(path):
    env = dict(os.environ)
    env["PATH"] = path
    return env


def path_without_runner():
    parts = [p for p in os.environ.get("PATH", "").split(os.pathsep)
             if p and not (Path(p) / "mise").exists()]
    return os.pathsep.join(parts)


def write_runner_shim(directory):
    path = Path(directory) / "mise"
    path.write_text(SHIM, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return directory


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

    def test_report_names_one_mise_mode_without_fallback_commands(self):
        report = json.loads(self.result.stdout)
        self.assertEqual(report["mode"], "mise")
        self.assertNotIn("fallback", report)


class TestDoctorWithoutTaskRunner(unittest.TestCase):
    def setUp(self):
        env = env_with_path(path_without_runner())
        self.result = run("doctor.py", env=env)
        self.report = json.loads(self.result.stdout)

    def test_absent_task_runner_fails_closed(self):
        self.assertEqual(self.result.returncode, 1, self.result.stdout)

    def test_absent_task_runner_blocks_readiness(self):
        self.assertEqual(self.report["mode"], "mise")
        self.assertFalse(self.report["ready"])

    def test_task_runner_check_is_required(self):
        runner = [c for c in self.report["checks"] if c["name"] == "mise"][0]
        self.assertTrue(runner["required"])
        self.assertFalse(runner["ok"])

    def test_report_does_not_offer_direct_command_bypass(self):
        self.assertNotIn("fallback", self.report)


class TestDoctorWithTaskRunner(unittest.TestCase):
    def test_present_task_runner_reports_full_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_runner_shim(tmp)
            env = env_with_path(tmp + os.pathsep + path_without_runner())
            result = run("doctor.py", env=env)
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(report["mode"], "mise")
        self.assertNotIn("fallback", report)


class TestDoctorMissingRequirement(unittest.TestCase):
    def test_missing_bundled_file_fails(self):
        report = json.loads(run("doctor.py").stdout)
        files = [c for c in report["checks"] if c["name"] == "scripts"][0]
        self.assertTrue(files["required"])
        self.assertTrue(files["ok"], files["detail"])


if __name__ == "__main__":
    unittest.main()
