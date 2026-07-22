"""Helpers for invoking the bundled scripts in tests."""
import pathlib
import subprocess
import sys

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = SKILL_DIR / "scripts"


def run(script, *args, cwd=None):
    """Run a bundled script with real arguments and capture the result."""
    cmd = [sys.executable, str(SCRIPTS / script)]
    cmd.extend(str(arg) for arg in args)
    return subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd, timeout=180
    )
