"""Tests for scripts/check_code_rules.py against real code files."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR, run


class TestCheckCodeRulesCli(unittest.TestCase):
    def test_help_documents_usage_and_exit_codes(self):
        result = run("check_code_rules.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        self.assertIn("exit code", result.stdout.lower())

    def test_missing_target_is_a_usage_error(self):
        result = run("check_code_rules.py")
        self.assertEqual(result.returncode, 2)


def _TestCheckCodeRules_check_source(self, source, suffix=".py"):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"sample{suffix}"
        path.write_text(source, encoding="utf-8")
        return run("check_code_rules.py", path)

def _TestCheckCodeRules_test_own_code_passes(self):
    result = run("check_code_rules.py", SKILL_DIR)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

def _TestCheckCodeRules_test_missing_native_dependency_preserves_the_actual_failure(self):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for name in ["check_code_rules.py", "check_javascript.ts", "skill_package.py"]:
            shutil.copy2(SKILL_DIR / "scripts" / name, root / name)
        source = root / "sample.js"
        source.write_text("export const answer = 42;\n")
        result = subprocess.run([sys.executable, str(root / "check_code_rules.py"),
                                 str(source)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("JavaScript/TypeScript checker", result.stderr)
        self.assertIn("ERR_MODULE_NOT_FOUND", result.stderr)
        self.assertIn("typescript", result.stderr)

def _TestCheckCodeRules_test_small_clean_file_passes(self):
    result = self.check_source("def add(a, b):\n    return a + b\n")
    self.assertEqual(result.returncode, 0)

def _TestCheckCodeRules_test_long_expression_does_not_become_block_nesting(self):
    source = "def total(x):\n    return " + "+".join(["x"] * 1500) + "\n"
    result = self.check_source(source)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

def _TestCheckCodeRules_test_parser_depth_limit_is_reported_without_traceback(self):
    source = "def total(x):\n    return " + "+".join(["x"] * 5000) + "\n"
    result = self.check_source(source)
    self.assertEqual(result.returncode, 1)
    self.assertIn("does not parse", result.stdout)
    self.assertNotIn("Traceback", result.stderr)

def _TestCheckCodeRules_test_file_over_200_loc_fails(self):
    source = "\n".join(f"x{i} = {i}" for i in range(201)) + "\n"
    result = self.check_source(source)
    self.assertEqual(result.returncode, 1)
    self.assertIn("200", result.stdout)

def _TestCheckCodeRules_test_function_over_30_loc_fails(self):
    lines = [f"    y{i} = {i}" for i in range(31)]
    source = "def big():\n" + "\n".join(lines) + "\n    return y0\n"
    result = self.check_source(source)
    self.assertEqual(result.returncode, 1)
    self.assertIn("big", result.stdout)

def _TestCheckCodeRules_test_nesting_over_three_fails(self):
    source = (
        "def deep(rows):\n"
        "    for row in rows:\n"
        "        if row:\n"
        "            for cell in row:\n"
        "                if cell:\n"
        "                    print(cell)\n"
    )
    result = self.check_source(source)
    self.assertEqual(result.returncode, 1)
    self.assertIn("nesting", result.stdout)

def _TestCheckCodeRules_test_placeholder_marker_fails(self):
    marker = "TO" + "DO"
    result = self.check_source(f"# {marker}: finish later\nx = 1\n")
    self.assertEqual(result.returncode, 1)

def _TestCheckCodeRules_test_shell_file_over_200_loc_fails(self):
    source = "\n".join(f"echo {i}" for i in range(201)) + "\n"
    result = self.check_source(source, suffix=".sh")
    self.assertEqual(result.returncode, 1)

def _TestCheckCodeRules_test_physical_comments_and_blank_lines_count(self):
    for source in ["# comment\n" * 201, "\n" * 201]:
        result = self.check_source(source)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("201 physical lines", result.stdout)

def _TestCheckCodeRules_test_whole_class_and_decorators_count(self):
    methods = "\n".join(f"    def m{n}(self):\n        return {n}" for n in range(16))
    decorated = "@decorator\n" * 30 + "def small():\n    pass\n"
    for source in ["class Whole:\n" + methods, decorated]:
        result = self.check_source(source)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("cap is 30", result.stdout)

def _TestCheckCodeRules_test_file_scope_blocks_count_and_elif_is_a_peer(self):
    rejected = "if True:\n    if True:\n        if True:\n            if True:\n                pass\n"
    self.assertEqual(self.check_source(rejected).returncode, 1)
    accepted = "if False:\n    pass\n" + "elif False:\n    pass\n" * 8
    self.assertEqual(self.check_source(accepted).returncode, 0)

def _TestCheckCodeRules_test_physical_boundary_is_inclusive(self):
    self.assertEqual(self.check_source("# line\n" * 200).returncode, 0)
    body = "def exact():\n" + "    pass\n" * 29
    self.assertEqual(self.check_source(body).returncode, 0)


def _TestCheckCodeRules_test_lambda_obeys_function_size_and_nesting(self):
    source = "value = lambda: (\n" + "    # retained physical line\n" * 30 + "    1\n)\n"
    self.assertEqual(self.check_source(source).returncode, 1)
    nested = "if True:\n    if True:\n        if True:\n            value = lambda: 1\n"
    self.assertEqual(self.check_source(nested).returncode, 1)
    self.assertEqual(self.check_source("value = lambda: 1\n").returncode, 0)


class TestCheckCodeRules(unittest.TestCase):
    test_lambda_obeys_function_size_and_nesting = _TestCheckCodeRules_test_lambda_obeys_function_size_and_nesting
    check_source = _TestCheckCodeRules_check_source
    test_own_code_passes = _TestCheckCodeRules_test_own_code_passes
    test_missing_native_dependency_preserves_the_actual_failure = _TestCheckCodeRules_test_missing_native_dependency_preserves_the_actual_failure
    test_small_clean_file_passes = _TestCheckCodeRules_test_small_clean_file_passes
    test_long_expression_does_not_become_block_nesting = _TestCheckCodeRules_test_long_expression_does_not_become_block_nesting
    test_parser_depth_limit_is_reported_without_traceback = _TestCheckCodeRules_test_parser_depth_limit_is_reported_without_traceback
    test_file_over_200_loc_fails = _TestCheckCodeRules_test_file_over_200_loc_fails
    test_function_over_30_loc_fails = _TestCheckCodeRules_test_function_over_30_loc_fails
    test_nesting_over_three_fails = _TestCheckCodeRules_test_nesting_over_three_fails
    test_placeholder_marker_fails = _TestCheckCodeRules_test_placeholder_marker_fails
    test_shell_file_over_200_loc_fails = _TestCheckCodeRules_test_shell_file_over_200_loc_fails
    test_physical_comments_and_blank_lines_count = _TestCheckCodeRules_test_physical_comments_and_blank_lines_count
    test_whole_class_and_decorators_count = _TestCheckCodeRules_test_whole_class_and_decorators_count
    test_file_scope_blocks_count_and_elif_is_a_peer = _TestCheckCodeRules_test_file_scope_blocks_count_and_elif_is_a_peer
    test_physical_boundary_is_inclusive = _TestCheckCodeRules_test_physical_boundary_is_inclusive


if __name__ == "__main__":
    unittest.main()
