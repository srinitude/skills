"""Tests for factory-owned registry lineage refresh routing."""
import importlib.util
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "refresh_registry_lineage.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("refresh_registry_lineage", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestRegistryLineageRefresh(unittest.TestCase):
    def fixture(self, root, kind):
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

    def test_archived_source_keeps_native_lineage_and_marks_scaffolding(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root, "archived_source")
            MODULE.refresh_skill(root, "clock-anchor")
            manifest = json.loads((root / "evidence/ports/clock-anchor/source-manifest.json").read_text())
            lineage = json.loads((root / "skills/clock-anchor/evals/source-lineage.json").read_text())
            self.assertEqual(manifest["source_kind"], "archived_source")
            self.assertEqual(lineage["source_files"], [{
                "path": "native.txt", "sha256": manifest["files"][0]["sha256"]}])
            self.assertEqual(lineage["public_files"], [{
                "path": "SKILL.md",
                "source_paths": ["native.txt", "target-scaffolding"],
            }])

    def test_repository_baseline_adopts_current_lineage_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root, "repository_baseline")
            manifest_path = root / "evidence/ports/clock-anchor/source-manifest.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["native_manifest_sha256"] = hashlib.sha256(b"old").hexdigest()
            manifest_path.write_text(json.dumps(manifest))
            MODULE.refresh_skill(root, "clock-anchor")
            lineage = json.loads((root / "skills/clock-anchor/evals/source-lineage.json").read_text())
            saved = json.loads(manifest_path.read_text())
            self.assertEqual(saved["native_manifest_sha256"],
                             lineage["native_manifest_sha256"])
            self.assertEqual(lineage["native_manifest_sha256"],
                             MODULE.canonical_digest(lineage["source_files"]))

    def test_refresh_formats_before_hashing_and_after_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root, "repository_baseline")
            skill = root / "skills/clock-anchor"
            lineage = skill / "evals/source-lineage.json"
            manifest = root / "evidence/ports/clock-anchor/source-manifest.json"
            calls = []
            with mock.patch.object(MODULE, "format_target",
                                   side_effect=lambda path: calls.append(("target", path))), \
                 mock.patch.object(MODULE, "format_files",
                                   side_effect=lambda path, files: calls.append(
                                       ("files", path, tuple(files)))):
                MODULE.refresh_skill(root, "clock-anchor")
            self.assertEqual(calls, [
                ("target", skill),
                ("files", skill, (lineage, manifest)),
            ])

    def test_unknown_skill_fails_before_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "skills").mkdir()
            with self.assertRaisesRegex(ValueError, "unknown registry skill"):
                MODULE.validate_names(root, ["missing"])


if __name__ == "__main__":
    unittest.main()
