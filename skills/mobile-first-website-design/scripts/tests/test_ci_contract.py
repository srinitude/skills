"""Pin the skill-local task graph and one-entry workflow."""
import pathlib
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


class TestCiContract(unittest.TestCase):
    def test_task_graph(self):
        with open(ROOT / "mise.toml", "rb") as handle:
            tasks = tomllib.load(handle)["tasks"]
        self.assertEqual(tasks["ci"]["run"], [
            "mise run test", "mise run validate", "mise run evals"
        ])
        for name in ("test", "validate", "evals", "ci"):
            self.assertTrue(tasks[name]["description"])

    def test_workflow_has_one_entry(self):
        text = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        runs = [line.strip() for line in text.splitlines() if line.strip().startswith("- run:")]
        self.assertEqual(runs, ["- run: mise run ci"])


if __name__ == "__main__":
    unittest.main()
