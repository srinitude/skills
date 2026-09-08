"""Read-only variant planning and source/destination boundaries."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_scaffold_skill import scaffold
from test_scope_standardization import snapshot


def plan(source, dest, scope="project", name="derived-skill", *extra):
    return run("skill_variant.py", "plan", "--source", source,
               "--source-id", "skill:" + source.name, "--scope", scope,
               "--name", name, "--dest", dest, *extra)


class TestVariantPlanning(unittest.TestCase):
    def test_missing_project_context_does_not_write(self):
        with tempfile.TemporaryDirectory() as temp:
            scaffold(temp)
            source = Path(temp) / "demo-skill"
            before = snapshot(source)
            result = plan(source, temp)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("project", result.stdout)
            self.assertEqual(snapshot(source), before)
            self.assertFalse((Path(temp) / "derived-skill").exists())

    def test_plan_records_complete_source_and_project_context(self):
        with tempfile.TemporaryDirectory() as temp:
            scaffold(temp)
            source = Path(temp) / "demo-skill"
            project = Path(temp) / "project"
            project.mkdir()
            (project / "AGENTS.md").write_text("Use Python. Read src/ files only.\n")
            result = plan(source, temp, "project", "derived-skill",
                          "--project", project, "--project-id", "repo:example")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["source"]["scope"], "user")
            self.assertEqual(data["target"]["scope"], "project")
            self.assertIn("scripts/skill_info.py", data["source"]["files"])
            self.assertIn("AGENTS.md", data["project"]["files"])
            self.assertEqual(data["writes"], 0)

    def test_same_name_refuses_shadowing_and_existing_target_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            scaffold(temp, "demo-skill", "Use when testing scope.", "--scope", "project")
            source = Path(temp) / "demo-skill"
            for name in ["demo-skill", "occupied"]:
                target = Path(temp) / name
                target.mkdir(exist_ok=True)
                result = plan(source, temp, "user", name)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertTrue(target.is_dir())

    def test_source_symlink_rejected_before_read(self):
        with tempfile.TemporaryDirectory() as temp:
            scaffold(temp)
            link = Path(temp) / "linked"
            link.symlink_to(Path(temp) / "demo-skill", target_is_directory=True)
            result = plan(link, temp, "user")
            self.assertEqual(result.returncode, 1)
            self.assertIn("symlink", result.stdout)
