"""Executable adaptation, independent validation, and immutable source proof."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from publication_fixtures import variant
from test_scope_standardization import snapshot
from test_skill_variant import plan
from variant_fixtures import export_packages, package, project, review, write_json


def accept(base, data, source, candidate, scenarios):
    plan_path, review_path = base / "plan.json", base / "review.json"
    write_json(plan_path, data)
    write_json(review_path, review(source, candidate, scenarios))
    return variant("--plan", plan_path,
               "--candidate", candidate, "--review", review_path)


class TestVariantAcceptance(unittest.TestCase):
    def test_both_directions_preserve_source_and_execute_adapted_behavior(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            atlas = project(base / "atlas")
            boreal = project(base / "boreal", "repo:boreal", "packages/lib", ".js")
            source = package(base / "source" / "demo-skill", "user")
            candidate = package(base / "stage" / "atlas-inventory", "project")
            dest = base / "accepted"
            dest.mkdir()
            result = plan(source, dest, "project", candidate.name,
                          "--project", atlas, "--project-id", "repo:atlas")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data, before = json.loads(result.stdout), snapshot(source)
            result = accept(base, data, source, candidate, [(atlas, "Python src directory")])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(snapshot(source), before)
            derived = dest / candidate.name
            self.assertTrue(json.loads(result.stdout)["source_preserved"])
            self.assertEqual(run("check_lineage.py", derived).returncode, 0)
            user = package(base / "stage" / "portable-inventory", "user")
            result = plan(derived, dest, "user", user.name)
            data, before = json.loads(result.stdout), snapshot(derived)
            result = accept(base, data, derived, user, [(atlas, "Python src directory"), (boreal, "JavaScript packages/lib directory")])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(snapshot(derived), before)
            lineage = json.loads((dest / user.name / "evals/source-lineage.json").read_text())
            self.assertEqual(lineage["derivation"]["source"]["identity"], "skill:atlas-inventory")
            self.assertEqual(lineage["derivation"]["source"]["scope"], "project")
            export_packages(base)

    def test_failed_candidate_does_not_touch_source_or_destination(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = package(base / "source" / "demo-skill", "project")
            candidate = package(base / "stage" / "portable-inventory", "user")
            (candidate / "assets/private.txt").write_text("PRIVATE_CUSTOMER_DATA")
            result = plan(source, base, "user", candidate.name)
            before = snapshot(source)
            result = accept(base, json.loads(result.stdout), source, candidate, [])
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(snapshot(source), before)
            self.assertFalse((base / candidate.name).exists())
