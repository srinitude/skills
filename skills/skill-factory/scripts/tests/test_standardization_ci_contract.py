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


class TestGeneratedCIContract(unittest.TestCase):
    test_custom_ci_contract_passes_and_command_drift_fails = _TestGeneratedCIContract_test_custom_ci_contract_passes_and_command_drift_fails
    test_exact_generated_contract_is_refreshed_for_changed_commands = _TestGeneratedCIContract_test_exact_generated_contract_is_refreshed_for_changed_commands
    test_customized_contract_is_preserved_for_explicit_review = _TestGeneratedCIContract_test_customized_contract_is_preserved_for_explicit_review
    test_custom_legacy_run_assertion_is_not_replaced = _TestGeneratedCIContract_test_custom_legacy_run_assertion_is_not_replaced
    test_exact_legacy_generated_contract_is_migrated = _TestGeneratedCIContract_test_exact_legacy_generated_contract_is_migrated


# Exact previous generated contract retained as compatibility evidence.
LEGACY = b'"""Pin the clock-anchor task graph and one-entry workflow."""\nimport pathlib\nimport tomllib\nimport unittest\n\nROOT = pathlib.Path(__file__).resolve().parents[2]\nEXPECTED_CI_DEPENDS = []\n\n\nclass TestPackageContract(unittest.TestCase):\n    def test_ci_dependency_contract(self):\n        with (ROOT / "mise.toml").open("rb") as handle:\n            tasks = tomllib.load(handle)["tasks"]\n        self.assertEqual(tasks["ci"]["depends"], EXPECTED_CI_DEPENDS)\n        self.assertNotIn("run", tasks["ci"])\n\n    def test_tasks_have_explicit_contracts(self):\n        with (ROOT / "mise.toml").open("rb") as handle:\n            tasks = tomllib.load(handle)["tasks"]\n        for task in tasks.values():\n            self.assertTrue(task.get("description"))\n            self.assertIsInstance(task.get("depends"), list)\n            self.assertNotIn("mise run", str(task.get("run", "")))\n\n    def test_workflow_uses_one_mise_entry(self):\n        path = ROOT / ".github/workflows/ci.yml"\n        lines = path.read_text(encoding="utf-8").splitlines()\n        runs = [line.strip() for line in lines if line.strip().startswith("- run:")]\n        self.assertEqual(runs, ["- run: mise run ci"])\n\n\nif __name__ == "__main__":\n    unittest.main()\n'

if __name__ == '__main__':
    unittest.main()
