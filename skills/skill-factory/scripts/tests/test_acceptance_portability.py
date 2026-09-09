"""Generated and standardized output consumers must carry their real dependencies."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cli import SCRIPTS, run
sys.path.insert(0, str(SCRIPTS))
from standardize_registry_skill import copy_support

CHECKERS = ["check_invocation_receipt.py", "invocation_acceptance.py",
            "source_coverage.py", "skill_package.py", "skill_scope.py", "validate_skill.py",
            "check_task_graph.py", "mise_task_graph.py"]


class TestAcceptancePortability(unittest.TestCase):
    def test_both_copy_paths_include_current_independent_acceptance_consumer(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            result = run("scaffold_skill.py", "--name", "release-notes",
                         "--description", "Use when release notes need review.",
                         "--scope", "user", "--audience", "agent", "--dest", base)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            generated = base / "release-notes"
            standardized = base / "standardized"
            standardized.mkdir()
            copy_support(standardized)
            for output in [generated, standardized]:
                for name in CHECKERS:
                    actual = output / "scripts" / name
                    self.assertTrue(actual.is_file(), str(actual))
                    self.assertEqual(actual.read_bytes(), (SCRIPTS / name).read_bytes())
                result = subprocess.run([sys.executable, str(output / "scripts/check_invocation_receipt.py"), "--help"],
                                        cwd=base, env={**os.environ, "PYTHONPATH": ""}, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("--receipt-sha256", result.stdout)
