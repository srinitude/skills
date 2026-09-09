"""A mechanical text rewrite cannot create a semantic preservation judgment."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from standardization_mapping import repair_mapping_json, snapshot_public_lines, text_digest
from test_use_case_contract import contract


def skill_body(rule):
    return "# Release notes\n\n## Outcome\n\nPrimary audience: human.\n\n" + rule + "\n"


class TestMappingEvidence(unittest.TestCase):
    def exercise(self, changed):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve() / "release-notes"
            (root / "evals").mkdir(parents=True)
            (root / "assets").mkdir()
            (root / "assets/use-case-contract.json").write_text(json.dumps(contract()))
            old = "Run `scripts/check.py` before release."
            new = "Run `mise run check` before release."
            (root / "SKILL.md").write_text(skill_body(old))
            entry = {"id": "source-1", "source_line": 1, "action": "retain",
                     "public_targets": ["SKILL.md"], "public_text_sha256": text_digest(old),
                     "preservation_judgment": "Model reviewed the release prerequisite in context."}
            original = copy.deepcopy(entry)
            path = root / "evals/source-mapping.json"
            path.write_text(json.dumps({"entries": [entry]}))
            prior = snapshot_public_lines(root)
            (root / "SKILL.md").write_text(skill_body(new if changed else old))
            repair_mapping_json(root, {"check.py": "check"} if changed else {}, {}, prior)
            saved = json.loads(path.read_text())["entries"][0]
            if not changed:
                self.assertEqual(saved, original)
                return
            self.assertNotIn("preservation_judgment", saved)
            self.assertEqual(saved["preservation_review"]["state"], "stale")
            self.assertEqual(saved["preservation_review"]["history"][0], original)
            self.assert_recovery(root, path, saved)

    def assert_recovery(self, root, path, saved):
        result = run("check_use_case_contract.py", root)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("stale preservation review", result.stdout)
        saved["preservation_review"]["state"] = "passed"
        path.write_text(json.dumps({"entries": [saved]}))
        result = run("check_use_case_contract.py", root)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("bound preservation judgment", result.stdout)
        saved["preservation_judgment"] = "Model reviewed the new release prerequisite in context."
        saved["preservation_review"]["reviewed_sha256"] = saved["public_text_sha256"]
        path.write_text(json.dumps({"entries": [saved]}))
        self.assertEqual(run("check_use_case_contract.py", root).returncode, 0)

    def test_rewrite_invalidates_review_and_consumer_rejects_stale_claim(self):
        self.exercise(True)

    def test_unchanged_mapping_retains_original_judgment(self):
        self.exercise(False)

    def test_public_text_change_invalidates_a_previously_bound_judgment(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve() / "release-notes"
            (root / "assets").mkdir(parents=True)
            (root / "evals").mkdir()
            (root / "assets/use-case-contract.json").write_text(json.dumps(contract()))
            original = "Review release notes before publishing."
            (root / "SKILL.md").write_text(skill_body(original))
            entry = {"public_targets": ["SKILL.md"], "public_text_sha256": text_digest(original),
                     "preservation_judgment": "Mechanical fixture of a prior model record, not human evidence.",
                     "preservation_review": {"state": "passed", "reviewed_sha256": text_digest(original)}}
            (root / "evals/source-mapping.json").write_text(json.dumps({"entries": [entry]}))
            self.assertEqual(run("check_use_case_contract.py", root).returncode, 0)
            (root / "SKILL.md").write_text(skill_body("Publish without reviewing release notes."))
            result = run("check_use_case_contract.py", root)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("mapped public text changed", result.stdout)
            (root / "SKILL.md").write_text(skill_body(original))
            self.assertEqual(run("check_use_case_contract.py", root).returncode, 0)
