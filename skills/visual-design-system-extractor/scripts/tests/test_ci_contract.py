import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CiContractTests(unittest.TestCase):
    def setUp(self):
        self.config = tomllib.loads((ROOT / "mise.toml").read_text())

    def test_ci_task_runs_every_gate(self):
        self.assertEqual(
            self.config["tasks"]["ci"]["run"],
            [
                "mise run test",
                "mise run validate",
                "mise run lint-writing",
                "mise run lint-code",
                "mise run evals",
            ],
        )

    def test_test_task_supplies_the_yaml_parser(self):
        run = self.config["tasks"]["test"]["run"]
        self.assertIn("uv run --no-project --with 'PyYAML>=6,<7'", run)
        self.assertIn("unittest discover -s scripts/tests", run)

    def test_toolchain_is_pinned(self):
        tools = self.config["tools"]
        self.assertEqual(tools["python"], "3.13.14")
        self.assertEqual(tools["uv"], "0.11.29")

    def test_workflow_calls_only_the_ci_task(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("- run: mise run ci", workflow)
        self.assertNotIn("python3 scripts/", workflow)


if __name__ == "__main__":
    unittest.main()
