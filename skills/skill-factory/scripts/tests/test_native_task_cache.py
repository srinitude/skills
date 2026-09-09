"""The output's public code gate must not reuse a pass for newly added code."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from cli import run


class TestNativeTaskCache(unittest.TestCase):
    def test_warm_gate_rejects_a_new_unhandled_language(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve() / "native-cache"
            created = run("scaffold_skill.py", "--name", root.name,
                          "--description", "Use when source code needs checking.",
                          "--scope", "user", "--audience", "agent", "--dest", root.parent)
            self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
            install = subprocess.run(["npm", "ci", "--offline", "--ignore-scripts", "--no-fund"],
                                     cwd=root, capture_output=True, text=True, timeout=60)
            self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
            environment = {**os.environ, "MISE_TRUSTED_CONFIG_PATHS": str(root)}
            command = ["mise", "run", "lint-code"]
            first = subprocess.run(command, cwd=root, env=environment,
                                   capture_output=True, text=True, timeout=60)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            (root / "scripts/new-language.rs").write_text("fn main() {}\n")
            second = subprocess.run(command, cwd=root, env=environment,
                                    capture_output=True, text=True, timeout=60)
            self.assertNotEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertIn("no native checker", second.stdout)


if __name__ == "__main__":
    unittest.main()
