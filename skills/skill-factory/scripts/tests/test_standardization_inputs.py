"""Test declaration preservation and preflight; no semantic acceptance claim."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_mapping_promotion import snapshot
from test_standardize_registry_skill import profile, write_target


class TestStandardizationInputs(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / "clock-anchor"
        write_target(self.root)
        self.config = self.base / "profile.json"
        self.data = profile()

    def invoke(self):
        self.config.write_text(json.dumps(self.data))
        return run("standardize_registry_skill.py", self.root, "--profile", self.config,
                   "--scope", "user", "--apply")

    def test_unresolved_declarations_block_without_touching_target(self):
        good = json.dumps(self.data)
        before = snapshot(self.root)
        for field in ["audience", "initial_context"]:
            self.data = json.loads(good)
            self.data.pop(field)
            result = self.invoke()
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn(field, result.stderr)
            self.assertEqual(snapshot(self.root), before)
        self.data = json.loads(good)
        self.assertEqual(self.invoke().returncode, 0)

    def test_existing_use_case_meaning_and_extensions_are_preserved(self):
        self.assertEqual(self.invoke().returncode, 0)
        path = self.root / "assets/use-case-contract.json"
        original = json.loads(path.read_text())
        original.update(audience=self.data["audience"], initial_context=self.data["initial_context"])
        original["domain_dimensions"]["quality"] = ["Clock anchor keeps exact offset and per-turn freshness."]
        original["domain_extension"] = {"precision": "one observed anchor, no invented refresh"}
        raw = json.dumps(original, separators=(",", ":")) + "\n"
        path.write_text(raw)
        accepted = run("check_use_case_contract.py", self.root, "--accept")
        self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(path.read_text(), raw)

    def test_conflicting_existing_audience_cannot_be_relabelled(self):
        self.assertEqual(self.invoke().returncode, 0)
        path = self.root / "assets/use-case-contract.json"
        original = json.loads(path.read_text())
        original.update(audience={"primary": "human"}, initial_context=self.data["initial_context"])
        path.write_text(json.dumps(original))
        before = snapshot(self.root)
        result = self.invoke()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("audience", result.stderr)
        self.assertEqual(snapshot(self.root), before)

    def test_malformed_profile_sets_fail_cleanly_without_writes(self):
        before = snapshot(self.root)
        for data in [None, [], {"profiles": None}, {"profiles": {"clock-anchor": []}}]:
            self.config.write_text(json.dumps(data))
            result = run("standardize_registry_skill.py", self.root, "--profile", self.config,
                         "--scope", "user", "--apply")
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(snapshot(self.root), before)

    def test_duplicate_profile_keys_fail_before_any_write(self):
        self.config.write_text('{"audience":{"primary":"human"},' + json.dumps(self.data)[1:])
        before = snapshot(self.root)
        result = run("standardize_registry_skill.py", self.root, "--profile", self.config,
                     "--scope", "user", "--apply")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("duplicate JSON key", result.stderr)
        self.assertEqual(snapshot(self.root), before)


if __name__ == "__main__":
    unittest.main()
