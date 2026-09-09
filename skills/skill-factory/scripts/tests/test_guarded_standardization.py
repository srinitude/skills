"""Inject invalidation through public preparation and protected apply routes."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from publication_fixtures import evidence
from skill_package import inventory
from test_standardize_registry_skill import profile, write_target


class TestGuardedStandardization(unittest.TestCase):
    def test_prepare_preserves_source_and_apply_requires_current_bound_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            root = base / "clock-anchor"
            write_target(root)
            source = base / "profile.json"
            source.write_text(json.dumps(profile()))
            before = inventory(root)
            args = [root, "--profile", source, "--scope", "user"]
            prepared = base / "prepared" / root.name
            result = run("standardize_registry_skill.py", *args, "--prepare", prepared)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(inventory(root), before)
            report = json.loads(result.stdout)
            self.assertEqual(report["acceptance"], "pending")
            expected = {"route": "standardize-target", "target": str(root),
                        "inputs": report["consumer_inputs"]}
            flags = evidence(base, prepared, expected)
            checked = run("standardize_registry_skill.py", *args, "--check-candidate",
                          "--candidate", prepared, *flags)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertEqual(json.loads(checked.stdout)["acceptance"], "pending")
            self.assertEqual(inventory(root), before)
            self.reject_mutations(base, root, source, prepared, args, flags)
            result = run("standardize_registry_skill.py", *args, "--apply", "--candidate", prepared, *flags)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(inventory(root), inventory(prepared))

    def reject_mutations(self, base, root, source, prepared, args, flags):
        result = run("standardize_registry_skill.py", *args, "--apply", "--candidate", prepared)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("acceptance", result.stderr)
        paths = [base / "evidence.json", base / "context.json", base / "receipt.json",
                 prepared / "SKILL.md", root / "SKILL.md", source]
        for path in paths:
            original = path.read_bytes()
            path.write_bytes(original + b" ")
            protected = inventory(root)
            result = run("standardize_registry_skill.py", *args, "--apply", "--candidate", prepared, *flags)
            self.assertNotEqual(result.returncode, 0, (path, result.stdout))
            self.assertEqual(inventory(root), protected)
            self.assertNotIn("Traceback", result.stderr)
            path.write_bytes(original)


if __name__ == "__main__":
    unittest.main()
