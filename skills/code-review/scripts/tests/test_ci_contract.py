import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CiContractTests(unittest.TestCase):
    def test_ci_task_runs_every_gate(self):
        tasks = tomllib.loads((ROOT / "mise.toml").read_text())["tasks"]
        self.assertEqual(
            tasks["test"]["run"],
            "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s scripts/tests -p 'test_*.py' -v",
        )
        self.assertEqual(
            tasks["ci"]["run"],
            [
                "mise run test",
                "mise run validate",
                "mise run lint-writing",
                "mise run lint-code",
                "mise run evals",
            ],
        )

    def test_workflow_calls_only_the_ci_task(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("- run: mise run ci", workflow)
        self.assertNotIn("python3 scripts/", workflow)


if __name__ == "__main__":
    unittest.main()
