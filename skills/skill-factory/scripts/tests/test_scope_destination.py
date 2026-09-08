"""Installation placement consumes verified integration rules separately from scope."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_scope_standardization import snapshot

class TestScopeDestination(unittest.TestCase):
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
