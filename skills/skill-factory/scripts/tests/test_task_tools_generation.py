"""A generated skill must run its copied protocol checks with its own runtime."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_scaffold_skill import scaffold


def test_generated_skill_task_tools():
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary).resolve()
        result = scaffold(base, "tools-trial", "Use when a task tool trial is requested.")
        assert result.returncode == 0, result.stdout + result.stderr
        root = base / "tools-trial"
        assert (root / "scripts/task_tools.ts").is_file()
        for pattern in ["test_task_tools.py", "test_task_tools_handoff.py"]:
            result = subprocess.run(
                ["mise", "run", "test", "--", "-p", pattern], cwd=root,
                env={**os.environ, "MISE_TRUSTED_CONFIG_PATHS": str(root)},
                text=True, capture_output=True, timeout=180)
            assert result.returncode == 0, result.stdout + result.stderr
            assert "Ran 1 test" in result.stderr and "OK" in result.stderr


def load_tests(loader, tests, pattern):
    return unittest.TestSuite([unittest.FunctionTestCase(test_generated_skill_task_tools)])
