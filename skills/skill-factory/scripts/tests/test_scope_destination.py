"""Installation placement consumes verified integration rules separately from scope."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR, run
from test_scope_standardization import snapshot

ADAPTER = SKILL_DIR.parents[1] / "adapters/shared-skills/check_destination.py"


class TestScopeDestination(unittest.TestCase):
    def test_collision_in_another_shared_root_prevents_shadowing(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            user_root = base / "person/.agents/skills"
            project_root = base / "project/.agents/skills"
            (user_root / "inventory-variant").mkdir(parents=True)
            project_root.mkdir(parents=True)
            result = subprocess.run([sys.executable, str(ADAPTER), "--scope", "project",
                "--name", "inventory-variant", "--dest", str(project_root / "inventory-variant"),
                "--home", str(base / "person"), "--project", str(base / "project")],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertFalse((project_root / "inventory-variant").exists())

    def test_integration_resolves_both_scopes_without_installing(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            for scope, owner in [("user", base / "person"), ("project", base / "project")]:
                root = owner / ".agents/skills"
                root.mkdir(parents=True)
                target = root / "inventory-variant"
                result = subprocess.run([sys.executable, str(ADAPTER), "--scope", scope,
                    "--name", target.name, "--dest", str(target), "--home", str(base / "person"),
                    "--project", str(base / "project")], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(json.loads(result.stdout)["scope"], scope)
                self.assertFalse(target.exists())

    def test_wrong_scope_destination_blocks_scaffold_without_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = root / "placement.json"
            receipt.write_text(json.dumps({"kind": "installation", "scope": "project",
                "destination": str(root / "demo-skill"), "scope_root": str(root),
                "visible_roots": [str(root)], "reference": "https://agentskills.io/client-implementation/adding-skills-support"}))
            before = snapshot(root)
            result = run("scaffold_skill.py", "--name", "demo-skill", "--scope", "user",
                         "--description", "Use when testing destination scope.", "--dest", root,
                         "--placement-receipt", receipt)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("scope", result.stdout)
            self.assertEqual(snapshot(root), before)
