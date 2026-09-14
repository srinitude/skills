"""Check actual scaffold plans retain their rules in native task owners."""
import base64
import json
import re
import unittest
import tempfile
import sys
from pathlib import Path

from cli import SCRIPTS
sys.path.insert(0, str(SCRIPTS))
from scaffold_rules import template_inputs
from scaffold_plan import render_plan
from scaffold_skill import source_files
import tomllib


def rendered():
    plan = render_plan(SCRIPTS.parent, {"NAME": "plain-skill", "DESCRIPTION": "Use when plain output is needed.",
                                      "SCOPE": "user", "DATE": "2026-01-01"}, source_files())
    return {item["path"]: base64.b64decode(item["content_base64"]).decode() for item in plan["files"]}


def test_body_uses_real_workflow_tasks(self):
    files = rendered()
    body, tasks = files["SKILL.md"], tomllib.loads(files["mise.toml"])["tasks"]
    self.assertIn("mise run rule:body-context", body)
    self.assertLessEqual(len(body.splitlines()), 200)
    for name in re.findall(r"mise run (rule:body-[a-z-]+)", body):
        self.assertEqual(tasks[name]["run"], "node scripts/run_rule.ts " + name)
        self.assertEqual(len(tasks[name]["depends"]), 1)
        self.assertIn(tasks[name]["depends"][0], tasks)
    declared = {item["task"] for item in json.loads(files["assets/use-case-contract.json"])["task_graph"]["public_operations"]}
    self.assertTrue(set(re.findall(r"mise run (rule:body-[a-z-]+)", body)) <= declared)


def test_source_rules_survive_without_loss(self):
    files = rendered()
    source = (SCRIPTS.parent / "assets/skill-template.md").read_text()
    source = source.replace("{{NAME}}", "plain-skill").replace("{{SCOPE}}", "user")
    descriptions = "\n".join(task.get("description", "") for task in tomllib.loads(files["mise.toml"])["tasks"].values())
    preserved = files["SKILL.md"] + "\n" + descriptions
    for block in re.split(r"\n\s*\n", source):
        if block.startswith("---"):
            continue
        self.assertIn(block.strip(), preserved, block[:100])
    self.assertIn("SCAFFOLD-PLACEHOLDER", files["SKILL.md"])


def test_rejects_unreviewed_template_mapping(self):
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "assets").mkdir()
        source = SCRIPTS.parent / "assets/skill-template.md"
        target = root / "assets/skill-template.md"
        target.write_bytes(source.read_bytes())
        original = json.loads((SCRIPTS.parent / "assets/skill-template-routes.json").read_text())
        mapping = root / "assets/skill-template-routes.json"
        cases = [{**original, "routes": original["routes"][:-1]},
                 {**original, "routes": original["routes"] + original["routes"][:1]},
                 {**original, "source_sha256": "0" * 64}]
        for value in cases:
            mapping.write_text(json.dumps(value))
            self.assertRaises(ValueError, template_inputs, root)
        mapping.write_text(json.dumps(original))
        blocks, owners = template_inputs(root)
        self.assertEqual(len(owners), len(original["routes"]))
        target.write_bytes(source.read_bytes() + b"\nA changed rule.\n")
        with self.assertRaises(ValueError):
            template_inputs(root)


def test_broad_method_reaches_created_skill(self):
    files = rendered()
    startup = files["SKILL.md"].split("## Outcome", 1)[0]
    self.assertIn("Build broad working paths before polish", startup)
    self.assertIn("safety and required inputs", startup)
    tasks = tomllib.loads(files["mise.toml"])["tasks"]
    progress = tasks["rule:implementation-progress"]["description"]
    for duty in ["Build broad working paths before optional polish", "owner, required inputs, next action and deciding check",
                 "main paths work", "whole domain result", "A small request needs a small change"]:
        self.assertIn(duty, progress)
    selected = tasks["rule:selected"]["description"]
    self.assertIn("broad work or precise repair", selected)
    acceptance = tasks["rule:acceptance"]["description"]
    self.assertIn("whole factory", acceptance)
    self.assertIn("whole output skill", acceptance)
    self.assertIn("whole domain result", acceptance)
    body = tasks["rule:body-implementation-progress"]["description"]
    self.assertNotIn("Close the smallest ready functional path", body)
    self.assertIn("broad working paths", body)
    self.assertEqual(tasks["rule:body-implementation-progress"]["depends"], ["rule:implementation-progress"])


def load_tests(loader, tests, pattern):
    cls = type("ScaffoldRuleTests", (unittest.TestCase,), {
        "test_body_uses_real_workflow_tasks": test_body_uses_real_workflow_tasks,
        "test_source_rules_survive_without_loss": test_source_rules_survive_without_loss,
        "test_rejects_unreviewed_template_mapping": test_rejects_unreviewed_template_mapping,
        "test_broad_method_reaches_created_skill": test_broad_method_reaches_created_skill})
    return loader.loadTestsFromTestCase(cls)
