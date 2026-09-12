"""Execute generated CI contracts against retained commands and subsequent changes."""
import runpy
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from cli import SCRIPTS

sys.path.insert(0, str(SCRIPTS))
from standardization_contracts import contract_files

PATH = 'scripts/tests/test_package_contract.py'
SOURCE = '[tasks.ci]\ndescription = "Check the clock"\ndepends = []\nrun = ["python3 first.py", "python3 second.py"]\nhide = true\nenv = { TZ = "UTC" }\n'


def generated(files, source):
    contract_files(files, tomllib.loads(source)['tasks'], {'skill': 'clock-anchor'})
    return files[PATH]


def check_contract(code, source):
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        target = root / PATH
        target.parent.mkdir(parents=True)
        target.write_bytes(code)
        (root / 'mise.toml').write_text(source)
        module = runpy.run_path(str(target))
        module['TestPackageContract']().test_ci_dependency_contract()


def _TestGeneratedCIContract_test_custom_ci_contract_passes_and_command_drift_fails(self):
    code = generated({}, SOURCE)
    check_contract(code, SOURCE)
    with self.assertRaises(AssertionError):
        check_contract(code, SOURCE.replace('first.py', 'changed.py'))
    with self.assertRaises(AssertionError):
        check_contract(code, SOURCE.replace('UTC', 'Asia/Kolkata'))

def _TestGeneratedCIContract_test_exact_generated_contract_is_refreshed_for_changed_commands(self):
    files = {}
    before = generated(files, SOURCE)
    changed = SOURCE.replace('second.py', 'corrected.py')
    after = generated(files, changed)
    self.assertNotEqual(before, after)
    check_contract(after, changed)

def _TestGeneratedCIContract_test_customized_contract_is_preserved_for_explicit_review(self):
    files = {}
    custom = generated(files, SOURCE) + b'\nDOMAIN_CHECK = "preserve-me"\n'
    files[PATH] = custom
    generated(files, SOURCE.replace('second.py', 'corrected.py'))
    self.assertEqual(files[PATH], custom)

def _TestGeneratedCIContract_test_custom_legacy_run_assertion_is_not_replaced(self):
    custom = b'from unittest import TestCase\nclass Domain(TestCase):\n    def test_domain(self):\n        self.assertIn("domain-check", self.tasks["ci"]["run"])\n'
    files = {PATH: custom}
    generated(files, SOURCE)
    self.assertEqual(files[PATH], custom)

def _TestGeneratedCIContract_test_exact_legacy_generated_contract_is_migrated(self):
    files = {PATH: LEGACY}
    updated = generated(files, SOURCE)
    self.assertNotEqual(updated, LEGACY)
    check_contract(updated, SOURCE)


def run_test_probe(command, outcome):
    import shlex
    import subprocess
    args = shlex.split(command)
    args = args[args.index("python") + 1:]
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        tests = root / "scripts/tests"
        tests.mkdir(parents=True)
        (tests / "test_probe.py").write_text(
            "import unittest\nfrom pathlib import Path\n"
            "class Probe(unittest.TestCase):\n"
            "    def test_a(self):\n        " + outcome + "\n"
            "    def test_b(self):\n        Path('visited').touch()\n")
        result = subprocess.run([sys.executable, *args], cwd=root,
                                capture_output=True, text=True, timeout=10)
        return result, (root / "visited").exists()


def _test_commands_stop_after_failure_and_run_all_after_recovery(self):
    from standardization_seed import base_mise
    from standardization_mise import normalize_mise
    root = SCRIPTS.parent
    sources = [(root / name).read_text() for name in ["mise.toml", "assets/mise-template.toml"]]
    sources += [base_mise({"primary_term": "probe"}), normalize_mise("[tasks.ci]\ndepends = []\n")]
    from itertools import product
    tasks = [tomllib.loads(source)["tasks"]["test"] for source in sources]
    commands = [task[key] for task in tasks for key in ["run", "run_windows"] if key in task]
    outcomes = ["raise AssertionError('probe-failure')", "raise RuntimeError('probe-error')", "pass"]
    for command, outcome in product(commands, outcomes):
        with self.subTest(command=command, outcome=outcome):
            result, visited = run_test_probe(command, outcome)
            failed = outcome != "pass"
            self.assertEqual(result.returncode, int(failed), result.stderr)
            self.assertEqual(visited, not failed, result.stderr)
            self.assertIn("Ran 1 test" if failed else "Ran 2 tests", result.stderr)
            self.assertIn("probe-" if failed else "OK", result.stderr)


class TestGeneratedCIContract(unittest.TestCase):
    test_commands_stop_after_failure_and_run_all_after_recovery = _test_commands_stop_after_failure_and_run_all_after_recovery
    test_custom_ci_contract_passes_and_command_drift_fails = _TestGeneratedCIContract_test_custom_ci_contract_passes_and_command_drift_fails
    test_exact_generated_contract_is_refreshed_for_changed_commands = _TestGeneratedCIContract_test_exact_generated_contract_is_refreshed_for_changed_commands
    test_customized_contract_is_preserved_for_explicit_review = _TestGeneratedCIContract_test_customized_contract_is_preserved_for_explicit_review
    test_custom_legacy_run_assertion_is_not_replaced = _TestGeneratedCIContract_test_custom_legacy_run_assertion_is_not_replaced
    test_exact_legacy_generated_contract_is_migrated = _TestGeneratedCIContract_test_exact_legacy_generated_contract_is_migrated


# Exact previous generated contract retained as compatibility evidence.
LEGACY = b'"""Pin the clock-anchor task graph and one-entry workflow."""\nimport pathlib\nimport tomllib\nimport unittest\n\nROOT = pathlib.Path(__file__).resolve().parents[2]\nEXPECTED_CI_DEPENDS = []\n\n\nclass TestPackageContract(unittest.TestCase):\n    def test_ci_dependency_contract(self):\n        with (ROOT / "mise.toml").open("rb") as handle:\n            tasks = tomllib.load(handle)["tasks"]\n        self.assertEqual(tasks["ci"]["depends"], EXPECTED_CI_DEPENDS)\n        self.assertNotIn("run", tasks["ci"])\n\n    def test_tasks_have_explicit_contracts(self):\n        with (ROOT / "mise.toml").open("rb") as handle:\n            tasks = tomllib.load(handle)["tasks"]\n        for task in tasks.values():\n            self.assertTrue(task.get("description"))\n            self.assertIsInstance(task.get("depends"), list)\n            self.assertNotIn("mise run", str(task.get("run", "")))\n\n    def test_workflow_uses_one_mise_entry(self):\n        path = ROOT / ".github/workflows/ci.yml"\n        lines = path.read_text(encoding="utf-8").splitlines()\n        runs = [line.strip() for line in lines if line.strip().startswith("- run:")]\n        self.assertEqual(runs, ["- run: mise run ci"])\n\n\nif __name__ == "__main__":\n    unittest.main()\n'

if __name__ == '__main__':
    unittest.main()
