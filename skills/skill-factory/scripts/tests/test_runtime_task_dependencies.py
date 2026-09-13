"""Keep native checker consumers behind preparation without duplicate paths."""
import sys
import tomllib
import unittest

from cli import SKILL_DIR, SCRIPTS

sys.path.insert(0, str(SCRIPTS))
from check_task_graph import dependencies, find_cycle, path_counts
from standardization_mise import normalize_mise, runtime_dependencies
from standardization_seed import base_mise


def assert_task_order(case, tasks):
    seen = set()
    for task, fields in tasks.items():
        case.assertTrue(set(dependencies(fields)) <= seen, task)
        seen.add(task)


def _TestRuntimeDependencies_assert_ready_graph(self, tasks):
    self.assertIn("setup-graph-renderer", tasks["test"]["depends"])
    self.assertEqual(tasks["setup-graph-renderer"]["depends"], ["lint-code"])
    self.assertEqual(tasks["render-file-graph"]["depends"], ["setup-graph-renderer"])
    self.assertIn("check-runtime", tasks["lint-code"]["depends"])
    self.assertEqual(tasks["check-runtime"]["depends"], ["setup-runtime"])
    self.assertIsNone(find_cycle(tasks))
    for entry in ["test", "ci"]:
        counts = path_counts(tasks, entry)
        for name in ["test", "setup-graph-renderer", "lint-code", "check-runtime", "setup-runtime"]:
            self.assertEqual(counts[name], 1, (entry, name, counts))
        self.assertTrue(all(count <= 1 for count in counts.values()))

def _TestRuntimeDependencies_test_public_variant_and_target_validation_prepare_the_native_checker(self):
    tasks = tomllib.loads((SKILL_DIR / "mise.toml").read_text())["tasks"]
    for entry in ["variant", "validate-target"]:
        with self.subTest(entry=entry):
            counts = path_counts(tasks, entry)
            required = ["doctor", "check-runtime", "setup-runtime"]
            self.assertEqual({name: counts.get(name, 0) for name in required}, dict.fromkeys(required, 1), entry)
            self.assertTrue(all(count <= 1 for count in counts.values()))

def _TestRuntimeDependencies_test_existing_ci_reaches_validation_once_on_direct_and_indirect_routes(self):
    for dependency in ['anchor', 'verify-anchor']:
        with self.subTest(dependency=dependency):
            source = ('[tasks.anchor]\ndescription = "Read the clock"\ndepends = []\nrun = "true"\n'
                      '[tasks.verify-anchor]\ndescription = "Check the clock package"\ndepends = ["validate"]\n'
                      '[tasks.ci]\ndescription = "Check the clock"\ndepends = ["' + dependency + '"]\n')
            output = normalize_mise(source)
            tasks = tomllib.loads(output)['tasks']
            self.assertIsNone(find_cycle(tasks))
            self.assertEqual(path_counts(tasks, 'ci')['validate'], 1)
            self.assertEqual(tasks['anchor']['depends'], [])
            self.assertEqual(tasks['verify-anchor']['depends'], ['validate'])
            self.assertLess(list(tasks).index('validate'), list(tasks).index('ci'))
            self.assertEqual(normalize_mise(output), output)

def _TestRuntimeDependencies_test_partial_legacy_ci_reaches_every_required_standard_check(self):
    source = ('[tasks.anchor]\ndescription = "Read the clock"\ndepends = []\nrun = "true"\n'
              '[tasks.ci]\ndescription = "Check the clock"\nrun = "mise run anchor"\n')
    checks = tomllib.loads(base_mise({'primary_term': 'clock'}))['tasks']['ci']['depends']
    output = normalize_mise(source)
    tasks = tomllib.loads(output)['tasks']
    self.assertTrue(set(checks) <= set(tasks), set(checks) - set(tasks))
    counts = path_counts(tasks, 'ci')
    for check in [*checks, 'anchor', 'check-runtime', 'setup-runtime']:
        self.assertEqual(counts[check], 1, check)
    self.assertIsNone(find_cycle(tasks))
    self.assertEqual(tasks['anchor'], tomllib.loads(source)['tasks']['anchor'])
    self.assertEqual(normalize_mise(output), output)

def _TestRuntimeDependencies_test_absent_lint_owner_does_not_erase_the_declared_runtime(self):
    names = {"test", "check-runtime", "setup-runtime"}
    self.assertEqual(runtime_dependencies("test", ["check-runtime"], names), ["check-runtime"])

def _TestRuntimeDependencies_test_conflicting_native_task_is_rejected_without_rewriting_input(self):
    source = normalize_mise(base_mise({"primary_term": "source-ledger"}))
    invalid = source.replace("npm ci --include=dev --ignore-scripts", "npm run custom")
    with self.assertRaisesRegex(ValueError, "native runtime task"):
        normalize_mise(invalid)

def _TestRuntimeDependencies_test_shared_python_helpers_have_an_explicit_mise_owned_environment(self):
    for name in ["mise.toml", "assets/mise-template.toml"]:
        config = tomllib.loads((SKILL_DIR / name).read_text())
        self.assertEqual(config["tools"]["python"], "3.11.15")
        self.assertEqual(config["tools"]["uv"], "0.11.29")
        commands = [(task.get(field, ""), task) for task in config["tasks"].values()
                    for field in ["run", "run_windows"]]
        helpers = ((command, task) for command, task in commands
                   if isinstance(command, str) and command.startswith("uv run "))
        for command, task in helpers:
            self.assertIn("--no-project --isolated --no-python-downloads", command)
            self.assertEqual(task["env"]["UV_PYTHON"], "{{tools.python.path}}")

def _TestRuntimeDependencies_test_standardization_isolates_shared_helpers_and_preserves_domain_owners(self):
    source = base_mise({"primary_term": "source-ledger"})
    source += '\n[tasks.domain]\nrun = "uv run --project custom python tool.py"\nenv = { UV_PYTHON = "owned" }\ndepends = []\n'
    result = normalize_mise(source)
    config = tomllib.loads(result)
    self.assertEqual(config["tools"]["python"], tomllib.loads(source)["tools"]["python"])
    self.assertEqual(config["tools"]["uv"], "0.11.29")
    self.assertEqual(config["tasks"]["domain"], tomllib.loads(source)["tasks"]["domain"])
    task = config["tasks"]["validate"]
    self.assertIn("--no-project --isolated --no-python-downloads", task["run"])
    self.assertEqual(task["env"], {"UV_PYTHON": "{{tools.python.path}}"})
    self.assertEqual(normalize_mise(result), result)

def _TestRuntimeDependencies_test_custom_helper_environment_requires_reconciliation_without_mutation(self):
    source = base_mise({"primary_term": "source-ledger"})
    source = source.replace('[tasks.validate]', '[tasks.validate]\nenv = { UV_PYTHON = "custom" }')
    with self.assertRaisesRegex(ValueError, "Python helper environment"):
        normalize_mise(source)

def _TestRuntimeDependencies_test_uv_version_customization_requires_reconciliation(self):
    source = base_mise({"primary_term": "source-ledger"})
    with self.assertRaisesRegex(ValueError, "runtime uv version"):
        normalize_mise(source.replace('uv = "0.11.29"', 'uv = "custom"'))
    legacy = source.replace('uv = "0.11.29"', 'uv = "latest"')
    self.assertEqual(tomllib.loads(normalize_mise(legacy))["tools"]["uv"], "0.11.29")

def _TestRuntimeDependencies_test_catalog_migration_preserves_options_and_rejects_customization(self):
    source = base_mise({"primary_term": "source-ledger"})
    output = normalize_mise(source)
    task = tomllib.loads(output)['tasks']['mise-primitives-update']
    self.assertEqual(task['usage'], 'flag "--review <path>" required=#true')
    self.assertIn('--review "${usage_review?}"', task['run'])
    self.assertIn('mise-primitives-plan', tomllib.loads(output)['tasks'])
    self.assertEqual(normalize_mise(output), output)
    altered = output.replace('scripts/sync_mise_primitives.py . --review', 'scripts/custom.py . --review')
    with self.assertRaisesRegex(ValueError, 'catalog command'):
        normalize_mise(altered)
    altered = output.replace('required=#true', 'required=#false')
    with self.assertRaisesRegex(ValueError, 'catalog review usage'):
        normalize_mise(altered)

def _TestRuntimeDependencies_test_catalog_migration_preserves_inline_comments(self):
    source = base_mise({'primary_term': 'source-ledger'})
    source += '\n[tasks.mise-primitives-update]\nrun = "python3 scripts/sync_mise_primitives.py ." # keep catalog context\n'
    source += 'run_windows = "python scripts/sync_mise_primitives.py ." # keep Windows context\ndepends = ["mise-latest"]\n'
    output = normalize_mise(source)
    for comment in ['# keep catalog context', '# keep Windows context']:
        self.assertEqual(output.count(comment), 1)
    self.assertEqual(normalize_mise(output), output)

def _TestRuntimeDependencies_test_task_definitions_follow_their_reading_dependencies(self):
    for name in ["mise.toml", "assets/mise-template.toml"]:
        with self.subTest(name=name):
            tasks = tomllib.loads((SKILL_DIR / name).read_text())["tasks"]
            assert_task_order(self, tasks)

def _TestRuntimeDependencies_test_factory_and_generated_test_routes_prepare_the_runtime(self):
    for name in ["mise.toml", "assets/mise-template.toml"]:
        with self.subTest(name=name):
            self.assert_ready_graph(tomllib.loads((SKILL_DIR / name).read_text())["tasks"])

def _TestRuntimeDependencies_test_standardization_preserves_all_checks_on_one_runtime_path(self):
    source = base_mise({"primary_term": "source-ledger"})
    normalized = normalize_mise(source)
    self.assert_ready_graph(tomllib.loads(normalized)["tasks"])
    self.assertEqual(normalize_mise(normalized), normalized)


class TestRuntimeDependencies(unittest.TestCase):
    assert_ready_graph = _TestRuntimeDependencies_assert_ready_graph
    test_factory_and_generated_test_routes_prepare_the_runtime = _TestRuntimeDependencies_test_factory_and_generated_test_routes_prepare_the_runtime
    test_public_variant_and_target_validation_prepare_the_native_checker = _TestRuntimeDependencies_test_public_variant_and_target_validation_prepare_the_native_checker
    test_standardization_preserves_all_checks_on_one_runtime_path = _TestRuntimeDependencies_test_standardization_preserves_all_checks_on_one_runtime_path
    test_existing_ci_reaches_validation_once_on_direct_and_indirect_routes = _TestRuntimeDependencies_test_existing_ci_reaches_validation_once_on_direct_and_indirect_routes
    test_partial_legacy_ci_reaches_every_required_standard_check = _TestRuntimeDependencies_test_partial_legacy_ci_reaches_every_required_standard_check
    test_absent_lint_owner_does_not_erase_the_declared_runtime = _TestRuntimeDependencies_test_absent_lint_owner_does_not_erase_the_declared_runtime
    test_conflicting_native_task_is_rejected_without_rewriting_input = _TestRuntimeDependencies_test_conflicting_native_task_is_rejected_without_rewriting_input
    test_shared_python_helpers_have_an_explicit_mise_owned_environment = _TestRuntimeDependencies_test_shared_python_helpers_have_an_explicit_mise_owned_environment
    test_standardization_isolates_shared_helpers_and_preserves_domain_owners = _TestRuntimeDependencies_test_standardization_isolates_shared_helpers_and_preserves_domain_owners
    test_custom_helper_environment_requires_reconciliation_without_mutation = _TestRuntimeDependencies_test_custom_helper_environment_requires_reconciliation_without_mutation
    test_uv_version_customization_requires_reconciliation = _TestRuntimeDependencies_test_uv_version_customization_requires_reconciliation
    test_catalog_migration_preserves_options_and_rejects_customization = _TestRuntimeDependencies_test_catalog_migration_preserves_options_and_rejects_customization
    test_catalog_migration_preserves_inline_comments = _TestRuntimeDependencies_test_catalog_migration_preserves_inline_comments
    test_task_definitions_follow_their_reading_dependencies = _TestRuntimeDependencies_test_task_definitions_follow_their_reading_dependencies


if __name__ == "__main__":
    unittest.main()
