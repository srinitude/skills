"""Contract tests for scripts/ledger.py.

Each test pins a contract a caller touches:
  1. init creates a ledger file with its header
  2. add appends one row a reader can find
  3. show prints the ledger back
  4. count reports how often a decision class already appeared
  5. add without a decision is a usage error
"""
import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
LEDGER = SKILL_DIR / "scripts" / "ledger.py"


class TestLedger(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self.tmp.name) / "decision-ledger-demo.md"

    def tearDown(self):
        self.tmp.cleanup()

    def run_cmd(self, *args):
        return subprocess.run([sys.executable, str(LEDGER), *args],
                              capture_output=True, text=True)

    def test_init_creates_a_file_with_a_header(self):
        proc = self.run_cmd("init", "--file", str(self.path), "--slug", "demo")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("| The decision |", self.path.read_text())

    def test_add_appends_a_findable_row(self):
        self.run_cmd("init", "--file", str(self.path), "--slug", "demo")
        proc = self.run_cmd("add", "--file", str(self.path),
                            "--decision", "Row height on the orders table",
                            "--chosen", "32px compact", "--origin", "inherited")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Row height on the orders table", self.path.read_text())

    def test_show_prints_the_ledger(self):
        self.run_cmd("init", "--file", str(self.path), "--slug", "demo")
        self.run_cmd("add", "--file", str(self.path),
                     "--decision", "Accent colour", "--origin", "deliberate")
        proc = self.run_cmd("show", "--file", str(self.path))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("Accent colour", proc.stdout)

    def test_count_reports_prior_appearances(self):
        self.run_cmd("init", "--file", str(self.path), "--slug", "demo")
        for _ in range(3):
            self.run_cmd("add", "--file", str(self.path),
                         "--decision", "Spacing scale", "--origin", "inherited")
        proc = self.run_cmd("count", "--file", str(self.path),
                            "--decision", "Spacing scale")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("3", proc.stdout)

    def test_add_without_a_decision_is_a_usage_error(self):
        self.run_cmd("init", "--file", str(self.path), "--slug", "demo")
        proc = self.run_cmd("add", "--file", str(self.path),
                            "--origin", "inherited")
        self.assertEqual(proc.returncode, 2)

    def test_show_on_a_missing_file_exits_one(self):
        proc = self.run_cmd("show", "--file", str(self.path))
        self.assertEqual(proc.returncode, 1)

    def test_help_exits_zero(self):
        proc = self.run_cmd("--help")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("exit codes", proc.stdout.lower())
