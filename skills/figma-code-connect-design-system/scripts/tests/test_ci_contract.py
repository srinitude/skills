"""Test the Figma skill task graph and CI path."""
import pathlib
import tomllib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
CHECK_JOBS = ["validate", "lint-writing", "lint-code",
              "lint-placeholders", "evals"]
REQUIRED_TASKS = ["ci", "test"] + CHECK_JOBS


def load_tasks(path):
    with open(path, "rb") as handle:
        return tomllib.load(handle).get("tasks", {})


class TestTaskGraph(unittest.TestCase):
    def setUp(self):
        self.tasks = load_tasks(SKILL_DIR / "mise.toml")

    def test_every_required_task_exists(self):
        for name in REQUIRED_TASKS:
            self.assertIn(name, self.tasks, f"missing task: {name}")

    def test_ci_reaches_every_check_job(self):
        pending, reached = ["ci"], set()
        while pending:
            name = pending.pop()
            if name in reached:
                continue
            reached.add(name)
            pending.extend(self.tasks[name].get("depends", []))
        for job in CHECK_JOBS:
            self.assertIn(job, reached)

    def test_every_task_has_a_description(self):
        for name, task in self.tasks.items():
            self.assertTrue(task.get("description"), f"{name} needs one")
            self.assertIsInstance(task.get("depends"), list)

    def test_no_task_runs_mise_inside_mise(self):
        for name, task in self.tasks.items():
            commands = task.get("run", [])
            commands = [commands] if isinstance(commands, str) else commands
            self.assertFalse(any("mise run" in item for item in commands), name)

    def test_each_check_job_runs_one_command(self):
        for job in CHECK_JOBS:
            run = self.tasks[job]["run"]
            self.assertIsInstance(run, str, f"{job} must run one command")
            self.assertIn("python3 scripts/", run)


class TestWorkflow(unittest.TestCase):
    def setUp(self):
        path = SKILL_DIR / ".github" / "workflows" / "ci.yml"
        self.assertTrue(path.is_file(), "missing .github/workflows/ci.yml")
        self.text = path.read_text(encoding="utf-8")

    def test_workflow_runs_only_the_single_entry_point(self):
        run_lines = [line.strip() for line in self.text.splitlines()
                     if line.strip().startswith("- run:")]
        self.assertEqual(run_lines, ["- run: mise run ci"])

    def test_workflow_triggers_on_push_and_pull_request(self):
        self.assertIn("push:", self.text)
        self.assertIn("pull_request:", self.text)


if __name__ == "__main__":
    unittest.main()
