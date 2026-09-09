"""The factory's variant checks work outside the source registry."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR


class TestPortableFactory(unittest.TestCase):
    def test_copied_factory_runs_variant_acceptance_without_registry_files(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            target = base / "standalone" / "skill-factory"
            shutil.copytree(SKILL_DIR, target,
                            ignore=shutil.ignore_patterns(".mise", ".artifacts", "__pycache__"))
            result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s",
                str(target / "scripts/tests"), "-p", "test_variant_acceptance.py", "-v"],
                cwd=base, capture_output=True, text=True, timeout=180)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Ran 2 tests", result.stderr)
