"""Tests for canonical factory support-file propagation."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run, SKILL_DIR
from test_mapping_promotion import snapshot
from test_standardize_registry_skill import profile, write_target


class TestCanonicalCopy(unittest.TestCase):
    def test_apply_refreshes_the_writing_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            checker = root / "scripts/lint_writing.py"
            checker.write_text("print('stale')\n", encoding="utf-8")
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(profile()), encoding="utf-8")
            result = run("standardize_registry_skill.py", root, "--profile",
                         profile_path, "--scope", "user", "--apply")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("mise_section_lines", checker.read_text())

    def test_standardization_copies_the_locked_code_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            config = Path(temp) / "profile.json"
            config.write_text(json.dumps(profile()))
            result = run("standardize_registry_skill.py", root, "--profile",
                         config, "--scope", "user", "--apply")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for name in ["package.json", "package-lock.json", "tsconfig.json",
                         "scripts/check_code_rules.py", "scripts/check_javascript.ts",
                         "scripts/skill_package.py"]:
                self.assertEqual((root / name).read_bytes(), (SKILL_DIR / name).read_bytes())
            mise = (root / "mise.toml").read_text()
            self.assertIn('[tasks.check-runtime]', mise)
            self.assertIn('node = "24.18.0"', mise)
            self.assertIn('npm = "11.16.0"', mise)

    def test_conflicting_runtime_and_custom_checker_preserve_the_whole_target(self):
        for name in ["package.json", "tsconfig.json", "scripts/check_code_rules.py"]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root = Path(temp) / "clock-anchor"
                write_target(root)
                (root / name).write_text("custom owned content\n")
                before = snapshot(root)
                config = Path(temp) / "profile.json"
                config.write_text(json.dumps(profile()))
                result = run("standardize_registry_skill.py", root, "--profile",
                             config, "--scope", "user", "--apply")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("runtime", result.stderr)
                self.assertEqual(snapshot(root), before)


if __name__ == "__main__":
    unittest.main()
