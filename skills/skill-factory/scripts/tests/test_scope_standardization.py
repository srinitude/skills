"""Standardization must resolve scope before any affected write."""
import json
import tempfile
import unittest
from pathlib import Path

from standardization_test_support import reviewed_standardize

from cli import run
from test_standardize_registry_skill import profile, write_target


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()}


def _TestScopeStandardization_test_flow_metadata_is_preserved_when_legacy_scope_is_added(self):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "clock-anchor"
        write_target(root)
        file = root / "SKILL.md"
        text = file.read_text()
        start = text.index("metadata:")
        end = text.index("\n---", start)
        file.write_text(text[:start] + 'metadata: {author: Kiren, version: "0.1.0", custom: "keep"}' + text[end:])
        path = Path(temp) / "profile.json"
        path.write_text(json.dumps(profile()))
        result = reviewed_standardize(root, "--profile", path, "--scope", "user", "--apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('custom: "keep", scope: "user"', file.read_text())
        self.assertIn('author: Kiren, version: "0.1.0"', file.read_text())

def _TestScopeStandardization_test_legacy_missing_scope_blocks_apply_without_changes(self):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "clock-anchor"
        write_target(root)
        path = Path(temp) / "profile.json"
        path.write_text(json.dumps(profile()))
        before = snapshot(root)
        result = reviewed_standardize(root, "--profile", path, "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Should this skill", result.stdout + result.stderr)
        self.assertEqual(snapshot(root), before)

def _TestScopeStandardization_test_failure_after_staging_keeps_original_unchanged(self):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "clock-anchor"
        write_target(root)
        data = profile()
        data["section_rewrites"] = [{"path": "SKILL.md", "heading": "## Missing",
                                     "until": "## Absent", "replacement": "No match."}]
        path = Path(temp) / "profile.json"
        path.write_text(json.dumps(data))
        before = snapshot(root)
        result = reviewed_standardize(root, "--profile", path,
                     "--scope", "user", "--apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(snapshot(root), before)

def _TestScopeStandardization_test_update_preserves_scope_and_other_metadata_on_rerun(self):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "clock-anchor"
        write_target(root)
        path = Path(temp) / "profile.json"
        path.write_text(json.dumps(profile()))
        file = root / "SKILL.md"
        file.write_text(file.read_text().replace("metadata:\n", 'metadata:\n  scope: "project"\n  project-id: "repo:clock"\n'))
        result = reviewed_standardize(root, "--profile", path, "--apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('scope: "project"', file.read_text())
        self.assertIn('project-id: "repo:clock"', file.read_text())


class TestScopeStandardization(unittest.TestCase):
    test_flow_metadata_is_preserved_when_legacy_scope_is_added = _TestScopeStandardization_test_flow_metadata_is_preserved_when_legacy_scope_is_added
    test_legacy_missing_scope_blocks_apply_without_changes = _TestScopeStandardization_test_legacy_missing_scope_blocks_apply_without_changes
    test_failure_after_staging_keeps_original_unchanged = _TestScopeStandardization_test_failure_after_staging_keeps_original_unchanged
    test_update_preserves_scope_and_other_metadata_on_rerun = _TestScopeStandardization_test_update_preserves_scope_and_other_metadata_on_rerun
