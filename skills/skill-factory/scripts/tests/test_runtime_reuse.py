"""Real setup must reuse valid installs and preserve them after failed repair."""
import json
import os
import tempfile
import unittest
from pathlib import Path

from test_rule_workflow import fixture, run_bounded


def setup(root):
    return run_bounded(["mise", "run", "setup-runtime"], cwd=root,
                       env={**os.environ, "MISE_TRUSTED_CONFIG_PATHS": str(root)}, timeout=120)


def test_warm_setup_preserves_installed_files_and_recovers_invalid_lock(self):
    with tempfile.TemporaryDirectory() as temporary:
        root, _ = fixture(Path(temporary).resolve())
        sentinel = root / "node_modules/.retained-state"
        sentinel.write_bytes(b"Existing runtime state")
        inode = sentinel.stat().st_ino
        warm = setup(root)
        self.assertEqual(warm.returncode, 0, warm.stdout + warm.stderr)
        self.assertTrue(sentinel.exists(), "warm setup removed existing runtime state")
        self.assertEqual(sentinel.stat().st_ino, inode)
        package = root / "package.json"
        before = package.read_bytes()
        invalid = json.loads(before)
        invalid["dependencies"]["missing-from-frozen-lock"] = "1.0.0"
        package.write_text(json.dumps(invalid))
        failed = setup(root)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(sentinel.read_bytes(), b"Existing runtime state")
        self.assertEqual(sentinel.stat().st_ino, inode)
        package.write_bytes(before)
        recovered = setup(root)
        self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
        self.assertEqual(sentinel.stat().st_ino, inode)


def test_broken_storage_import_is_rebuilt_without_replacing_valid_root(self):
    with tempfile.TemporaryDirectory() as temporary:
        root, _ = fixture(Path(temporary).resolve())
        sentinel = root / "node_modules/.retained-state"
        sentinel.write_bytes(b"Keep valid root")
        storage = root / "runtime/standardization/node_modules/@mastra/libsql"
        package = json.loads((storage / "package.json").read_text())
        module = storage / package["exports"]["."]["import"]["default"]
        original = module.read_bytes()
        module.write_bytes(b"throw Error('broken storage fixture');\n")
        repaired = setup(root)
        self.assertEqual(repaired.returncode, 0, repaired.stdout + repaired.stderr)
        self.assertIn("broken storage fixture", repaired.stderr)
        self.assertEqual(module.read_bytes(), original)
        self.assertEqual(sentinel.read_bytes(), b"Keep valid root")
        failures = list((root / ".artifacts").glob("runtime-*/prior/@mastra/libsql/dist/index.js"))
        self.assertTrue(any(path.read_bytes() == b"throw Error('broken storage fixture');\n" for path in failures))


def load_tests(loader, tests, pattern):
    case = type("RuntimeReuseTests", (unittest.TestCase,), {
        "test_warm_setup_preserves_installed_files_and_recovers_invalid_lock":
            test_warm_setup_preserves_installed_files_and_recovers_invalid_lock,
        "test_broken_storage_import_is_rebuilt_without_replacing_valid_root":
            test_broken_storage_import_is_rebuilt_without_replacing_valid_root})
    return loader.loadTestsFromTestCase(case)
