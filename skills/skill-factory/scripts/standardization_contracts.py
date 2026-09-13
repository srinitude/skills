"""Reconcile legacy package checks with the factory contract."""
import ast
import json
import re
from pathlib import Path


LEGACY_LAYOUT = '''    for name in REQUIRED_DIRS + ["scripts/tests"]:
        if not (skill / name).is_dir():
            problems.append(f"missing required directory: {name}/")
        elif body and f"{name}/" not in body:
            problems.append(f"body never references {name}/")
'''
CURRENT_LAYOUT = '''    for name in REQUIRED_DIRS + ["scripts/tests"]:
        if not (skill / name).is_dir():
            problems.append(f"missing required directory: {name}/")
    for name in ["references", "assets", "examples", "evals"]:
        if body and f"{name}/" not in body:
            problems.append(f"body never references {name}/")
'''
LEGACY_CI_TEMPLATE = '''"""Pin the {skill} task graph and one-entry workflow."""
import pathlib
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPECTED_CI_DEPENDS = {expected}


class TestPackageContract(unittest.TestCase):
    def test_ci_dependency_contract(self):
        with (ROOT / "mise.toml").open("rb") as handle:
            tasks = tomllib.load(handle)["tasks"]
        self.assertEqual(tasks["ci"]["depends"], EXPECTED_CI_DEPENDS)
        self.assertNotIn("run", tasks["ci"])

    def test_tasks_have_explicit_contracts(self):
        with (ROOT / "mise.toml").open("rb") as handle:
            tasks = tomllib.load(handle)["tasks"]
        for task in tasks.values():
            self.assertTrue(task.get("description"))
            self.assertIsInstance(task.get("depends"), list)
            self.assertNotIn("mise run", str(task.get("run", "")))

    def test_workflow_uses_one_mise_entry(self):
        path = ROOT / ".github/workflows/ci.yml"
        lines = path.read_text(encoding="utf-8").splitlines()
        runs = [line.strip() for line in lines if line.strip().startswith("- run:")]
        self.assertEqual(runs, ["- run: mise run ci"])


if __name__ == "__main__":
    unittest.main()
'''
# Exact historical template and assertion bytes identify automatic migrations.
CI_TEMPLATE = LEGACY_CI_TEMPLATE.replace('EXPECTED_CI_DEPENDS', 'EXPECTED_CI_TASK').replace(
    '        self.assertEqual(tasks["ci"]["depends"], EXPECTED_CI_TASK)\n        self.assertNotIn("run", tasks["ci"])',
    '        self.assertEqual(tasks["ci"], EXPECTED_CI_TASK)')
LEGACY_CI_ASSERTION = b'steps = self.tasks["ci"]["run"]\nself.assertIn(f"mise run {job}", " ".join(steps))\n'

SCRIPT_COMMAND_RE = re.compile(r"scripts/([\w./-]+\.py)")


def ci_contract(skill, task):
    return CI_TEMPLATE.format(skill=skill, expected=repr(task))


def cli_scripts(tasks):
    found = set()
    for task in tasks.values():
        run = task.get("run", "")
        commands = [run] if isinstance(run, str) else run if isinstance(run, list) else []
        for command in commands:
            found.update(Path(item).name for item in SCRIPT_COMMAND_RE.findall(command))
    return sorted(found)


def ci_binding(node):
    if not isinstance(node, ast.Assign) or len(node.targets) != 1:
        return False
    return isinstance(node.targets[0], ast.Name) and node.targets[0].id in ('EXPECTED_CI_DEPENDS', 'EXPECTED_CI_TASK')


def owned_ci_contract(old, skill):
    try:
        node = next((node for node in ast.parse(old).body if ci_binding(node)), None)
        if node is None:
            return False
        name = node.targets[0].id
        value = ast.literal_eval(node.value)
        expected = (LEGACY_CI_TEMPLATE.format(skill=skill, expected=json.dumps(value))
                    if name == 'EXPECTED_CI_DEPENDS' else ci_contract(skill, value))
        return old == expected.encode()
    except (SyntaxError, ValueError, TypeError):
        return False


def contract_files(files, tasks, profile):
    validator = 'scripts/validate_skill.py'
    if validator in files:
        files[validator] = files[validator].replace(LEGACY_LAYOUT.encode(), CURRENT_LAYOUT.encode())
    legacy = 'scripts/tests/test_ci_contract.py'
    target = legacy if legacy in files else 'scripts/tests/test_package_contract.py'
    old = files.get(target, b'')
    if not old or old == LEGACY_CI_ASSERTION or owned_ci_contract(old, profile['skill']):
        files[target] = ci_contract(profile['skill'], tasks['ci']).encode()
    help_path = 'scripts/tests/test_scripts.py'
    text = files.get(help_path, b'').decode('utf-8')
    old = '        scripts = sorted((SKILL_DIR / "scripts").glob("*.py"))'
    if old in text:
        marker = 'SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]\n'
        constant = marker + f'CLI_SCRIPTS = {json.dumps(cli_scripts(tasks))}\n'
        replacement = '        scripts = [SKILL_DIR / "scripts" / name for name in CLI_SCRIPTS]'
        files[help_path] = text.replace(marker, constant).replace(old, replacement).encode('utf-8')
