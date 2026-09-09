"""Tests for canonical factory support-file propagation."""
import json
import tempfile
import unittest
import subprocess
import sys
from pathlib import Path

from cli import run, SKILL_DIR
from publication_fixtures import standardize
from test_standardize_registry_skill import profile, write_target


class TestCanonicalCopy(unittest.TestCase):
    def test_native_checker_and_lock_are_independent_of_the_factory(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            result = run("scaffold_skill.py", "--name", "native-checks",
                         "--description", "Use when source syntax needs checking.",
                         "--scope", "user", "--audience", "agent", "--dest", base)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            root = base / "native-checks"
            for name in ["package.json", "package-lock.json", "tsconfig.json", "scripts/check_native_code.mjs"]:
                self.assertTrue((root / name).is_file(), name)
            package = json.loads((root / "package.json").read_text())
            owner = json.loads((SKILL_DIR / "package.json").read_text())
            self.assertEqual(package["dependencies"], owner["dependencies"])
            self.assertEqual(package["name"], "native-checks-workflows")
            installed = subprocess.run(["npm", "ci", "--offline", "--ignore-scripts", "--no-fund"],
                                       cwd=root, capture_output=True, text=True, timeout=60)
            self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
            code = root / "scripts/broken.ts"
            code.write_text("const value: number = ;")
            command = [sys.executable, str(root / "scripts/check_code_rules.py"), str(root)]
            rejected = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(rejected.returncode, 0)
            code.write_text("const value: number = 1;")
            accepted = subprocess.run(command, capture_output=True, text=True, timeout=30)
            self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)

    def test_apply_refreshes_the_writing_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            checker = root / "scripts/lint_writing.py"
            checker.write_text("print('stale')\n", encoding="utf-8")
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(profile()), encoding="utf-8")
            result = standardize(root, "--profile",
                         profile_path, "--scope", "user", "--apply")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("mise_section_lines", checker.read_text())


if __name__ == "__main__":
    unittest.main()
