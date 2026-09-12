"""Exercise JavaScript/TypeScript rules through the actual public code checker."""
import tempfile
import unittest
from pathlib import Path

from cli import run


def _TestJavaScriptRules_check(self, text, suffix=".ts", directory=False):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        path = root / ("sample" + suffix)
        path.write_text(text)
        return run("check_code_rules.py", root if directory else path)

def _TestJavaScriptRules_test_dependency_and_cache_trees_are_excluded(self):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        for name in ["node_modules", ".git", ".artifacts", "__pycache__"]:
            folder = root / name
            folder.mkdir()
            (folder / "broken.ts").write_text("const broken: = ;")
            (folder / "broken.py").write_text("def broken(")
        (root / "valid.ts").write_text("export const good = 1;")
        result = run("check_code_rules.py", root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("checked 1 files", result.stdout)

def _TestJavaScriptRules_test_discovers_all_supported_extensions(self):
    large = "\n".join(f"const item{n} = {n};" for n in range(201))
    for suffix in [".js", ".mjs", ".cjs", ".jsx", ".ts", ".mts", ".cts", ".tsx"]:
        with self.subTest(suffix=suffix):
            result = self.check(large, suffix, directory=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("200", result.stdout)

def _TestJavaScriptRules_test_real_ast_rejects_invalid_syntax(self):
    result = self.check("export const broken: = ;")
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.assertIn("does not parse", result.stdout)

def _TestJavaScriptRules_test_functions_methods_and_arrows_obey_construct_cap(self):
    body = "\n".join(f"  const item{n} = {n};" for n in range(31))
    for source in [f"function big() {{\n{body}\n}}",
                   f"const big = () => {{\n{body}\n}};",
                   f"class Small {{ big() {{\n{body}\n}} }}"]:
        with self.subTest(source=source[:35]):
            result = self.check(source)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("cap is 30", result.stdout)

def _TestJavaScriptRules_test_nested_blocks_are_counted(self):
    result = self.check("function deep() { if (true) { while (true) { "
                        "for (;;) { if (true) { break; } } } } }")
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.assertIn("nesting", result.stdout)

def _TestJavaScriptRules_test_comments_and_literal_content_count_physical_lines(self):
    comments = "/*\n" + "comment\n" * 210 + "*/\nexport const good = 1;\n"
    result = self.check(comments)
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    literal = "const content = `\n" + "literal\n" * 210 + "`;\n"
    result = self.check(literal)
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

def _TestJavaScriptRules_test_whole_class_includes_method_bodies(self):
    methods = "\n".join(f"method{n}() {{\nreturn {n};\n}}" for n in range(20))
    result = self.check("class Methods {\n" + methods + "\n}\n")
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

def _TestJavaScriptRules_test_unknown_code_extension_fails_explicitly(self):
    result = self.check("print('value')", ".lua")
    self.assertNotEqual(result.returncode, 0)
    self.assertIn("unsupported", result.stdout + result.stderr)

def _TestJavaScriptRules_test_interfaces_enums_and_aliases_are_whole_constructs(self):
    fields = "\n".join(f"  value{n}: string;" for n in range(31))
    members = "\n".join(f"  value{n}," for n in range(31))
    for source in [f"interface Whole {{\n{fields}\n}}", f"type Whole = {{\n{fields}\n}};", f"enum Whole {{\n{members}\n}}"]:
        result = self.check(source)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("cap is 30", result.stdout)

def _TestJavaScriptRules_test_file_scope_depth_and_physical_boundaries(self):
    deep = "if (true) { if (true) { if (true) { if (true) {} } } }"
    self.assertEqual(self.check(deep).returncode, 1)
    self.assertEqual(self.check("// line\n" * 200).returncode, 0)
    self.assertEqual(self.check("// line\n" * 201).returncode, 1)
    chain = "if (false) {} " + "else if (false) {} " * 8
    self.assertEqual(self.check(chain).returncode, 0)


def _TestJavaScriptRules_test_all_physical_line_separators_keep_the_boundary(self):
    separators = ("\n", "\r", "\r\n", "\v", "\f", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029")
    for separator in separators:
        for size, code in [(200, 0), (201, 1)]:
            result = self.check("/*" + separator * (size - 1) + "*/")
            self.assertEqual(result.returncode, code, repr(separator) + result.stdout + result.stderr)


class TestJavaScriptRules(unittest.TestCase):
    test_all_physical_line_separators_keep_the_boundary = _TestJavaScriptRules_test_all_physical_line_separators_keep_the_boundary
    check = _TestJavaScriptRules_check
    test_discovers_all_supported_extensions = _TestJavaScriptRules_test_discovers_all_supported_extensions
    test_real_ast_rejects_invalid_syntax = _TestJavaScriptRules_test_real_ast_rejects_invalid_syntax
    test_functions_methods_and_arrows_obey_construct_cap = _TestJavaScriptRules_test_functions_methods_and_arrows_obey_construct_cap
    test_nested_blocks_are_counted = _TestJavaScriptRules_test_nested_blocks_are_counted
    test_comments_and_literal_content_count_physical_lines = _TestJavaScriptRules_test_comments_and_literal_content_count_physical_lines
    test_whole_class_includes_method_bodies = _TestJavaScriptRules_test_whole_class_includes_method_bodies
    test_dependency_and_cache_trees_are_excluded = _TestJavaScriptRules_test_dependency_and_cache_trees_are_excluded
    test_unknown_code_extension_fails_explicitly = _TestJavaScriptRules_test_unknown_code_extension_fails_explicitly
    test_interfaces_enums_and_aliases_are_whole_constructs = _TestJavaScriptRules_test_interfaces_enums_and_aliases_are_whole_constructs
    test_file_scope_depth_and_physical_boundaries = _TestJavaScriptRules_test_file_scope_depth_and_physical_boundaries


if __name__ == "__main__":
    unittest.main()
