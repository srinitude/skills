"""Contract tests for the mise task graph and the CI workflow template."""
import pathlib
import tomllib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
REQUIRED_TASKS = [
    "ci", "test-ci", "test", "validate",
    "lint-writing", "lint-code", "evals", "doctor", "new",
]


def load_tasks(path):
    with open(path, "rb") as handle:
        data = tomllib.load(handle)
    return data.get("tasks", {})


class TestMiseTaskGraph(unittest.TestCase):
    def setUp(self):
        self.tasks = load_tasks(SKILL_DIR / "mise.toml")

    def test_required_tasks_exist(self):
        for name in REQUIRED_TASKS:
            self.assertIn(name, self.tasks, f"missing task: {name}")

    def test_ci_runs_ci_tests_before_code_tests(self):
        steps = self.tasks["ci"]["run"]
        self.assertIsInstance(steps, list)
        self.assertEqual(steps[0], "mise run test-ci")
        self.assertEqual(steps[1], "mise run test")

    def test_ci_covers_every_check_job(self):
        steps = " ".join(self.tasks["ci"]["run"])
        for job in ["validate", "lint-writing", "lint-code", "evals"]:
            self.assertIn(f"mise run {job}", steps)

    def test_each_check_job_has_one_default_path(self):
        for job in ["validate", "lint-writing", "lint-code", "evals"]:
            run = self.tasks[job]["run"]
            self.assertIsInstance(run, str, f"{job} must run one command")
            self.assertIn("python3 scripts/", run)


class TestWorkflowTemplate(unittest.TestCase):
    def setUp(self):
        self.path = SKILL_DIR / "assets" / "ci" / "ci.yml"
        self.text = self.path.read_text(encoding="utf-8")

    def test_template_exists_in_assets(self):
        self.assertTrue(self.path.is_file())

    def test_workflow_runs_only_mise_run_ci(self):
        run_lines = [
            line.strip() for line in self.text.splitlines()
            if line.strip().startswith("- run:")
        ]
        self.assertEqual(run_lines, ["- run: mise run ci"])

    def test_workflow_installs_mise(self):
        self.assertIn("jdx/mise-action", self.text)

    def test_workflow_triggers_on_push_and_pull_request(self):
        self.assertIn("push:", self.text)
        self.assertIn("pull_request:", self.text)


class TestGeneratedSkillTemplate(unittest.TestCase):
    def setUp(self):
        path = SKILL_DIR / "assets" / "mise-template.toml"
        self.tasks = load_tasks(path)

    def test_template_has_single_ci_entrypoint(self):
        steps = self.tasks["ci"]["run"]
        self.assertEqual(steps[0], "mise run test")
        joined = " ".join(steps)
        for job in ["validate", "lint-writing", "lint-code", "evals"]:
            self.assertIn(f"mise run {job}", joined)

    def test_template_jobs_match_factory_jobs(self):
        for job in ["test", "validate", "lint-writing", "lint-code", "evals"]:
            self.assertIn(job, self.tasks)


if __name__ == "__main__":
    unittest.main()
