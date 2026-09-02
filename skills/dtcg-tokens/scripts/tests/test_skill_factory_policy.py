"""Contracts imported from Skill Factory for standalone DTCG use."""
import json
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


class ImprovementPolicyTests(unittest.TestCase):
    def test_machine_policy_has_protected_dimensions(self):
        path = ROOT / "assets" / "improvement-contract.json"
        policy = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(policy["cli_owner"], "mise")
        self.assertEqual(policy["acceptance"], "pareto_non_regression")
        self.assertEqual(policy["failure"], "restore_last_accepted_version")
        protected = set(policy["protected_dimensions"])
        self.assertTrue({"correctness", "wall_clock_time", "current_skill_contract"} <= protected)

    def test_policy_checker_passes_the_package(self):
        script = ROOT / "scripts" / "check_improvement_contract.py"
        result = subprocess.run(
            [sys.executable, str(script), str(ROOT)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("improvement contract: 0 problems", result.stdout)

    def test_step_contract_and_skill_route_the_policy(self):
        path = ROOT / "assets" / "execution-step-contract.json"
        policy = json.loads(path.read_text(encoding="utf-8"))["optional_skill_improvement"]
        self.assertEqual(policy["policy_owner"], "assets/improvement-contract.json")
        self.assertIn("elapsed_time", policy["protected_dimensions"])
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for marker in ["## Optional final step", "one named dimension",
                       "restore the last accepted version", "mise run ci"]:
            self.assertIn(marker, skill)

    def test_lineage_refresh_stays_behind_mise(self):
        import tomllib

        with open(ROOT / "mise.toml", "rb") as handle:
            tasks = tomllib.load(handle)["tasks"]
        self.assertEqual(
            tasks["refresh-lineage"]["run"],
            "python3 scripts/check_lineage.py . --write",
        )
        self.assertEqual(tasks["refresh-lineage"]["depends"], ["acceptance"])


class ProgressiveDisclosureTests(unittest.TestCase):
    def test_skill_routes_factory_policy_owners(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        paths = [
            "references/resource-and-experiment-design.md",
            "assets/improvement-contract.json",
            "references/use-case-specificity.md",
            "assets/use-case-contract.json",
        ]
        for path in paths:
            self.assertIn(path, skill)
            self.assertTrue((ROOT / path).is_file(), path)

    def test_recursive_contract_keeps_factory_invariants(self):
        path = ROOT / "references" / "generation-contract.md"
        contract = path.read_text(encoding="utf-8")
        for marker in [
            "## Simplicity and language",
            "## Deterministic and model-owned boundary",
            "Use dependency edges",
            "Pareto improvement",
        ]:
            self.assertIn(marker, contract)


if __name__ == "__main__":
    unittest.main()
