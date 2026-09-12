"""Tests for canonical factory support-file propagation."""
import json
import tempfile
import unittest
from pathlib import Path

from standardization_test_support import reviewed_standardize

from cli import run, SKILL_DIR
from test_mapping_promotion import snapshot
from test_standardize_registry_skill import profile, write_target


check = unittest.TestCase()


def test_apply_refreshes_the_writing_gate():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "clock-anchor"
        write_target(root)
        checker = root / "scripts/lint_writing.py"
        checker.write_text("print('stale')\n", encoding="utf-8")
        profile_path = Path(temp) / "profile.json"
        profile_path.write_text(json.dumps(profile()), encoding="utf-8")
        result = reviewed_standardize(root, "--profile",
                     profile_path, "--scope", "user", "--apply")
        check.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        check.assertIn("mise_section_lines", checker.read_text())

def test_standardization_copies_the_locked_code_runtime():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "clock-anchor"
        write_target(root)
        config = Path(temp) / "profile.json"
        config.write_text(json.dumps(profile()))
        result = reviewed_standardize(root, "--profile",
                     config, "--scope", "user", "--apply")
        check.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for name in ["package.json", "package-lock.json", "tsconfig.json",
                     "scripts/check_code_rules.py", "scripts/check_javascript.ts",
                     "scripts/native_file_workflow.ts", "scripts/run_review_ledger.ts", "scripts/tests/test_native_runtime_review.py",
                         "scripts/render_file_graph.py", "scripts/tests/test_render_file_graph.py",
                     "scripts/skill_package.py", "scripts/sync_mise_primitives.py",
                     "scripts/tests/test_related_owner_write.py", "scripts/tests/test_catalog_review.py", "scripts/tests/test_sync_mise_primitives.py",
                     "examples/example-ledger-write.md", "examples/lineage-public-run.json",
                     "examples/catalog-public-run.json", "examples/registry-public-run.json",
                     "examples/graph-public-run.json"]:
            check.assertEqual((root / name).read_bytes(), (SKILL_DIR / name).read_bytes())
        mise = (root / "mise.toml").read_text()
        check.assertIn('[tasks.check-runtime]', mise)
        check.assertIn('[tasks.render-file-graph]', mise)
        check.assertIn('[tasks.setup-graph-renderer]', mise)
        check.assertIn('node = "24.18.0"', mise)
        check.assertIn('npm = "11.16.0"', mise)

def test_conflicting_runtime_and_custom_checker_preserve_the_whole_target():
    for name in ["package.json", "tsconfig.json", "scripts/check_code_rules.py"]:
        with check.subTest(name=name), tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            (root / name).write_text("custom owned content\n")
            before = snapshot(root)
            config = Path(temp) / "profile.json"
            config.write_text(json.dumps(profile()))
            result = reviewed_standardize(root, "--profile",
                         config, "--scope", "user", "--apply")
            check.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            check.assertIn("runtime", result.stderr)
            check.assertEqual(snapshot(root), before)


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(unittest.FunctionTestCase(value) for name, value in globals().items()
                              if name.startswith('test_') and callable(value))


if __name__ == '__main__':
    unittest.main()
