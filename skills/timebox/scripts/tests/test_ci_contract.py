"""Pin the timebox task graph and one-entry workflow."""
import pathlib
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXPECTED_CI_DEPENDS = ["test", "validate", "lint-writing", "lint-code", "evals", "decision-policy"]


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
