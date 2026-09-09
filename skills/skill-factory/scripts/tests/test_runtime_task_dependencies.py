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
