"""Adaptation failures preserve source bytes and never publish an invalid variant."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_scope_standardization import snapshot
from test_skill_variant import plan
from test_variant_acceptance import accept
from variant_fixtures import package, project


class TestVariantBoundaries(unittest.TestCase):
    def test_label_only_generalization_fails_actual_second_project_behavior(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = package(base / "source" / "demo-skill", "project")
            candidate = package(base / "stage" / "portable-inventory", "project")
            file = candidate / "SKILL.md"
            file.write_text(file.read_text().replace('scope: "project"', 'scope: "user"'))
            atlas = project(base / "atlas")
            boreal = project(base / "boreal", "repo:boreal", "lib", ".js")
            data = json.loads(plan(source, base, "user", candidate.name).stdout)
            before = snapshot(source)
            result = accept(base, data, source, candidate, [(atlas, "Python src"), (boreal, "JavaScript lib")])
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("adapted behavior failed", result.stdout)
            self.assertEqual(snapshot(source), before)
            self.assertFalse((base / candidate.name).exists())

    def test_hidden_source_dependency_and_missing_attribution_block_acceptance(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = package(base / "source" / "demo-skill", "project")
            candidate = package(base / "stage" / "portable-inventory", "user")
            atlas = project(base / "atlas")
            boreal = project(base / "boreal", "repo:boreal", "lib", ".js")
            data = json.loads(plan(source, base, "user", candidate.name).stdout)
            before = snapshot(source)
            note = candidate / "assets/dependency.txt"
            note.write_text(str(source))
            scenarios = [(atlas, "Python src"), (boreal, "JavaScript lib")]
            result = accept(base, data, source, candidate, scenarios)
            self.assertEqual(result.returncode, 1)
            self.assertIn("hidden source dependency", result.stdout)
            note.unlink()
            (candidate / "NOTICE").unlink()
            result = accept(base, data, source, candidate, scenarios)
            self.assertEqual(result.returncode, 1)
            self.assertIn("attribution", result.stdout)
            self.assertEqual(snapshot(source), before)

    def test_explicit_in_place_scope_change_requires_and_passes_adaptation(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = package(base / "source" / "demo-skill", "project")
            candidate = package(base / "stage" / "demo-skill", "user")
            atlas = project(base / "atlas")
            boreal = project(base / "boreal", "repo:boreal", "lib", ".js")
            result = plan(source, source.parent, "user", source.name, "--in-place")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = accept(base, json.loads(result.stdout), source, candidate,
                            [(atlas, "Python src"), (boreal, "JavaScript lib")])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse(json.loads(result.stdout)["source_preserved"])
            self.assertTrue(json.loads(result.stdout)["source_change_explicit"])
            self.assertIn('scope: "user"', (source / "SKILL.md").read_text())

    def test_source_change_after_plan_rejects_candidate_and_preserves_current_source(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = package(base / "source" / "demo-skill", "project")
            candidate = package(base / "stage" / "portable-inventory", "user")
            data = json.loads(plan(source, base, "user", candidate.name).stdout)
            (source / "new.txt").write_text("Source update must survive.\n")
            before = snapshot(source)
            result = accept(base, data, source, candidate, [])
            self.assertEqual(result.returncode, 1)
            self.assertIn("source changed", result.stdout)
            self.assertEqual(snapshot(source), before)
