"""Exercise JavaScript/TypeScript rules through the actual public code checker."""
import tempfile
import unittest
from pathlib import Path

from cli import run


class TestJavaScriptRules(unittest.TestCase):
    def check(self, text, suffix=".ts", directory=False):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / ("sample" + suffix)
            path.write_text(text)
            return run("check_code_rules.py", root if directory else path)

    def test_discovers_all_supported_extensions(self):
        large = "\n".join(f"const item{n} = {n};" for n in range(201))
        for suffix in [".js", ".mjs", ".cjs", ".jsx", ".ts", ".mts", ".cts", ".tsx"]:
            with self.subTest(suffix=suffix):
                result = self.check(large, suffix, directory=True)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("200", result.stdout)

    def test_real_ast_rejects_invalid_syntax(self):
        result = self.check("export const broken: = ;")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("does not parse", result.stdout)

    def test_functions_methods_and_arrows_obey_construct_cap(self):
        body = "\n".join(f"  const item{n} = {n};" for n in range(31))
        for source in [f"function big() {{\n{body}\n}}",
                       f"const big = () => {{\n{body}\n}};",
                       f"class Small {{ big() {{\n{body}\n}} }}"]:
            with self.subTest(source=source[:35]):
                result = self.check(source)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("cap is 30", result.stdout)

    def test_nested_blocks_are_counted(self):
        result = self.check("function deep() { if (true) { while (true) { "
                            "for (;;) { if (true) { break; } } } } }")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("nesting", result.stdout)

    def test_comments_are_excluded_but_literal_content_is_code(self):
        comments = "/*\n" + "comment\n" * 210 + "*/\nexport const good = 1;\n"
        result = self.check(comments)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        literal = "const content = `\n" + "literal\n" * 210 + "`;\n"
        result = self.check(literal)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_class_own_lines_exclude_method_bodies(self):
        methods = "\n".join(f"method{n}() {{\nreturn {n};\n}}" for n in range(20))
        result = self.check("class Methods {\n" + methods + "\n}\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_dependency_and_cache_trees_are_excluded(self):
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

    def test_unknown_code_extension_fails_explicitly(self):
        result = self.check("print('value')", ".lua")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsupported", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
