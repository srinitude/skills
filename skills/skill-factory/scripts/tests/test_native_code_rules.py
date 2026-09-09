"""Use real language parsers to reject malformed and oversized owned code."""
import tempfile
import unittest
from pathlib import Path

from cli import run


def check(text, suffix):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / ("sample" + suffix)).write_text(text)
        return run("check_code_rules.py", root)


class TestNativeCodeRules(unittest.TestCase):
    def test_native_syntax_failures_reject_and_recover(self):
        cases = [
            (".ts", "export const value: number = ;", "export const value: number = 1;"),
            (".js", "export const value = ;", "export const value = 1;"),
            (".sh", "if then\n", "printf '%s\\n' ready\n"),
            (".json", '{"a":1,"a":2}', '{"a":1}'),
            (".json", '{"a":NaN}', '{"a":1}'),
            (".JSON", '{"a":NaN}', '{"a":1}'),
            (".toml", 'key = [', 'key = [1]'),
            (".TOML", 'key = [', 'key = [1]'),
            (".yaml", 'key: 1\nkey: 2\n', 'key: 1\n'),
        ]
        for suffix, bad, good in cases:
            with self.subTest(suffix=suffix, bad=bad):
                rejected = check(bad, suffix)
                self.assertNotEqual(rejected.returncode, 0, rejected.stdout + rejected.stderr)
                self.assertNotIn("Traceback", rejected.stderr)
                accepted = check(good, suffix)
                self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)

    def test_typescript_construct_and_nesting_limits_use_syntax_tree(self):
        cases = [
            "export function big() {\n" + "\n".join(f"  let v{i} = {i};" for i in range(31)) + "\n}",
            "export function deep(xs: number[][]) {\nfor (const x of xs) {\nif (x) {\nfor (const y of x) {\nif (y) {\nconsole.log(y);\n}\n}\n}\n}\n}",
            "\n".join(f"export const v{i} = {i};" for i in range(201)),
        ]
        for text in cases:
            with self.subTest(text=text[:50]):
                result = check(text, ".ts")
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("cap", result.stdout)
        comments = "/*\n" + "\n".join("A comment." for _ in range(220)) + "\n*/\nexport const n = 1;\n"
        result = check(comments, ".ts")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_shell_construct_and_nesting_limits_use_native_tree(self):
        cases = [
            "big() {\n" + "\n".join(f"  echo {i}" for i in range(31)) + "\n}\n",
            "deep() {\n" + "if true; then\n" * 4 + "echo value\n" + "fi\n" * 4 + "}\n",
            "cat <<'BODY'\n" + "# literal data\n" * 201 + "BODY\n",
        ]
        for text in cases:
            with self.subTest(text=text[:40]):
                result = check(text, ".sh")
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("cap", result.stdout)
        result = check("# comment\n" * 220 + "small() {\nprintf '%s' 'if { then } fi'\n}\n", ".sh")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unhandled_code_and_extensionless_scripts_cannot_silently_pass(self):
        for suffix, text in [(".rs", "fn main() {}"), (".TS", "export const value = ;"),
                             ("", "#!/usr/bin/env python3\ndef broken(\n")]:
            with self.subTest(suffix=suffix):
                result = check(text, suffix)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
