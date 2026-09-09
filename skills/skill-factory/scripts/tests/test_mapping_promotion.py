"""Check mapping bindings at promotion; no semantic or human acceptance claim."""
import hashlib
import json
import sys
import subprocess
from pathlib import Path

from standardization_test_support import reviewed_standardize
import tempfile
import unittest

from test_standardize_registry_skill import profile, write_target
from cli import SCRIPTS, run

sys.path.insert(0, str(SCRIPTS))
from standardization_mapping import repair_mapping_json


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()}


class TestMappingPromotion(unittest.TestCase):
    def test_unreviewed_mapping_change_cannot_promote_then_bound_content_recovers(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            (root / "evals").mkdir()
            path = root / "evals/source-mapping.json"
            line = "Run `python3 scripts/anchor.py` once."
            entry = {"source_line": 12, "public_targets": ["SKILL.md"],
                     "public_text_sha256": hashlib.sha256(line.encode()).hexdigest(),
                     "preservation_judgment": "Test binding only; not a semantic review."}
            path.write_text(json.dumps({"entries": [entry]}) + "\n")
            config = Path(temp) / "profile.json"
            config.write_text(json.dumps(profile()))
            before = snapshot(root)
            result = reviewed_standardize(root, "--profile", config,
                         "--scope", "user", "--apply")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("source mapping", result.stderr)
            self.assertEqual(snapshot(root), before)
            self.check_bound_recovery(root, path, config, entry)

    def check_bound_recovery(self, root, path, config, entry):
        # Supplied binding tests mechanics only, not authenticity or sound judgment.
        current = "Run `mise run anchor` once."
        entry["public_text_sha256"] = hashlib.sha256(current.encode()).hexdigest()
        bound = json.dumps({"entries": [entry]}, separators=(",", ":")) + "\n"
        path.write_text(bound)
        result = reviewed_standardize(root, "--profile", config,
                     "--scope", "user", "--apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(path.read_text(), bound)
        self.assertIn(current, (root / "SKILL.md").read_text())

    def test_standardization_preserves_a_failing_exact_inventory_check(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "clock-anchor"
            write_target(root)
            tests = root / "scripts/tests"
            tests.mkdir()
            path = tests / "test_source_mapping.py"
            raw = ("import unittest\r\n"
                   "class ExactSource(unittest.TestCase):\r\n"
                   "    def test_inventory(self):\r\n"
                   "        files = {'kept': 'café', 'unexpected': 'new'}\r\n"
                   "        EXPECTED_FILES = {'kept': 'café'}\r\n"
                   "        self.assertEqual(files, EXPECTED_FILES)\r\n"
                   "unittest.main()\r\n").encode()
            path.write_bytes(raw)
            config = Path(temp) / "profile.json"
            config.write_text(json.dumps(profile()))
            before = subprocess.run([sys.executable, str(path)], capture_output=True)
            self.assertEqual(before.returncode, 1, before.stderr)
            result = reviewed_standardize(root, "--profile", config,
                         "--scope", "user", "--apply")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(path.read_bytes(), raw)
            after = subprocess.run([sys.executable, str(path)], capture_output=True)
            self.assertEqual(after.returncode, 1, after.stderr)
            self.assertIn(b"unexpected", after.stderr)

    def test_assertions_are_not_rewritten_to_fit_changed_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "evals").mkdir()
            (root / "SKILL.md").write_text("Run `mise run check` before release.\n")
            path = root / "evals/source-mapping.json"
            content = {"entries": [{"public_assertions": [{"target": "SKILL.md",
                "contains": "Run `scripts/check.py` before release."}]}]}
            raw = json.dumps(content)
            path.write_text(raw)
            with self.assertRaisesRegex(ValueError, "source mapping"):
                repair_mapping_json(root, {"check.py": "check"}, {}, {})
            self.assertEqual(path.read_text(), raw)


    def test_malformed_mapping_fields_fail_without_changing_bytes(self):
        cases = [
            {"entries": [{}], "semantic_mappings": None},
            {"entries": [{"public_semantic_id": []}]},
            {"entries": [{"public_targets": ["SKILL.md"], "public_text_sha256": []}]},
            {"entries": []},
            {"entries": [{"public_assertions": [{"target": "../outside", "contains": "source"}]}]},
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "evals").mkdir()
            (root / "SKILL.md").write_text("source\n")
            path = root / "evals/source-mapping.json"
            for data in cases:
                with self.subTest(data=data):
                    raw = json.dumps(data)
                    path.write_text(raw)
                    self.assertRaisesRegex(ValueError, "source mapping", repair_mapping_json, root)
                    self.assertEqual(path.read_text(), raw)

if __name__ == "__main__":
    unittest.main()
