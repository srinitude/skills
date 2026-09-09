"""Publication retains destination-local data and excludes it from new outputs."""
import shutil
import stat
import tempfile
import unittest
from pathlib import Path

from acceptance_fixtures import setup
from test_promotion_acceptance import bindings
from test_standardization_inputs import prepare, invoke
from skill_package import inventory, promote, replace_directory, tree_digest


class TestPackageRuntimePreservation(unittest.TestCase):
    def test_preparation_does_not_copy_runtime_or_repository_state(self):
        with tempfile.TemporaryDirectory() as temp:
            root, path, candidate = prepare(Path(temp).resolve())
            root.chmod(0o700)
            (root / "scripts").chmod(0o700)
            (root / "empty-local-directory").mkdir(mode=0o700)
            for name in [".git/config", ".venv/lib/cache.py", ".artifacts/private.json"]:
                file = root / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text("Unrelated local state.\n")
            before = inventory(root)
            result = invoke(root, path, candidate)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for name in [".git", ".venv", ".artifacts"]:
                self.assertFalse((candidate / name).exists(), name)
                self.assertTrue((root / name).exists(), name)
            self.assertEqual(inventory(root), before)
            for name in [".", "scripts", "empty-local-directory"]:
                self.assertEqual(stat.S_IMODE((candidate / name).stat().st_mode), 0o700, name)

    def test_guarded_promotion_preserves_current_destination_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            stage, context, receipt, _, _ = setup(base)
            target = base / "destination" / stage.name
            shutil.copytree(stage, target)
            target.chmod(0o700)
            before = inventory(target)
            (target / ".artifacts").mkdir()
            (target / ".artifacts/current.json").write_text("Current result.\n")
            (stage / ".artifacts").mkdir()
            (stage / ".artifacts/stale.json").write_text("Stale result.\n")
            (target / ".git").mkdir()
            (target / ".git/config").write_text("Existing authority.\n")
            runtime = base / "runtime"
            runtime.mkdir()
            (target / "node_modules").symlink_to(runtime, target_is_directory=True)
            expected = {"route": "variant", "inputs": {"candidate": tree_digest(inventory(stage))}}
            trusted = bindings(base, context, receipt, target, expected)
            promote(stage, target, before, acceptance=(expected, trusted))
            self.assertEqual((target / ".artifacts/current.json").read_text(), "Current result.\n")
            self.assertFalse((target / ".artifacts/stale.json").exists())
            self.assertEqual((target / ".git/config").read_text(), "Existing authority.\n")
            self.assertTrue((target / "node_modules").is_symlink())
            self.assertEqual((target / "node_modules").resolve(), runtime)
            self.assertEqual(inventory(target), before)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o700)

    def test_failed_runtime_transfer_restores_the_original_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            target, stage = base / "target", base / "stage"
            (target / ".git").mkdir(parents=True)
            (target / ".git/config").write_text("Keep repository state.\n")
            (target / "z").mkdir()
            (target / "z/.DS_Store").write_bytes(b"keep-local")
            stage.mkdir()
            (stage / "z").write_text("Conflicts with destination-local directory.\n")
            with self.assertRaises(OSError):
                replace_directory(stage, target)
            self.assertEqual((target / ".git/config").read_text(), "Keep repository state.\n")
            self.assertEqual((target / "z/.DS_Store").read_bytes(), b"keep-local")
            self.assertEqual((stage / "z").read_text(), "Conflicts with destination-local directory.\n")


if __name__ == "__main__":
    unittest.main()
