"""Runtime propagation must not silently combine unrelated dependency owners."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR
from runtime_package import copy_runtime
from skill_package import inventory
from test_standardization_inputs import prepare, invoke


class TestRuntimePackage(unittest.TestCase):
    def test_partial_or_incompatible_runtime_rejects_without_source_changes(self):
        cases = [("package-lock.json", {"name": "unrelated", "lockfileVersion": 3}),
                 ("package.json", {"name": "unrelated", "dependencies": {}}),
                 ("package.json", {"dependencies": None})]
        for name, data in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                root, profile, target = prepare(Path(temp))
                (root / name).write_text(json.dumps(data))
                before = inventory(root)
                result = invoke(root, profile, target)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("runtime", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(inventory(root), before)
                self.assertFalse(target.exists())
                (root / name).unlink()
                recovered = invoke(root, profile, target)
                self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)

    def test_compatible_existing_runtime_keeps_its_metadata_and_compiler_options(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            copy_runtime(SKILL_DIR, root)
            package = root / "package.json"
            data = json.loads(package.read_text())
            data["description"] = "A preserved independent package."
            package.write_text(json.dumps(data))
            config = root / "tsconfig.json"
            data = json.loads(config.read_text())
            data["compilerOptions"]["noUnusedLocals"] = True
            config.write_text(json.dumps(data))
            before = inventory(root)
            copy_runtime(SKILL_DIR, root)
            self.assertEqual(inventory(root), before)

    def test_changed_sdk_or_lock_rejects_at_public_preparation_and_recovers(self):
        for filename in ["package.json", "package-lock.json"]:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as temp:
                root, profile, target = prepare(Path(temp))
                copy_runtime(SKILL_DIR, root)
                path = root / filename
                original = path.read_bytes()
                data = json.loads(original)
                if filename == "package.json":
                    data["dependencies"]["@mastra/core"] = "0.0.0"
                else:
                    data["packages"][""]["dependencies"] = {}
                path.write_text(json.dumps(data))
                before = inventory(root)
                result = invoke(root, profile, target)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("runtime", result.stderr)
                self.assertEqual(inventory(root), before)
                self.assertFalse(target.exists())
                path.write_bytes(original)
                recovered = invoke(root, profile, target)
                self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)


if __name__ == "__main__":
    unittest.main()
