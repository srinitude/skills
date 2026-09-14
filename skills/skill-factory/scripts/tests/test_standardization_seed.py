"""Preserve authored evals and reject unfinished standardization seeds."""
import json
import tempfile
import sys
import tomllib
import unittest
from pathlib import Path

from cli import SKILL_DIR
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from check_evals import check_cases, check_queries
from check_placeholders import line_problems
from standardization_seed import build_evals, build_triggers, seeds, base_mise, operations, task_records
from standardization_mise import normalize_mise
from standardization_runtime import UV_RUN, ISOLATED_UV
from check_task_graph import problems, route_problems

PROFILE = {"skill": "clock-anchor", "primary_term": "clock anchor",
           "outcome": "Read the current clock anchor with its UTC offset."}


def _TestStandardizationSeeds_test_missing_triggers_have_required_shape_but_cannot_pass_as_authored(self):
    with tempfile.TemporaryDirectory() as temp:
        queries = build_triggers(Path(temp), PROFILE)
    problems = []
    check_queries(queries, 4, problems)
    self.assertEqual(problems, [])
    self.assertTrue(all(line_problems(item["query"]) for item in queries))

def _TestStandardizationSeeds_test_missing_eval_details_remain_detectable_placeholders(self):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        data = build_evals(root, PROFILE)
        problems = []
        check_cases(data, root, 4, problems)
    self.assertEqual(problems, [])
    for item in data["evals"]:
        self.assertTrue(line_problems(item["prompt"]))
        self.assertTrue(line_problems(item["expected_output"]))
        self.assertTrue(all(line_problems(value) for value in item["assertions"]))

def _TestStandardizationSeeds_test_all_legacy_triggers_and_labels_survive_without_coercion(self):
    items = [{"prompt": f"Authored query {i}", "should_trigger": i % 2 == 0}
             for i in range(12)]
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "evals").mkdir()
        source = root / "evals/trigger-cases.json"
        source.write_text(json.dumps({"cases": items}))
        before = source.read_bytes()
        queries = build_triggers(root, PROFILE)
        self.assertEqual(source.read_bytes(), before)
    self.assertEqual(queries, [{"query": item["prompt"],
                                "should_trigger": item["should_trigger"]}
                               for item in items])

def _TestStandardizationSeeds_test_invalid_legacy_label_is_not_silently_turned_into_true(self):
    items = [{"prompt": "query", "should_trigger": flag}
             for flag in [True, False, "false", True]]
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "evals").mkdir()
        (root / "evals/trigger-cases.json").write_text(json.dumps({"cases": items}))
        queries = build_triggers(root, PROFILE)
    self.assertEqual(queries[2]["should_trigger"], "false")
    problems = []
    check_queries(queries, 4, problems)
    self.assertTrue(any("true or false" in item for item in problems))

def _TestStandardizationSeeds_test_all_legacy_evals_keep_their_authored_meaning(self):
    items = [{"prompt": f"Read input {i}", "expected_output": f"Output {i}",
              "assertions": [f"Exact predicate {i}"]} for i in range(7)]
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "evals").mkdir()
        source = root / "evals/cases.json"
        source.write_text(json.dumps({"cases": items}))
        before = source.read_bytes()
        actual = build_evals(root, PROFILE)["evals"]
        self.assertEqual(source.read_bytes(), before)
    self.assertEqual(actual, [dict(item, id=i) for i, item in enumerate(items, 1)])

def _TestStandardizationSeeds_test_existing_eval_owners_do_not_read_unused_broken_legacy_files(self):
    files = {"evals/evals.json": b"authored eval bytes",
             "evals/trigger-queries.json": b"authored query bytes"}
    before = dict(files)
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "evals").mkdir()
        for name in ["cases.json", "trigger-cases.json"]:
            (root / "evals" / name).write_text("invalid unused legacy JSON")
        seeds(root, files, PROFILE, SKILL_DIR)
    for name, value in before.items():
        self.assertEqual(files[name], value)


def _TestStandardizationSeeds_test_generated_markdown_tasks_have_one_public_path(self):
    tasks = tomllib.loads(normalize_mise(base_mise(PROFILE)))["tasks"]
    profile = {**PROFILE, "main_task": "validate"}
    graph = {"ci_task": "ci", "public_operations": operations(profile, tasks),
             "tasks": task_records(profile, tasks)}
    contract = {"domain_terms": ["clock anchor"], "task_graph": graph}
    self.assertEqual(problems(tasks, contract), [])
    self.assertIn("markdown:accept", [row["task"] for row in graph["public_operations"]])
    graph["public_operations"] = [row for row in graph["public_operations"] if row["task"] != "markdown:accept"]
    self.assertTrue(any("no public operation reaches markdown:" in row for row in problems(tasks, contract)))


def _TestStandardizationSeeds_test_scaffold_template_accounts_for_every_task(self):
    tasks = tomllib.loads((SKILL_DIR / "assets/mise-template.toml").read_text())["tasks"]
    graph = json.loads((SKILL_DIR / "assets/use-case-contract-template.json").read_text())["task_graph"]
    self.assertEqual(set(tasks), set(graph["tasks"]))
    entries = [graph["ci_task"], *[row["task"] for row in graph["public_operations"]]]
    self.assertEqual(route_problems(tasks, entries), [])


def test_generated_test_runtime_preserves_target_selection(self):
    suffix = "python -m unittest discover -s domain_tests -p 'check_*.py' --buffer"
    for prefix in [UV_RUN, ISOLATED_UV]:
        source = '[tasks.test]\nrun = ' + json.dumps(prefix + suffix)
        source += '\nrun_windows = ' + json.dumps(prefix + suffix) + '\n'
        output = normalize_mise(source)
        task = tomllib.loads(output)['tasks']['test']
        for field in ['run', 'run_windows']:
            self.assertTrue(task[field].endswith(suffix))
            self.assertIn('--with markdown-it-py==4.0.0 ', task[field])
            self.assertIn('--with textstat==0.7.8 ', task[field])
            self.assertIn('--no-project --isolated --no-python-downloads ', task[field])
        self.assertEqual(task['env']['UV_PYTHON'], '{{tools.python.path}}')
        self.assertEqual(normalize_mise(output), output)
    custom = 'uv run --with domain-package==1.0 python -m unittest discover -s domain_tests'
    output = normalize_mise('[tasks.test]\nrun = ' + json.dumps(custom) + '\n')
    self.assertEqual(tomllib.loads(output)['tasks']['test']['run'], custom)
    isolated = ISOLATED_UV + 'scripts/check_target.py "domain path"'
    output = normalize_mise('[tasks.anchor]\nrun = ' + json.dumps(isolated) + '\n')
    self.assertEqual(tomllib.loads(output)['tasks']['anchor']['run'], isolated)


class TestStandardizationSeeds(unittest.TestCase):
    test_generated_test_runtime_preserves_target_selection = test_generated_test_runtime_preserves_target_selection
    test_scaffold_template_accounts_for_every_task = _TestStandardizationSeeds_test_scaffold_template_accounts_for_every_task
    test_generated_markdown_tasks_have_one_public_path = _TestStandardizationSeeds_test_generated_markdown_tasks_have_one_public_path
    test_missing_triggers_have_required_shape_but_cannot_pass_as_authored = _TestStandardizationSeeds_test_missing_triggers_have_required_shape_but_cannot_pass_as_authored
    test_missing_eval_details_remain_detectable_placeholders = _TestStandardizationSeeds_test_missing_eval_details_remain_detectable_placeholders
    test_all_legacy_triggers_and_labels_survive_without_coercion = _TestStandardizationSeeds_test_all_legacy_triggers_and_labels_survive_without_coercion
    test_invalid_legacy_label_is_not_silently_turned_into_true = _TestStandardizationSeeds_test_invalid_legacy_label_is_not_silently_turned_into_true
    test_all_legacy_evals_keep_their_authored_meaning = _TestStandardizationSeeds_test_all_legacy_evals_keep_their_authored_meaning
    test_existing_eval_owners_do_not_read_unused_broken_legacy_files = _TestStandardizationSeeds_test_existing_eval_owners_do_not_read_unused_broken_legacy_files


if __name__ == "__main__":
    unittest.main()
