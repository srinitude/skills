"""Preserve real task programs when standardizing a skill."""
import json
import tempfile
import tomllib
import unittest
import subprocess
import sys
from pathlib import Path

from cli import run
from publication_fixtures import standardize
from test_standardize_registry_skill import profile, write_target
from test_standardization_inputs import prepare, invoke
from cli import SKILL_DIR


def files(root):
    return {str(path.relative_to(root)): path.read_bytes()
            for path in root.rglob("*") if path.is_file()}


def apply_target(root, task):
    write_target(root)
    config = root / "mise.toml"
    text = config.read_text().replace('run = ["mise run anchor"]', task)
    config.write_text(text)
    source = root.parent / "profile.json"
    source.write_text(json.dumps(profile()))
    before = files(root)
    result = standardize(root, "--profile", source,
                 "--scope", "user", "--apply")
    return result, before


class TestMisePreservation(unittest.TestCase):
    def test_ci_keeps_ordered_commands_and_arguments(self):
        commands = ["python3 scripts/anchor.py --format json", "python3 scripts/inspect.py"]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            result, _ = apply_target(root, "run = " + json.dumps(commands))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            ci = tomllib.loads((root / "mise.toml").read_text())["tasks"]["ci"]
            self.assertEqual(ci["run"], commands)
            self.assertEqual(ci["depends"], ["decision-policy", "test", "validate", "lint-writing",
                                            "lint-placeholders", "evals", "improvement-policy"])

    def test_multiline_program_and_nested_config_survive(self):
        task = 'run = """\nprint(\'depends = ["inside-program"]\')\n"""\nshell = "python3 -c"'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            result, _ = apply_target(root, task)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(task, (root / "mise.toml").read_text())

    def test_structured_dependencies_keep_arguments_and_environment(self):
        task = ('depends = [{task="anchor", args=["--format", "json"], '
                'env={ZONE="UTC"}}]\nrun = "python3 scripts/inspect.py"')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            result, _ = apply_target(root, task)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            ci = tomllib.loads((root / "mise.toml").read_text())["tasks"]["ci"]
            self.assertEqual(ci["depends"][0], {"task": "anchor", "args": ["--format", "json"],
                                                "env": {"ZONE": "UTC"}})

    def test_ambiguous_nested_mise_does_not_replace_the_target(self):
        task = 'run = ["mise run anchor --format json", "python3 scripts/inspect.py"]'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            result, before = apply_target(root, task)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("explicit", result.stderr)
            self.assertEqual(files(root), before)

    def test_profile_command_update_retains_other_execution_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            root, path, target = prepare(Path(temp))
            config = root / "mise.toml"
            extras = ('env = {ZONE="UTC"}\nrun_windows = "python scripts/inspect.py"\n'
                      'timeout = "20s"\nshell = "bash -c"\ndir = "."\n')
            config.write_text(config.read_text() + extras)
            before = files(root)
            result = invoke(root, path, target)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            actual = tomllib.loads((target / "mise.toml").read_text())["tasks"]["inspect-anchor"]
            for key, expected in tomllib.loads(extras).items():
                self.assertEqual(actual.get(key), expected, key)
            self.assertEqual(actual["run"], "uv run python scripts/inspect.py --format json")
            self.assertEqual(files(root), before)

    def test_missing_mise_uses_the_current_canonical_tool_defaults(self):
        with tempfile.TemporaryDirectory() as temp:
            root, path, target = prepare(Path(temp))
            (root / "mise.toml").unlink()
            result = invoke(root, path, target)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            actual = tomllib.loads((target / "mise.toml").read_text())
            expected = tomllib.loads((SKILL_DIR / "assets/mise-template.toml").read_text())
            self.assertEqual(actual["tools"], expected["tools"])

    def test_generated_contract_accepts_preserved_programs_and_typed_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            root, path, target = prepare(Path(temp))
            config = root / "mise.toml"
            replacement = ('run = "python3 scripts/inspect.py"\n'
                           'depends = [{task="anchor", optional=true, args=["--format", "json"]}]')
            config.write_text(config.read_text().replace('run = ["mise run anchor"]', replacement))
            result = invoke(root, path, target)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            checked = subprocess.run([sys.executable, str(target / "scripts/tests/test_package_contract.py")],
                                     capture_output=True, text=True, timeout=15)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)


if __name__ == "__main__":
    unittest.main()
