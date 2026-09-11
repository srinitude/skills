"""Tests for factory-owned registry lineage refresh routing."""
import importlib.util
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
import base64
from registry_lineage_plan import build_plan
from skill_package import inventory
from standardization_test_support import native_formatter

SCRIPT = Path(__file__).resolve().parents[1] / "refresh_registry_lineage.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("refresh_registry_lineage", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def planned_json(plan, owner):
    item = next(item for item in plan['changes'] if item['owner'] == owner
                and (owner == 'repository' or item['path'] == 'evals/source-lineage.json'))
    return json.loads(base64.b64decode(item['content_base64']))


def _TestRegistryLineageRefresh_fixture(self, root, kind):
    skill = root / "skills/clock-anchor"
    (skill / "evals").mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Clock anchor\n")
    profile = root / "skills/skill-factory/assets"
    profile.mkdir(parents=True)
    (profile / "registry-standardization-profiles.json").write_text("{}\n")
    digest = hashlib.sha256(b"native\n").hexdigest()
    evidence = root / "evidence/ports/clock-anchor"
    evidence.mkdir(parents=True)
    (evidence / "native.txt").write_text("native\n")
    entry = {"bytes": 7, "location_kind": "evidence",
             "location_path": "native.txt", "sha256": digest,
             "source_path": "native.txt"}
    manifest = {"schema": "source-evidence/v1", "skill": "clock-anchor",
                "source_kind": kind, "native_manifest_sha256": digest,
                "evidence_packet_sha256": digest, "files": [entry]}
    (evidence / "source-manifest.json").write_text(json.dumps(manifest))
    lineage = {"schema_version": 1, "public_version": "0.1.0",
               "native_version": "1", "native_manifest_sha256": digest,
               "source_case_ids": ["case"],
               "source_files": [{"path": "native.txt", "sha256": digest}],
               "public_files": [{"path": "SKILL.md",
                                 "source_paths": ["native.txt"]}]}
    (skill / "evals/source-lineage.json").write_text(json.dumps(lineage))

def _TestRegistryLineageRefresh_test_unknown_skill_fails_before_execution(self):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "skills").mkdir()
        with self.assertRaisesRegex(ValueError, "unknown registry skill"):
            MODULE.validate_names(root, ["missing"])

def _TestRegistryLineageRefresh_test_archived_source_keeps_native_lineage_and_marks_scaffolding(self):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        self.fixture(root, "archived_source")
        plan = build_plan(root.resolve(), ["clock-anchor"])
        manifest = planned_json(plan, "repository")
        lineage = planned_json(plan, "skill")
        self.assertEqual(manifest["source_kind"], "archived_source")
        self.assertEqual(lineage["source_files"], [{
            "path": "native.txt", "sha256": manifest["files"][0]["sha256"]}])
        self.assertEqual(lineage["public_files"], [{
            "path": "SKILL.md",
            "source_paths": ["native.txt", "target-scaffolding"],
        }])

def _TestRegistryLineageRefresh_test_repository_baseline_adopts_current_lineage_identity(self):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        self.fixture(root, "repository_baseline")
        manifest_path = root / "evidence/ports/clock-anchor/source-manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["native_manifest_sha256"] = hashlib.sha256(b"old").hexdigest()
        manifest_path.write_text(json.dumps(manifest))
        plan = build_plan(root.resolve(), ["clock-anchor"])
        lineage = planned_json(plan, "skill")
        saved = planned_json(plan, "repository")
        self.assertEqual(saved["native_manifest_sha256"],
                         lineage["native_manifest_sha256"])
        self.assertEqual(lineage["native_manifest_sha256"],
                         MODULE.canonical_digest(lineage["source_files"]))

def _TestRegistryLineageRefresh_test_native_plan_formats_sources_before_derived_metadata_without_writing(self):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp).resolve(); self.fixture(root, "repository_baseline")
        native_formatter(root)
        skill = root / 'skills/clock-anchor'
        (skill / 'settings.json').write_text('{"value":1}')
        before = inventory(root); plan = build_plan(root, ['clock-anchor'])
        self.assertEqual(inventory(root), before)
        self.assertEqual([item['path'] for item in plan['changes']],
            ['settings.json', 'evals/source-lineage.json', 'evidence/ports/clock-anchor/source-manifest.json'])
        current = planned_json(plan, 'repository')
        setting = next(item for item in current['files'] if item['source_path'] == 'settings.json')
        self.assertEqual(setting['sha256'], hashlib.sha256(b'{ "value": 1 }\n').hexdigest())

def _TestRegistryLineageRefresh_test_public_inventory_excludes_runtime_but_rejects_owned_links(self):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        self.fixture(root, "repository_baseline")
        skill = root / "skills/clock-anchor"
        bins = skill / "node_modules/.bin"
        bins.mkdir(parents=True)
        (bins / "compiler").symlink_to(skill / "SKILL.md")
        self.assertEqual(MODULE.public_paths(root, "clock-anchor"), ["SKILL.md"])
        (skill / "owned-link").symlink_to(skill / "SKILL.md")
        with self.assertRaises(ValueError):
            MODULE.public_paths(root, "clock-anchor")


class TestRegistryLineageRefresh(unittest.TestCase):
    fixture = _TestRegistryLineageRefresh_fixture
    test_archived_source_keeps_native_lineage_and_marks_scaffolding = _TestRegistryLineageRefresh_test_archived_source_keeps_native_lineage_and_marks_scaffolding
    test_repository_baseline_adopts_current_lineage_identity = _TestRegistryLineageRefresh_test_repository_baseline_adopts_current_lineage_identity
    test_native_plan_formats_sources_before_derived_metadata_without_writing = _TestRegistryLineageRefresh_test_native_plan_formats_sources_before_derived_metadata_without_writing
    test_public_inventory_excludes_runtime_but_rejects_owned_links = _TestRegistryLineageRefresh_test_public_inventory_excludes_runtime_but_rejects_owned_links
    test_unknown_skill_fails_before_execution = _TestRegistryLineageRefresh_test_unknown_skill_fails_before_execution


if __name__ == "__main__":
    unittest.main()
