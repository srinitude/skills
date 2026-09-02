"""Behavior tests for run scaffolding and validation."""

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

from runtime_test_support import (
    comparison_proof, figma_audit_proof, governance_proof, property_proof,
    quality_evidence, render_context_proof,
)

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
NEW_RUN = SKILL_DIR / "scripts" / "new_run.py"
VALIDATE = SKILL_DIR / "scripts" / "validate_run.py"


def run(script, *args):
    command = [sys.executable, str(script), *map(str, args)]
    return subprocess.run(command, capture_output=True, text=True, timeout=30)


class TestRunScaffold(unittest.TestCase):
    def test_new_run_writes_valid_update_record(self):
        with tempfile.TemporaryDirectory() as temp:
            target = pathlib.Path(temp) / "run.json"
            result = run(
                NEW_RUN,
                "--output", target,
                "--mode", "update",
                "--platform", "ios",
                "--ui-scope", "account-settings",
                "--source", "figma_file=https://example.invalid/file",
                "--source", "codebase=/workspace/product",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            record = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(record["mode"], "update")
            self.assertEqual(record["target"]["platform"], "ios")
            self.assertEqual(len(record["sources"]), 2)
            checked = run(VALIDATE, target)
            self.assertEqual(checked.returncode, 0, checked.stdout)

    def test_new_run_refuses_unknown_source_type(self):
        with tempfile.TemporaryDirectory() as temp:
            target = pathlib.Path(temp) / "run.json"
            result = run(
                NEW_RUN,
                "--output", target,
                "--mode", "create",
                "--platform", "web",
                "--ui-scope", "checkout",
                "--source", "spreadsheet=/tmp/spec.csv",
            )
            self.assertEqual(result.returncode, 2)
            self.assertFalse(target.exists())


class TestRunValidation(unittest.TestCase):
    def setUp(self):
        with tempfile.TemporaryDirectory() as temp:
            target = pathlib.Path(temp) / "run.json"
            result = run(
                NEW_RUN,
                "--output", target,
                "--mode", "create",
                "--platform", "web",
                "--ui-scope", "checkout",
                "--source", "prd=/tmp/prd.md",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.record = json.loads(target.read_text(encoding="utf-8"))

    def validate_record(self, record):
        with tempfile.TemporaryDirectory() as temp:
            target = pathlib.Path(temp) / "run.json"
            target.write_text(json.dumps(record), encoding="utf-8")
            return run(VALIDATE, target)

    def test_rejects_changed_hierarchy_order(self):
        self.record["hierarchy"][1:3] = reversed(self.record["hierarchy"][1:3])
        result = self.validate_record(self.record)
        self.assertEqual(result.returncode, 1)
        self.assertIn("hierarchy", result.stdout)

    def test_rejects_missing_template_kind(self):
        self.record["template_kinds"].pop()
        result = self.validate_record(self.record)
        self.assertEqual(result.returncode, 1)
        self.assertIn("template_kinds", result.stdout)

    def test_rejects_unguarded_mutation(self):
        self.record["mutations"].append({
            "effect": "repository_write",
            "target": "/workspace/src/Button.figma.ts",
            "authorization_id": "",
            "readback": "",
            "status": "executed",
        })
        result = self.validate_record(self.record)
        self.assertEqual(result.returncode, 1)
        self.assertIn("authorization_id", result.stdout)
        self.assertIn("readback", result.stdout)

    def test_rejects_unpropagated_stale_dependency(self):
        self.record["lineage"] = [
            {"id": "token.color", "level": "dtcg-tokens", "status": "stale", "depends_on": []},
            {"id": "atom.button", "level": "atoms", "status": "pass", "depends_on": ["token.color"]},
        ]
        result = self.validate_record(self.record)
        self.assertEqual(result.returncode, 1)
        self.assertIn("stale dependency", result.stdout)

    def test_integrated_pass_rejects_missing_requirement_and_quality_evidence(self):
        self.record["completion"] = "pass"
        self.record["capabilities"] = [{"role": "figma.visual.read", "disposition": "use"}]
        result = self.validate_record(self.record)
        self.assertEqual(result.returncode, 1)
        self.assertIn("requirements", result.stdout)
        self.assertIn("quality_evidence", result.stdout)

    def test_integrated_pass_rejects_missing_property_parity_and_governance(self):
        self.record["completion"] = "pass"
        self.record["requirements"] = [{
            "id": "REQ-001", "request": "Map the component API", "owner": "component",
            "disposition": "use", "status": "pass", "evidence": ["current proof"],
            "invalidated_by": [],
        }]
        self.record["quality_evidence"] = {
            "token": {"status": "pass", "freshness": "current", "scope": "token_and_proof_only", "evidence": ["current token"]},
            "design": {
                "status": "pass", "diagnosis": "PASS", "freshness": "current",
                "checkpoint": "integrated",
                "vision_owner": "same invoking strong vision-capable executor",
                "whole_view_evidence": ["whole"], "detail_evidence": ["detail"],
                "responsive_evidence": ["responsive"], "input_path_evidence": ["input"],
                "gates": [{"id": gate_id, "status": "pass", "evidence": ["current"]} for gate_id in [
                    "truth", "access", "task", "perception", "familiarity",
                    "standards", "uniqueness", "craft", "resilience",
                ]],
            },
        }
        result = self.validate_record(self.record)
        self.assertEqual(result.returncode, 1)
        self.assertIn("property_parity", result.stdout)
        self.assertIn("governance", result.stdout)

    def test_integrated_pass_accepts_current_noncompensating_proof(self):
        self.record["completion"] = "pass"
        self.record["capabilities"] = [{"role": "figma.visual.read", "disposition": "use"}]
        for stage in self.record["stages"]:
            stage["status"] = "pass"
            stage["proof"] = ["current proof"]
        self.record["lineage"] = [{
            "id": "component-1", "level": "atoms", "status": "pass",
            "depends_on": [], "proof": ["current proof"],
        }]
        self.record["requirements"] = [{
            "id": "REQ-001", "request": "Map the component API", "owner": "component",
            "disposition": "use", "status": "pass", "evidence": ["current proof"],
            "invalidated_by": [],
        }]
        self.record["quality_evidence"] = quality_evidence()
        kinds = ["TEXT", "BOOLEAN", "VARIANT", "INSTANCE_SWAP", "SLOT", "NESTED_CONNECTED"]
        self.record["property_kind_dispositions"] = [{
            "kind": kind, "disposition": "use", "reason": "The inspected system uses it.",
            "evidence": ["current inventory"],
        } for kind in kinds]
        self.record["property_parity"] = property_proof(kinds)
        self.record["governance"] = governance_proof()
        self.record["comparison_inventory"], self.record["controlled_comparisons"] = comparison_proof()
        rules = json.loads((SKILL_DIR / "assets" / "run-contract.json").read_text())
        self.record["figma_app_audit"] = figma_audit_proof(rules)
        contexts = render_context_proof()
        self.record["render_context_inventory"], self.record["render_context_proof"] = contexts
        result = self.validate_record(self.record)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
