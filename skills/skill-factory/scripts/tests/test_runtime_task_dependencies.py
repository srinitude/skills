"""Keep native checker consumers behind preparation without duplicate paths."""
import sys
import tomllib
import unittest

from cli import SKILL_DIR, SCRIPTS

sys.path.insert(0, str(SCRIPTS))
from check_task_graph import find_cycle, path_counts
from standardization_mise import normalize_mise, runtime_dependencies
from standardization_seed import base_mise


class TestRuntimeDependencies(unittest.TestCase):
    def assert_ready_graph(self, tasks):
        self.assertIn("lint-code", tasks["test"]["depends"])
        self.assertIn("check-runtime", tasks["lint-code"]["depends"])
        self.assertEqual(tasks["check-runtime"]["depends"], ["setup-runtime"])
        self.assertIsNone(find_cycle(tasks))
        for entry in ["test", "ci"]:
            counts = path_counts(tasks, entry)
            for name in ["test", "lint-code", "check-runtime", "setup-runtime"]:
                self.assertEqual(counts[name], 1, (entry, name, counts))
            self.assertTrue(all(count <= 1 for count in counts.values()))

    def test_factory_and_generated_test_routes_prepare_the_runtime(self):
        for name in ["mise.toml", "assets/mise-template.toml"]:
            with self.subTest(name=name):
                self.assert_ready_graph(tomllib.loads((SKILL_DIR / name).read_text())["tasks"])

    def test_public_variant_and_target_validation_prepare_the_native_checker(self):
        tasks = tomllib.loads((SKILL_DIR / "mise.toml").read_text())["tasks"]
        for entry in ["variant", "validate-target"]:
            with self.subTest(entry=entry):
                counts = path_counts(tasks, entry)
                for prerequisite in ["doctor", "check-runtime", "setup-runtime"]:
                    self.assertEqual(counts.get(prerequisite, 0), 1, (entry, counts))
                self.assertTrue(all(count <= 1 for count in counts.values()))

    def test_standardization_preserves_all_checks_on_one_runtime_path(self):
        source = base_mise({"primary_term": "source-ledger"})
        normalized = normalize_mise(source)
        self.assert_ready_graph(tomllib.loads(normalized)["tasks"])
        self.assertEqual(normalize_mise(normalized), normalized)

    def test_absent_lint_owner_does_not_erase_the_declared_runtime(self):
        names = {"test", "check-runtime", "setup-runtime"}
        self.assertEqual(runtime_dependencies("test", ["check-runtime"], names), ["check-runtime"])

    def test_conflicting_native_task_is_rejected_without_rewriting_input(self):
        source = normalize_mise(base_mise({"primary_term": "source-ledger"}))
        invalid = source.replace("npm ci --include=dev --ignore-scripts", "npm run custom")
        with self.assertRaisesRegex(ValueError, "native runtime task"):
            normalize_mise(invalid)

    def test_shared_python_helpers_have_an_explicit_mise_owned_environment(self):
        for name in ["mise.toml", "assets/mise-template.toml"]:
            config = tomllib.loads((SKILL_DIR / name).read_text())
            self.assertEqual(config["tools"]["python"], "3.11.15")
            self.assertEqual(config["tools"]["uv"], "0.11.29")
            commands = [(task.get(field, ""), task) for task in config["tasks"].values()
                        for field in ["run", "run_windows"]]
            for command, task in commands:
                if isinstance(command, str) and command.startswith("uv run "):
                    self.assertIn("--no-project --isolated --no-python-downloads", command)
                    self.assertEqual(task["env"]["UV_PYTHON"], "{{tools.python.path}}")

    def test_standardization_isolates_shared_helpers_and_preserves_domain_owners(self):
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

    def test_custom_helper_environment_requires_reconciliation_without_mutation(self):
        source = base_mise({"primary_term": "source-ledger"})
        source = source.replace('[tasks.validate]', '[tasks.validate]\nenv = { UV_PYTHON = "custom" }')
        with self.assertRaisesRegex(ValueError, "Python helper environment"):
            normalize_mise(source)

    def test_uv_version_customization_requires_reconciliation(self):
        source = base_mise({"primary_term": "source-ledger"})
        with self.assertRaisesRegex(ValueError, "runtime uv version"):
            normalize_mise(source.replace('uv = "0.11.29"', 'uv = "custom"'))
        legacy = source.replace('uv = "0.11.29"', 'uv = "latest"')
        self.assertEqual(tomllib.loads(normalize_mise(legacy))["tools"]["uv"], "0.11.29")

    def test_task_definitions_follow_their_reading_dependencies(self):
        for name in ["mise.toml", "assets/mise-template.toml"]:
            with self.subTest(name=name):
                tasks = tomllib.loads((SKILL_DIR / name).read_text())["tasks"]
                seen = set()
                for task, fields in tasks.items():
                    self.assertTrue(set(fields.get("depends", []) + fields.get("depends_post", [])) <= seen, task)
                    seen.add(task)


if __name__ == "__main__":
    unittest.main()
