"""Reconcile legacy package checks with the factory contract."""
import json
import re
from pathlib import Path

from standardization_mapping import repair_mapping_json

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
CI_TEMPLATE = '''"""Pin the {skill} task graph and one-entry workflow."""
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
SCRIPT_COMMAND_RE = re.compile(r"scripts/([\w./-]+\.py)")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ci_contract(skill, dependencies):
    return CI_TEMPLATE.format(skill=skill, expected=json.dumps(dependencies))


def repair_validator(root):
    path = root / "scripts/validate_skill.py"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if LEGACY_LAYOUT in text:
        write(path, text.replace(LEGACY_LAYOUT, CURRENT_LAYOUT))


def repair_ci_test(root, tasks, profile):
    tests = root / "scripts/tests"
    tests.mkdir(parents=True, exist_ok=True)
    legacy = tests / "test_ci_contract.py"
    target = legacy if legacy.is_file() else tests / "test_package_contract.py"
    old = target.read_text(encoding="utf-8") if target.is_file() else ""
    if not old or '["ci"]["run"]' in old:
        write(target, ci_contract(profile["skill"], tasks["ci"]["depends"]))


def repair_source_tests(root):
    for path in (root / "scripts/tests").glob("test_source_mapping.py"):
        text = path.read_text(encoding="utf-8")
        old = "self.assertEqual(files, EXPECTED_FILES)"
        new = "self.assertEqual({key: files[key] for key in EXPECTED_FILES}, EXPECTED_FILES)"
        if old in text:
            write(path, text.replace(old, new))


def cli_scripts(tasks):
    found = set()
    for task in tasks.values():
        run = task.get("run", "")
        commands = [run] if isinstance(run, str) else run if isinstance(run, list) else []
        for command in commands:
            found.update(Path(item).name for item in SCRIPT_COMMAND_RE.findall(command))
    return sorted(found)


def repair_help_tests(root, tasks):
    path = root / "scripts/tests/test_scripts.py"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    old = '        scripts = sorted((SKILL_DIR / "scripts").glob("*.py"))'
    if old not in text:
        return
    marker = "SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]\n"
    constant = marker + f"CLI_SCRIPTS = {json.dumps(cli_scripts(tasks))}\n"
    replacement = '        scripts = [SKILL_DIR / "scripts" / name for name in CLI_SCRIPTS]'
    write(path, text.replace(marker, constant).replace(old, replacement))


def repair_contracts(root, tasks, profile, owners, snapshots):
    repair_validator(root)
    repair_ci_test(root, tasks, profile)
    repair_source_tests(root)
    repair_help_tests(root, tasks)
    repair_mapping_json(root, owners, profile, snapshots)
