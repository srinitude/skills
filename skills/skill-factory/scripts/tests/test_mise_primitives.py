"""Behavior tests for exhaustive, domain-specific Mise primitive decisions."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR, run


def payloads():
    names = ["mise-primitives-catalog.json", "mise-primitives.json"]
    return [json.loads((SKILL_DIR / "assets" / name).read_text())
            for name in names]


def write_case(root, catalog, decisions, mise="[tasks.check]\nrun='true'\n"):
    assets = root / "assets"
    assets.mkdir()
    (assets / "mise-primitives-catalog.json").write_text(
        json.dumps(catalog), encoding="utf-8")
    (assets / "mise-primitives.json").write_text(
        json.dumps(decisions), encoding="utf-8")
    (assets / "use-case-contract.json").write_text(
        json.dumps({"skill": decisions["skill"],
                    "domain_terms": [decisions["skill"], "agent skill"]}),
        encoding="utf-8")
    (root / "mise.toml").write_text(mise, encoding="utf-8")


class TestMisePrimitives(unittest.TestCase):
    def check(self, edit=None, mise=None):
        catalog, decisions = payloads()
        if edit:
            edit(catalog, decisions)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "skill-factory"
            root.mkdir()
            source = (SKILL_DIR / "mise.toml").read_text()
            write_case(root, catalog, decisions, mise or source)
            return run("check_mise_primitives.py", root)

    def test_factory_catalog_and_decisions_pass(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_primitive_disposition_fails(self):
        def edit(_, decisions):
            decisions["groups"]["config"]["not_applicable"].remove("oci")
        result = self.check(edit)
        self.assertEqual(result.returncode, 1)
        self.assertIn("must classify every primitive", result.stdout)

    def test_duplicate_primitive_disposition_fails(self):
        def edit(_, decisions):
            decisions["groups"]["config"]["used"].append("oci")
        result = self.check(edit)
        self.assertEqual(result.returncode, 1)
        self.assertIn("overlap", result.stdout)

    def test_claimed_use_requires_real_mise_field(self):
        result = self.check(mise="[tasks.check]\nrun='true'\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("claims used but is absent", result.stdout)

    def test_generic_reason_fails(self):
        def edit(_, decisions):
            decisions["groups"]["task"]["used_reason"] = "Useful."
        result = self.check(edit)
        self.assertEqual(result.returncode, 1)
        self.assertIn("domain term", result.stdout)

    def test_malformed_disposition_fails_without_traceback(self):
        def edit(_, decisions):
            decisions["groups"]["config"]["used"] = "tasks"
        result = self.check(edit)
        self.assertEqual(result.returncode, 1)
        self.assertIn("string lists", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_duplicate_inside_one_disposition_fails(self):
        def edit(_, decisions):
            decisions["groups"]["config"]["used"].append("tasks")
        result = self.check(edit)
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicates", result.stdout)

    def test_domain_term_must_not_match_inside_an_unrelated_word(self):
        def edit(_, decisions):
            decisions["skill"] = "git"
            decisions["groups"]["task"]["used_reason"] = "Digital output exists."
        result = self.check(edit)
        self.assertEqual(result.returncode, 1)
        self.assertIn("task.used_reason", result.stdout)


if __name__ == "__main__":
    unittest.main()
