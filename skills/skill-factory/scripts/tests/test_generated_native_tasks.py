"""A generated package runs its own installed compiler and real engine checks."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from cli import run


def native_gate(root):
    return subprocess.run(["mise", "run", "test-native"], cwd=root,
                          env={**os.environ, "MISE_TRUSTED_CONFIG_PATHS": str(root)},
                          capture_output=True, text=True, timeout=90)


class TestGeneratedNativeTasks(unittest.TestCase):
    def test_public_native_gate_installs_checks_and_recovers(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve() / "native-output"
            created = run("scaffold_skill.py", "--name", root.name,
                          "--description", "Use when native source checks are needed.",
                          "--scope", "project", "--audience", "human", "--dest", root.parent)
            self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
            self.assertFalse((root / "node_modules").exists())
            first = native_gate(root)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertIn("tests 11", first.stdout)
            source = root / "scripts/domain.ts"
            source.write_text('const result: number = "wrong";\n')
            rejected = native_gate(root)
            self.assertNotEqual(rejected.returncode, 0, rejected.stdout + rejected.stderr)
            self.assertIn("not assignable to type 'number'", rejected.stdout)
            source.write_text("const result: number = 1;\n")
            recovered = native_gate(root)
            self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
            self.assertIn("tests 11", recovered.stdout)


if __name__ == "__main__":
    unittest.main()
