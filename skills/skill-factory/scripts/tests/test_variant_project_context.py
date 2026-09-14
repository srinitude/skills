"""Project placement and complete authoritative context gate adaptation."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_scope_standardization import snapshot
from test_skill_variant import plan
from test_variant_acceptance import accept, reviewed_accept
from variant_fixtures import package, project, review, write_json


def _TestVariantProjectContext_test_project_destination_inside_declared_project_accepts_without_context_drift(self):
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = package(base / "source" / "demo-skill", "user")
        candidate = package(base / "stage" / "atlas-inventory", "project")
        atlas = project(base / "atlas")
        destination = atlas / "skills"
        destination.mkdir()
        data = json.loads(plan(source, destination, "project", candidate.name,
                          "--project", atlas, "--project-id", "repo:atlas").stdout)
        before = snapshot(source)
        result = accept(base, data, source, candidate, [(atlas, "Python src")])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(snapshot(source), before)
        self.assertTrue((destination / candidate.name / "SKILL.md").is_file())

def _TestVariantProjectContext_test_missing_project_review_fails_before_promotion(self):
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = package(base / "source" / "demo-skill", "user")
        candidate = package(base / "stage" / "atlas-inventory", "project")
        atlas = project(base / "atlas")
        data = json.loads(plan(source, base, "project", candidate.name,
                          "--project", atlas, "--project-id", "repo:atlas").stdout)
        evidence = review(source, candidate, [(atlas, "Python src")])
        evidence.pop("project_review", None)
        write_json(base / "plan.json", data)
        write_json(base / "review.json", evidence)
        before = snapshot(source)
        result = reviewed_accept("accept", "--plan", base / "plan.json",
                     "--candidate", candidate, "--review", base / "review.json")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("project_review", result.stdout)
        self.assertEqual(snapshot(source), before)
        self.assertFalse((base / candidate.name).exists())

def _TestVariantProjectContext_test_edited_plan_cannot_place_variant_inside_source(self):
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        source = package(base / "source" / "demo-skill", "project")
        candidate = package(base / "stage" / "portable-inventory", "user")
        atlas = project(base / "atlas")
        boreal = project(base / "boreal", "repo:boreal", "lib", ".js")
        data = json.loads(plan(source, base, "user", candidate.name).stdout)
        data["target"]["path"] = str(source / candidate.name)
        before = snapshot(source)
        result = accept(base, data, source, candidate,
                        [(atlas, "Python src"), (boreal, "JavaScript lib")])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(snapshot(source), before)


class TestVariantProjectContext(unittest.TestCase):
    test_project_destination_inside_declared_project_accepts_without_context_drift = _TestVariantProjectContext_test_project_destination_inside_declared_project_accepts_without_context_drift
    test_missing_project_review_fails_before_promotion = _TestVariantProjectContext_test_missing_project_review_fails_before_promotion
    test_edited_plan_cannot_place_variant_inside_source = _TestVariantProjectContext_test_edited_plan_cannot_place_variant_inside_source
