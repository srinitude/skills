"""Standardized outputs need their own public native validation path."""
import tempfile
import tomllib
import unittest
from pathlib import Path

from cli import SKILL_DIR
from test_generated_native_tasks import native_gate
from test_standardization_inputs import prepare, invoke
from skill_package import inventory


class TestStandardizedNativeTasks(unittest.TestCase):
    def test_prepared_output_runs_native_checks_without_source_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root, profile, candidate = prepare(Path(temp).resolve())
            before = inventory(root)
            prepared = invoke(root, profile, candidate)
            self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
            checked = native_gate(candidate)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertIn("tests 11", checked.stdout)
            self.assertEqual(inventory(root), before)
            config = tomllib.loads((candidate / "mise.toml").read_text())
            owner = tomllib.loads((SKILL_DIR / "mise.toml").read_text())
            self.assertEqual(config["tools"], owner["tools"])
            source = candidate / "scripts/domain.ts"
            source.write_text('const result: number = "wrong";\n')
            rejected = native_gate(candidate)
            self.assertNotEqual(rejected.returncode, 0, rejected.stdout + rejected.stderr)
            self.assertIn("not assignable to type 'number'", rejected.stdout)
            source.write_text("const result: number = 1;\n")
            recovered = native_gate(candidate)
            self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
            self.assertEqual(inventory(root), before)

    def test_preparation_preserves_existing_tool_and_environment_choices(self):
        with tempfile.TemporaryDirectory() as temp:
            root, profile, candidate = prepare(Path(temp).resolve())
            config = root / "mise.toml"
            prefix = '[tools]\npython = "3.12"\n\n[env]\nKEEP_VALUE = "retained"\n\n'
            config.write_text(prefix + config.read_text())
            before = inventory(root)
            result = invoke(root, profile, candidate)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            actual = tomllib.loads((candidate / "mise.toml").read_text())
            self.assertEqual(actual["tools"]["python"], "3.12")
            self.assertEqual(actual["env"]["KEEP_VALUE"], "retained")
            for tool in ["node", "uv", "shfmt"]:
                self.assertIn(tool, actual["tools"])
            self.assertEqual(inventory(root), before)


if __name__ == "__main__":
    unittest.main()
