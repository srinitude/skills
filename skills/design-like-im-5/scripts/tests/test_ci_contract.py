"""Contract tests that pin this skill's task graph and CI workflow.

Each test names the contract it pins:
  1. every task the pipeline needs exists in mise.toml
  2. the ci task invokes every check job
  3. every task carries a description a reader can act on
  4. the CI workflow runs the same single command as a local run
"""
import pathlib
import re
import subprocess
import tomllib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
LEAF_CHECKS = {
    "task-graph", "test", "validate", "reading", "lineage",
    "source-lineage", "ownership", "directories", "context-routing",
    "section-support", "lint-writing", "lint-code", "lint-placeholders",
    "evals", "examples", "file-manifest", "lineage-build", "proof-ladder",
}
FACTORY_CHECKS = {
    "domain-research-policy", "use-case-policy", "mise-primitives-policy",
    "primitive-lifecycle-policy", "task-graph-policy", "decision-policy",
    "improvement-policy", "factory-policy",
}
GROUPS = {"structure", "proof", "quality", "ci", "complete"}
RUNTIME = {
    "skill-info", "run-start", "run-packet", "run-record", "run-check",
    "run-scaffold", "review-checklist", "human-sweep", "lineage-file",
    "run-select-rules",
}
WRITERS = {
    "examples-write", "file-manifest-write", "source-manifest-write",
    "source-lineage-write", "generate",
}
REQUIRED_TASKS = LEAF_CHECKS | FACTORY_CHECKS | GROUPS | RUNTIME | WRITERS


def load_tasks(path):
    with open(path, "rb") as handle:
        return tomllib.load(handle).get("tasks", {})


def load_config(path):
    with open(path, "rb") as handle:
        return tomllib.load(handle)


def dependencies(tasks, name):
    found, stack = set(), list(tasks[name].get("depends", []))
    while stack:
        item = stack.pop()
        if item not in found:
            found.add(item)
            stack.extend(tasks[item].get("depends", []))
    return found


class TestTaskGraph(unittest.TestCase):
    def setUp(self):
        self.config = load_config(SKILL_DIR / "mise.toml")
        self.tasks = self.config.get("tasks", {})

    def test_package_gate_uses_the_measured_job_count(self):
        self.assertEqual(self.config.get("settings", {}).get("jobs"), 8)

    def test_every_required_task_exists(self):
        for name in REQUIRED_TASKS:
            self.assertIn(name, self.tasks, f"missing task: {name}")

    def test_complete_transitively_requires_every_check(self):
        reached = dependencies(self.tasks, "complete")
        expected = LEAF_CHECKS | FACTORY_CHECKS | {
            "structure", "proof", "quality", "ci",
        }
        self.assertEqual(expected, reached)

    def test_every_runtime_task_requires_its_static_contracts(self):
        required = {"task-graph", "context-routing", "section-support"}
        for name in {"run-start", "run-packet", "run-record", "run-check",
                     "run-select-rules"}:
            self.assertTrue(required <= dependencies(self.tasks, name), name)

    def test_lineage_file_accepts_the_manifest_at_run_time(self):
        command = self.tasks["lineage-file"]["run"]
        self.assertEqual(command, "python3 scripts/check_lineage.py")

    def test_dependency_graph_has_no_cycle(self):
        for name in self.tasks:
            self.assertNotIn(name, dependencies(self.tasks, name), name)

    def test_required_checks_cannot_be_cached_or_skipped(self):
        for name in LEAF_CHECKS:
            task = self.tasks[name]
            self.assertNotIn("sources", task, name)
            self.assertNotIn("outputs", task, name)
            self.assertNotIn("cache", task, name)

    def test_generated_writers_stay_in_one_ordered_chain(self):
        self.assertEqual(self.tasks["file-manifest-write"]["depends"],
                         ["examples-write"])
        self.assertEqual(self.tasks["source-lineage-write"]["depends"],
                         ["source-manifest-write"])
        self.assertEqual(self.tasks["source-manifest-write"]["depends"],
                         ["file-manifest-write"])
        self.assertEqual(self.tasks["generate"]["depends"],
                         ["source-lineage-write"])

    def test_mise_accepts_the_whole_task_graph(self):
        result = subprocess.run(
            ["mise", "tasks", "validate", "--errors-only"],
            cwd=SKILL_DIR, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_every_task_has_a_description(self):
        for name, task in self.tasks.items():
            self.assertTrue(task.get("description"), f"{name} needs one")

    def test_each_leaf_check_runs_one_command(self):
        for job in LEAF_CHECKS:
            task = self.tasks.get(job)
            self.assertIsNotNone(task, f"missing task: {job}")
            run = task["run"]
            self.assertIsInstance(run, str, f"{job} must run one command")

    def test_every_public_script_has_a_mise_task(self):
        commands = "\n".join(
            value for task in self.tasks.values()
            for value in ([task.get("run")] if isinstance(task.get("run"), str)
                          else task.get("run", [])))
        missing = [path.name for path in (SKILL_DIR / "scripts").glob("*.py")
                   if f"scripts/{path.name}" not in commands]
        self.assertEqual(missing, [])

    def test_skill_body_names_only_mise_executable_interfaces(self):
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("scripts/", text)
        self.assertNotIn("python3 ", text)
        named = set(re.findall(r"mise run ([a-z0-9-]+)", text))
        self.assertTrue(named, "SKILL.md needs named Mise tasks")
        self.assertEqual(named - set(self.tasks), set())
        self.assertIn("complete", named)

    def test_skill_body_forbids_pass_without_the_complete_task(self):
        text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        rule = "Return `PASS` only after `mise run complete` exits with code `0`."
        self.assertIn(rule, text)


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
