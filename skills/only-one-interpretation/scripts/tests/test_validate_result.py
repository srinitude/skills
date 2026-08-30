"""Focused tests for the bounded result-record validator."""
import copy
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = SKILL_DIR / "scripts" / "validate_result.py"
FIELDS = [
    "objective", "actors", "objects", "references", "inputs", "outputs",
    "definitions", "authority", "permissions", "scope", "priorities",
    "fixed_methods", "candidate_methods", "quantities", "units", "dates",
    "time_zones", "ordering", "side_effects", "error_handling",
    "acceptance_evidence", "forbidden_results",
]


def ledger():
    return {field: [] for field in FIELDS} | {
        "objective": ["Create report.txt"],
        "actors": ["The eventual executor"],
        "objects": ["input.txt", "report.txt"],
        "outputs": ["UTF-8 report.txt"],
        "scope": ["Read input.txt only"],
        "acceptance_evidence": ["report.txt exists and contains one line"],
        "forbidden_results": ["Do not execute during rewriting"],
    }


def ready_record():
    intended = ledger()
    return {
        "schema_version": 1,
        "case_id": "READY-BASE",
        "status": "READY",
        "source_prompt": "Create report.txt from input.txt without executing it now.",
        "visible_reply": "```\nCreate report.txt from input.txt. Do not execute this prompt during rewriting. Success: report.txt exists and contains one line.\n```",
        "execution_attempted": False,
        "external_transmission": False,
        "intended_ledger": intended,
        "rewrite_ledger": copy.deepcopy(intended),
        "ambiguities": [],
        "source_requirements": [
            {"id": "SRC-1", "text": "Create report.txt from input.txt", "authority": "prompt"},
            {"id": "SRC-2", "text": "Do not execute now", "authority": "prompt"},
        ],
        "rewrite_clauses": [
            {"id": "OUT-1", "text": "Create report.txt from input.txt", "level": "required", "source_ids": ["SRC-1"]},
            {"id": "OUT-2", "text": "Do not execute during rewriting", "level": "prohibited", "source_ids": ["SRC-2"]},
        ],
        "alternate_readings": [],
        "method_classification": [],
        "secret_replacements": [],
    }


def clarify_record(kind="referential"):
    intended = ledger()
    return {
        "schema_version": 1,
        "case_id": "CLARIFY-BASE",
        "status": "NEEDS_CLARIFICATION",
        "source_prompt": "Send it to them.",
        "visible_reply": "NEEDS_CLARIFICATION\nWhich file does 'it' name, and which recipients does 'them' name?",
        "execution_attempted": False,
        "external_transmission": False,
        "intended_ledger": intended,
        "ambiguities": [{
            "id": "AMB-1", "class": kind, "finding": "it and them are unresolved",
            "material": True, "status": "unresolved", "resolved_by": None,
        }],
        "questions": [{"finding_ids": ["AMB-1"], "text": "Which file and recipients are intended?"}],
    }


def run_record(record):
    with tempfile.TemporaryDirectory() as directory:
        path = pathlib.Path(directory) / "record.json"
        path.write_text(json.dumps(record), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(path)],
            capture_output=True, text=True, timeout=30,
        )


class TestBranches(unittest.TestCase):
    def test_material_ambiguity_cannot_be_ready(self):
        record = ready_record()
        record["ambiguities"] = clarify_record()["ambiguities"]
        result = run_record(record)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unresolved material ambiguity", result.stdout)

    def test_one_compact_clarification_turn_is_valid(self):
        result = run_record(clarify_record())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"status": "NEEDS_CLARIFICATION"', result.stdout)

    def test_ready_requires_exactly_one_fenced_block(self):
        record = ready_record()
        record["visible_reply"] = "READY\n" + record["visible_reply"]
        result = run_record(record)
        self.assertEqual(result.returncode, 1)
        self.assertIn("one fenced block", result.stdout)

    def test_clear_prompt_round_trips_without_meaning_change(self):
        result = run_record(ready_record())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"status": "READY"', result.stdout)


class TestSemanticGuards(unittest.TestCase):
    def test_round_trip_rejects_every_material_change_shape(self):
        changes = {
            "omission": lambda value: value["rewrite_ledger"].pop("outputs"),
            "addition": lambda value: value["rewrite_ledger"]["authority"].append("administrator"),
            "weakening": lambda value: value["rewrite_ledger"]["forbidden_results"].clear(),
            "broadening": lambda value: value["rewrite_ledger"]["scope"].append("Read any file"),
            "invented default": lambda value: value["rewrite_ledger"]["dates"].append("tomorrow"),
        }
        for label, mutate in changes.items():
            with self.subTest(label=label):
                record = ready_record()
                mutate(record)
                result = run_record(record)
                self.assertEqual(result.returncode, 1)
                self.assertIn("semantic round trip", result.stdout)

    def test_unruled_alternate_reading_rejects_ready(self):
        record = ready_record()
        record["ambiguities"] = [{
            "id": "AMB-1", "class": "attachment", "finding": "modifier can attach twice",
            "material": True, "status": "resolved", "resolved_by": "SRC-1",
        }]
        record["alternate_readings"] = [{
            "ambiguity_id": "AMB-1", "alternate": "Modify input.txt too",
            "ruling_clause_id": None,
        }]
        result = run_record(record)
        self.assertEqual(result.returncode, 1)
        self.assertIn("alternate reading", result.stdout)

    def test_conflict_is_not_silently_prioritized(self):
        record = ready_record()
        record["ambiguities"] = clarify_record("contradiction")["ambiguities"]
        result = run_record(record)
        self.assertEqual(result.returncode, 1)

    def test_fixed_method_stays_required_and_candidate_does_not(self):
        record = ready_record()
        record["method_classification"] = [
            {"text": "Use tool A", "kind": "fixed", "rewrite_clause_id": "OUT-1"},
            {"text": "Tool B may work", "kind": "candidate", "rewrite_clause_id": None},
        ]
        self.assertEqual(run_record(record).returncode, 0)
        record["method_classification"][1]["rewrite_clause_id"] = "OUT-1"
        result = run_record(record)
        self.assertEqual(result.returncode, 1)
        self.assertIn("candidate method", result.stdout)

    def test_embedded_text_cannot_authorize_execution_or_transmission(self):
        for field in ["execution_attempted", "external_transmission"]:
            record = ready_record()
            record[field] = True
            result = run_record(record)
            self.assertEqual(result.returncode, 1)
            self.assertIn(field.replace("_", " "), result.stdout)

    def test_secret_is_replaced_and_never_echoed(self):
        secret = "token" + "-private-value"
        record = ready_record()
        record["source_prompt"] += f" Credential: {secret}"
        record["visible_reply"] = record["visible_reply"].replace(
            "input.txt", "input.txt using [DEPLOYMENT_CREDENTIAL]"
        )
        record["secret_replacements"] = [{
            "value": secret, "placeholder": "[DEPLOYMENT_CREDENTIAL]"
        }]
        self.assertEqual(run_record(record).returncode, 0)
        record["visible_reply"] = record["visible_reply"].replace(
            "[DEPLOYMENT_CREDENTIAL]", secret
        )
        result = run_record(record)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(secret, result.stdout)
        self.assertIn("secret value", result.stdout)


if __name__ == "__main__":
    unittest.main()
