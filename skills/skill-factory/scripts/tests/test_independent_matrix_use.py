"""Independent new and updated packages retain mandatory matrix use in both scopes and audiences."""
import subprocess
import tempfile
import unittest
from itertools import product
from pathlib import Path

from cli import run
from human_matrix_fixtures import save
from skill_package import inventory
from test_human_matrix_use import context, invoke
from test_standardization_inputs import prepare


def output(base, operation, scope, audience):
    if operation == "new":
        target = base / "matrix-example"
        result = run("scaffold_skill.py", "--name", target.name, "--scope", scope,
                     "--audience", audience, "--description", "Use when a study needs an activity selection.", "--dest", base)
    else:
        source, profile, target = prepare(base)
        before = inventory(source)
        result = run("standardize_registry_skill.py", source, "--profile", profile,
                     "--scope", scope, "--audience", audience, "--prepare", target)
        if inventory(source) != before:
            raise AssertionError("Standardization changed the source")
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)
    return target


def eval_inputs(target):
    save(target / "evals/evals.json", {"skill_name": target.name, "evals": [{"id": "identity",
         "prompt": "Resolve the supplied repeated activity.", "expected_output": "Two activity instances retain their identities.",
         "assertions": ["Both occurrences remain independently addressable."]}]})
    save(target / "evals/trigger-queries.json", [{"query": "Resolve the activity selection", "should_trigger": True},
                                                {"query": "What is the current time?", "should_trigger": False}])


class TestIndependentMatrixUse(unittest.TestCase):
    def test_new_updated_scope_audience_combinations_consume_then_reject_a_missing_inventory(self):
        for operation, scope, audience in product(["new", "updated"], ["user", "project"], ["human", "agent"]):
            with self.subTest(operation=operation, scope=scope, audience=audience):
                self.check_output(operation, scope, audience)

    def check_output(self, operation, scope, audience):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            target = output(base, operation, scope, audience)
            missing = invoke("evals", root=target)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("human-context", missing.stderr)
            installed = subprocess.run(["mise", "run", "runtime-install"], cwd=target,
                                       text=True, capture_output=True, timeout=90)
            self.assertEqual(installed.returncode, 0, installed.stdout + installed.stderr)
            eval_inputs(target)
            path, digest = context(base, target)
            args = ["--human-context", path, "--human-context-sha256", digest, "--min-cases", "1", "--min-queries", "2"]
            checked = invoke("evals", args, target)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertIn('"acceptance": "pending"', checked.stdout)
            registry = target / "assets/human-catalogs.json"
            original = registry.read_bytes()
            registry.unlink()
            rejected = invoke("evals", args, target)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("lacks its matrix inventory", rejected.stdout)
            registry.write_bytes(original)
            restored = invoke("evals", args, target)
            self.assertEqual(restored.returncode, 0, restored.stdout + restored.stderr)


if __name__ == "__main__":
    unittest.main()
