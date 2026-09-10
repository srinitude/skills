"""Tests for factory-owned in-place registry standardization."""
import json
import sys
import tomllib
import tempfile
import unittest
from pathlib import Path

from standardization_test_support import reviewed_standardize

from standardization_fixtures import profile, write_target
from cli import SCRIPTS
sys.path.insert(0, str(SCRIPTS))
from check_task_graph import path_counts


class TestRegistryStandardization(unittest.TestCase):
    def invoke(self, root, profile_path, apply=False):
        args = [root, "--profile", profile_path]
        return reviewed_standardize(*args, *(["--scope", "user", "--apply"] if apply else []))

    def test_plan_makes_no_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            source = (root / "SKILL.md").read_bytes()
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(profile()), encoding="utf-8")
            result = self.invoke(root, profile_path)
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(report["writes"], 0)
            self.assertEqual((root / "SKILL.md").read_bytes(), source)

    def test_apply_adds_domain_owners_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(profile()), encoding="utf-8")
            first = self.invoke(root, profile_path, apply=True)
            second = self.invoke(root, profile_path, apply=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(json.loads(second.stdout)["changed"], [])
            self.assert_package_files(root)
            self.assert_package_graph(root)

    def assert_package_files(self, root):
            self.assertTrue((root / "assets/use-case-contract.json").is_file())
            self.assertTrue((root / "assets/primitive-lifecycle.json").is_file())
            skill = (root / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("mise run anchor", skill)
            self.assertNotIn("scripts/anchor.py", skill)
            owner = "[context reader](scripts/agentic_context.py)"
            self.assertIn(owner, skill)
            self.assertNotIn("scripts/", skill.replace(owner, "context reader"))
            reference = (root / "references/contract.md").read_text()
            self.assertIn("mise run anchor", reference)
            self.assertIn("mise run report-clock", reference)
            self.assertIn("`mise run inspect-anchor`", reference)
            self.assertNotIn("[the receipt inspector]", reference)
            self.assertIn("mise run ", reference)
            self.assertNotIn("Use it through", reference)
            self.assertNotIn("scripts/", reference)
            domain_check = (root / "scripts/domain_check.py").read_text()
            self.assertEqual(domain_check, "FACTORY_ASSERTION\n")

    def assert_package_graph(self, root):
            mise = (root / "mise.toml").read_text(encoding="utf-8")
            counts = path_counts(tomllib.loads(mise)["tasks"], "ci")
            for task in ["anchor", "decision-policy", "test", "validate",
                         "lint-writing", "lint-code", "lint-placeholders", "evals"]:
                self.assertEqual(counts.get(task), 1, task)
            self.assertIn("[tasks.inspect-anchor]", mise)
            self.assertIn("[tasks.report-clock]", mise)
            self.assertIn("uv run python scripts/inspect.py --format json", mise)
            self.assertNotIn("mise run anchor", mise)
            validator = (root / "scripts/validate_skill.py").read_text()
            self.assertNotIn('elif body and f"{name}/"', validator)
            self.assertTrue((root / "scripts/tests/test_package_contract.py").is_file())
            skill = (root / "SKILL.md").read_text()
            self.assertIn("assets/use-case-contract.json", skill)
            self.assertIn("evals/evals.json", skill)

    def test_apply_refreshes_the_recursive_generation_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            contract = root / "references/generation-contract.md"
            contract.write_text("# Stale contract\n", encoding="utf-8")
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(profile()), encoding="utf-8")
            result = self.invoke(root, profile_path, apply=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(contract.read_bytes(), (Path(__file__).resolve().parents[2] / "references/generation-contract.md").read_bytes())

    def test_apply_refreshes_the_placeholder_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            checker = root / "scripts/check_placeholders.py"
            checker.write_text("print('stale')\n", encoding="utf-8")
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(profile()), encoding="utf-8")
            result = self.invoke(root, profile_path, apply=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("documented_example", checker.read_text())

    def test_apply_updates_graph_and_preserves_source_inventory_assertion(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            tests = root / "scripts/tests"
            tests.mkdir()
            (tests / "test_ci_contract.py").write_text(
                'steps = self.tasks["ci"]["run"]\n'
                'self.assertIn(f"mise run {job}", " ".join(steps))\n')
            (tests / "test_source_mapping.py").write_text(
                "self.assertEqual(files, EXPECTED_FILES)\n")
            (tests / "test_scripts.py").write_text(
                "import pathlib\n"
                "SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]\n"
                '        scripts = sorted((SKILL_DIR / "scripts").glob("*.py"))\n'
                '        self.assertTrue(scripts, "scripts/ holds no python files")\n')
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(profile()), encoding="utf-8")
            result = self.invoke(root, profile_path, apply=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            ci_test = (tests / "test_ci_contract.py").read_text()
            source_test = (tests / "test_source_mapping.py").read_text()
            script_test = (tests / "test_scripts.py").read_text()
            self.assertIn('tasks["ci"]["depends"]', ci_test)
            self.assertNotIn('tasks["ci"]["run"]', ci_test)
            self.assertNotIn('f"mise run {job}"', ci_test)
            self.assertEqual(source_test, "self.assertEqual(files, EXPECTED_FILES)\n")
            self.assertIn("CLI_SCRIPTS", script_test)
            self.assertNotIn('glob("*.py")', script_test)

    def test_refuses_profile_or_target_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            data = profile()
            data["skill"] = "another-skill"
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(data), encoding="utf-8")
            result = self.invoke(root, profile_path, apply=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "assets/use-case-contract.json").exists())


if __name__ == "__main__":
    unittest.main()
