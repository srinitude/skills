"""Contract tests that pin this skill's task graph and CI workflow.

Each test names the contract it pins:
  1. every task the pipeline needs exists in mise.toml
  2. the ci task invokes every check job
  3. every task carries a description a reader can act on
  4. the CI workflow runs the same single command as a local run
"""
import json
import pathlib
import re
import tomllib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
CHECK_JOBS = ["validate-dtcg", "artifact-contract", "validate", "audit-files", "validate-exploration", "lint-writing",
              "lint-code", "lint-placeholders", "evals", "improvement-policy"]
POLICY_JOBS = ["domain-research-policy", "use-case-policy", "mise-primitives-policy",
               "primitive-lifecycle-policy", "task-graph-policy", "decision-policy"]
REQUIRED_TASKS = ["ci", "acceptance", "test-ci", "test", "lineage", "refresh-lineage"] + CHECK_JOBS + POLICY_JOBS


def load_tasks(path):
    with open(path, "rb") as handle:
        return tomllib.load(handle).get("tasks", {})


class TestTaskGraph(unittest.TestCase):
    def setUp(self):
        self.tasks = load_tasks(SKILL_DIR / "mise.toml")

    def test_every_required_task_exists(self):
        for name in REQUIRED_TASKS:
            self.assertIn(name, self.tasks, f"missing task: {name}")

    def test_ci_uses_dependency_edges(self):
        task = self.tasks["ci"]
        self.assertEqual(task["depends"], ["acceptance", "lineage"])
        self.assertNotIn("run", task)
        self.assertEqual(set(self.tasks["acceptance"]["depends"]),
                         set(["test", "decision-policy"] + CHECK_JOBS))
        self.assertEqual(self.tasks["test"]["depends"], ["test-ci"])

    def test_every_task_has_a_description(self):
        for name, task in self.tasks.items():
            self.assertTrue(task.get("description"), f"{name} needs one")
            self.assertIsInstance(task.get("depends"), list, f"{name} needs explicit dependencies")

    def test_each_check_job_runs_one_command(self):
        for job in CHECK_JOBS:
            self.assertIn(job, self.tasks, f"missing task: {job}")
            run = self.tasks[job]["run"]
            self.assertIsInstance(run, str, f"{job} must run one command")
            self.assertIn("python3 scripts/", run)
        self.assertEqual(self.tasks["decision-policy"]["depends"], ["task-graph-policy"])

    def test_validation_keeps_every_check_behind_mise(self):
        validation = (SKILL_DIR / "references" / "validation.md").read_text(encoding="utf-8")
        for job in CHECK_JOBS:
            self.assertIn(f"mise run {job}", validation, f"validation is missing {job}")
        self.assertIn("Mise is unavailable", validation)
        self.assertIn("`BLOCKED`", validation)
        self.assertNotIn("python3 scripts/", validation)


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


class TestJudgmentContract(unittest.TestCase):
    def setUp(self):
        self.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.execution = (SKILL_DIR / "references" / "deterministic-execution.md").read_text(encoding="utf-8")
        self.vision = (SKILL_DIR / "references" / "vision-execution.md").read_text(encoding="utf-8")
        self.guides = "".join(
            (SKILL_DIR / "references" / name).read_text(encoding="utf-8")
            for name in ["execution-guide.md", "execution-intake.md", "execution-build.md", "execution-review.md"]
        )

    def test_vision_gate_delegates_every_judgment(self):
        contract = self.skill + self.execution + self.vision + self.guides
        self.assertIn("strong vision-capable model", contract)
        self.assertIn("delegate every judgment", contract)
        self.assertIn("do not generate tokens or proof", contract)

    def test_deterministic_contract_is_loaded(self):
        self.assertIn("references/deterministic-execution.md", self.skill)
        self.assertIn("## Fixed stage machine", self.execution)
        self.assertIn("completion matrix", self.execution)

class TestCommandTable(unittest.TestCase):
    def test_every_command_is_in_the_commands_table(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        commands = skill.split("## Commands\n", 1)[1].split("\n## ", 1)[0]
        self.assertIn("| Command", commands)
        self.assertIn("| Result", commands)
        for command in ["`help`", "`generate <inputs>`", "`validate <tokens>`", "`prove <tokens> <evidence> [sources]`"]:
            self.assertRegex(commands, rf"(?m)^\| {re.escape(command)}\s+\|")


class TestExecutionRouting(unittest.TestCase):
    def setUp(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.execution = skill.split("## Execution\n", 1)[1].split("\n## ", 1)[0]
        self.rows = []
        for line in self.execution.splitlines():
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) == 4 and re.fullmatch(r"\d{2}", cells[0]):
                self.rows.append((cells[0], cells[1], cells[2], cells[3]))

    def test_every_execution_step_routes_to_existing_support(self):
        self.assertEqual([number for number, *_ in self.rows], [f"{number:02d}" for number in range(1, 26)])
        for number, *cells in self.rows:
            paths = re.findall(r"(?:references|assets|scripts|examples|evals)/[A-Za-z0-9._/#-]+", " ".join(cells))
            self.assertTrue(paths, f"Execution step {number} needs a supporting file route")
            for path in paths:
                file_path = path.split("#", 1)[0]
                self.assertTrue((SKILL_DIR / file_path).is_file(), f"Execution step {number} route is missing: {file_path}")

    def test_execution_is_one_readable_row_per_step(self):
        header = next(line for line in self.execution.splitlines() if line.startswith("| #"))
        self.assertEqual([cell.strip() for cell in header.strip("|").split("|")], ["#", "Step", "Use", "Produces"])
        self.assertEqual(len(self.rows), 25)
        for number, step, use, output in self.rows:
            self.assertTrue(step and use and output, f"Execution step {number} has an empty summary cell")
            self.assertNotIn("PASS:", " ".join((step, use, output)))
            self.assertNotIn("BLOCKED:", " ".join((step, use, output)))

    def test_execution_uses_one_shared_step_contract(self):
        relative = "assets/execution-step-contract.json"
        self.assertIn(relative, self.execution)
        contract = json.loads((SKILL_DIR / relative).read_text(encoding="utf-8"))
        self.assertEqual(contract["step_count"], 25)
        self.assertEqual(contract["label_order"], ["Input", "Action", "Save", "Pass", "Blocked", "Feeds"])
        self.assertEqual(contract["statuses"], ["PENDING", "RUNNING", "PASS", "BLOCKED"])

    def test_execution_is_an_all_steps_pipeline(self):
        contract = json.loads((SKILL_DIR / "assets" / "execution-step-contract.json").read_text(encoding="utf-8"))
        self.assertIn("`generate` and `prove` run all 25 steps in order", self.execution)
        self.assertIn("No deliverable alone completes the skill", self.execution)
        self.assertEqual(contract["completion_rule"], "All 25 step records are PASS on current inputs and final bytes.")
        self.assertTrue(any(rule.startswith("Never stop after producing or validating one deliverable") for rule in contract["rules"]))

    def test_execution_has_a_closed_input_output_chain(self):
        relative = "assets/execution-io-map.json"
        self.assertIn(relative, self.execution)
        io_map = json.loads((SKILL_DIR / relative).read_text(encoding="utf-8"))
        steps = io_map["steps"]
        self.assertEqual([step["id"] for step in steps], [f"S{number:02d}" for number in range(1, 26)])
        self.assertIn("request.packet", steps[0]["consumes"])
        for current, following in zip(steps, steps[1:]):
            self.assertIn(current["primary_output"], current["produces"])
            self.assertIn(current["primary_output"], following["consumes"])
        self.assertEqual(steps[-1]["primary_output"], "completion.disposition")
        for step in steps:
            self.assertTrue(step["consumes"], f"{step['id']} needs named inputs")
            self.assertTrue(step["produces"], f"{step['id']} needs named outputs")

    def test_every_step_routes_to_its_numbered_reference(self):
        guides = {}
        for name in ["execution-intake.md", "execution-build.md", "execution-review.md"]:
            relative = f"references/{name}"
            guides[relative] = (SKILL_DIR / relative).read_text(encoding="utf-8")
            self.assertNotIn("<" + "br>", guides[relative], f"{relative} must use plain Markdown field lines")
        headings = [
            number
            for guide in guides.values()
            for number in re.findall(r"^## Step (\d{2}):", guide, flags=re.MULTILINE)
        ]
        self.assertEqual(headings, [f"{number:02d}" for number in range(1, 26)])
        for number, step, *_ in self.rows:
            match = re.search(r"\((references/execution-(?:intake|build|review)\.md#step-\d{2}-[^)]+)\)", step)
            self.assertIsNotNone(match, f"Execution step {number} needs one exact phase-guide link")
            relative, anchor = match.group(1).split("#", 1)
            heading_text = next(
                heading for heading in guides[relative].splitlines() if heading.startswith(f"## Step {number}:")
            )
            expected_anchor = re.sub(r"[^a-z0-9 -]", "", heading_text[3:].lower()).replace(" ", "-")
            self.assertEqual(anchor, expected_anchor)

        sections = [
            section
            for guide in guides.values()
            for section in re.split(r"(?=^## Step \d{2}:)", guide, flags=re.MULTILINE)[1:]
        ]
        for section in sections:
            for marker in ["**Input**", "**Action**", "**Save**", "**Pass**", "**Blocked**", "**Feeds**"]:
                self.assertIn(marker, section)

    def test_vision_gate_has_dedicated_procedure(self):
        guide = (SKILL_DIR / "references" / "execution-intake.md").read_text(encoding="utf-8")
        step_three = re.split(r"(?=^## Step 03:)", guide, flags=re.MULTILINE)[1].split("\n## Step 04:", 1)[0]
        self.assertIn("references/vision-execution.md", step_three)
        reference = SKILL_DIR / "references" / "vision-execution.md"
        self.assertTrue(reference.is_file())
        text = reference.read_text(encoding="utf-8")
        for marker in ["## Capability probe", "## Delegation packet", "## PASS", "## BLOCKED"]:
            self.assertIn(marker, text)


class TestCompletionContract(unittest.TestCase):
    def setUp(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.completion = skill.split("## Completion\n", 1)[1]

    def test_completion_has_inspectable_done_gates(self):
        header = next(line for line in self.completion.splitlines() if line.startswith("| Gate"))
        self.assertEqual([cell.strip() for cell in header.strip("|").split("|")], ["Gate", "Done only when", "Check with"])
        gates = [line for line in self.completion.splitlines() if line.startswith("|")][2:]
        self.assertGreaterEqual(len(gates), 8)
        joined = "\n".join(gates)
        joined_lower = joined.lower()
        for marker in ["tokens.json", "evidence.json", "proof.html", "run.json", "exit 0", "at least three", "five source-derived", "zero unresolved vetoes", "globally_unique", "mise run ci"]:
            self.assertIn(marker, joined_lower)
        for number, gate in enumerate(gates, start=1):
            self.assertIn("mise run ", gate, f"Completion gate {number} needs a Mise owner")
        self.assertNotIn("scripts/", joined)


if __name__ == "__main__":
    unittest.main()
