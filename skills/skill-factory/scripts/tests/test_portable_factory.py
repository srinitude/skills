"""The factory's variant checks work outside the source registry."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR, SCRIPTS

sys.path.insert(0, str(SCRIPTS))
from skill_package import copy_owned, inventory, preserve_layout, unowned_entries


class TestPortableFactory(unittest.TestCase):
    def test_copied_factory_runs_variant_acceptance_without_registry_files(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            target = base / "standalone" / "skill-factory"
            expected = inventory(SKILL_DIR)
            copy_owned(SKILL_DIR, target)
            preserve_layout(SKILL_DIR, target)
            self.assertEqual(inventory(target), expected)
            self.assertEqual(list(unowned_entries(target)), [])
            env = dict(os.environ, MISE_TRUSTED_CONFIG_PATHS=str(target))
            runtime = subprocess.run(["mise", "run", "--force", "--task-cache", "off", "check-runtime"],
                cwd=target, env=env, capture_output=True, text=True, timeout=180)
            self.assertEqual(runtime.returncode, 0, runtime.stdout + runtime.stderr)
            self.assertEqual(inventory(target), expected)
            result = subprocess.run([sys.executable, "-I", "-m", "unittest", "discover", "-s",
                str(target / "scripts/tests"), "-p", "test_variant_acceptance.py", "-v"],
                cwd=base, capture_output=True, text=True, timeout=180)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Ran 2 tests", result.stderr)
            self.assertEqual(inventory(SKILL_DIR), expected)
