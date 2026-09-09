"""Portable variants remove private content and work without source installation."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_scope_standardization import snapshot
from test_skill_variant import plan
from test_variant_acceptance import accept, reviewed_accept
from variant_fixtures import package, project


class TestVariantPortability(unittest.TestCase):
    def test_unrelated_metadata_cannot_be_lost_in_a_variant(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = package(base / "source" / "demo-skill", "project")
            file = source / "SKILL.md"
            file.write_text(file.read_text().replace('metadata:\n', 'metadata:\n  custom: "keep"\n'))
            candidate = package(base / "stage" / "portable-inventory", "user")
            atlas = project(base / "atlas")
            boreal = project(base / "boreal", "repo:boreal", "lib", ".js")
            data = json.loads(plan(source, base, "user", candidate.name).stdout)
            before = snapshot(source)
            result = accept(base, data, source, candidate, [(atlas, "Python src"), (boreal, "JavaScript lib")])
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("preserve other metadata", result.stdout)
            self.assertEqual(snapshot(source), before)
            self.assertFalse((base / candidate.name).exists())

    def test_private_source_content_is_excluded_and_source_can_be_unavailable(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = package(base / "source" / "demo-skill", "project")
            (source / "assets/PRIVATE_CUSTOMER_DATA.txt").write_text("PRIVATE_CUSTOMER_DATA")
            candidate = package(base / "stage" / "portable-inventory", "user")
            atlas = project(base / "atlas")
            boreal = project(base / "boreal", "repo:boreal", "packages/lib", ".js")
            data = json.loads(plan(source, base, "user", candidate.name).stdout)
            before = snapshot(source)
            result = accept(base, data, source, candidate,
                            [(atlas, "Python src"), (boreal, "JavaScript packages/lib")])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(snapshot(source), before)
            target = base / candidate.name
            self.assertNotIn(b"PRIVATE_CUSTOMER_DATA", b"".join(snapshot(target).values()))
            source.rename(base / "source-unavailable")
            for context in [atlas, boreal]:
                result = subprocess.run([sys.executable, str(target / "scripts/inventory.py"),
                    "--project", str(context)], cwd=base, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), {"files": 1, "lines": 2})
            self.assertEqual(run("check_target.py", "validate", target).returncode, 0)
            self.assertEqual(run("check_lineage.py", target).returncode, 0)

    def test_plan_and_unaccepted_review_artifacts_are_exact_and_collision_safe(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = package(base / "source" / "demo-skill", "project")
            candidate = package(base / "stage" / "portable-inventory", "user")
            plan_path, review_path = base / "plan.json", base / "review.json"
            result = plan(source, base, "user", candidate.name, "--output", plan_path)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(plan_path.read_text()), json.loads(result.stdout))
            before = snapshot(source)
            result = run("skill_variant.py", "review", "--plan", plan_path,
                         "--candidate", candidate, "--output", review_path)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = reviewed_accept("accept", "--plan", plan_path,
                         "--candidate", candidate, "--review", review_path)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(json.loads(result.stdout)["source_preserved"])
            review_path.write_text('{"custom": "preserve"}')
            result = run("skill_variant.py", "review", "--plan", plan_path,
                         "--candidate", candidate, "--output", review_path)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(review_path.read_text()), {"custom": "preserve"})
            self.assertEqual(snapshot(source), before)
            self.assertFalse((base / candidate.name).exists())
