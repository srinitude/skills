"""Regression tests for Prime Vector's logic and evidence contracts."""
import hashlib
import json
import pathlib
import re
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
EVAL_DIR = SKILL_DIR / "evals"


def read_json(name):
    return json.loads((EVAL_DIR / name).read_text(encoding="utf-8"))


def read_skill():
    return (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")


class TestRuntimeContract(unittest.TestCase):
    def test_states_and_statuses_are_distinct(self):
        text = read_skill()
        self.assertIn("Workflow states are `FRAME | DRAFT | CHALLENGE | TEST | DECIDE`.", text)
        self.assertIn("Response statuses are `QUESTION | DRAFT | TEST | DONE | BLOCKED`.", text)
        self.assertIn("Remain in `TEST` with status `TEST`", text)
        self.assertNotIn("Exit to `TEST` when evidence is still missing", text)

    def test_decision_requires_criteria_and_comparison(self):
        text = read_skill()
        self.assertIn("decision criteria in precedence order", text)
        self.assertIn("status quo and at least one viable alternative", text)
        self.assertIn("user accepts the named residual uncertainty", text)

    def test_behavior_claims_route_to_evidence_owners(self):
        text = read_skill()
        self.assertIn("`would-humans-actually`", text)
        self.assertIn("`would-agents-actually`", text)
        self.assertIn("representative task set", text)
        self.assertIn("external readback", text)


class TestExecutionContract(unittest.TestCase):
    def test_crit_and_question_limit_are_explicit(self):
        text = read_skill()
        self.assertIn("Context, Role, Interview, Task (CRIT)", text)
        self.assertIn("Keep at most one unanswered material question live", text)
        self.assertIn("Repeat `CHALLENGE` only when new evidence changes the strategy", text)

    def test_scaling_waits_for_observed_acceptance(self):
        text = read_skill()
        self.assertIn("observed manual result", text)
        self.assertIn("accepted target result and exercised failure handling", text)

    def test_examples_do_not_claim_unsupported_work(self):
        simple = (SKILL_DIR / "examples/simple-task-bypass.md").read_text()
        high_stakes = (SKILL_DIR / "examples/high-stakes-decision.md").read_text()
        self.assertIn("BLOCKED", simple)
        self.assertNotIn("Changed the heading", simple)
        self.assertNotIn("Context needed", high_stakes)
        for heading in ["Decision criteria", "Status quo", "Rejected alternative"]:
            self.assertIn(heading, high_stakes)


class TestEvidenceIntegrity(unittest.TestCase):
    def test_candidate_evidence_ids_match_candidate_hash(self):
        data = read_json("centrality-mapping.json")
        candidate = hashlib.sha256((SKILL_DIR / "SKILL.md").read_bytes()).hexdigest()
        self.assertEqual(data["candidate_skill_sha256"], candidate)
        basis = data[data["candidate_evidence_id_basis"]]
        expected = [f"CANDIDATE-SKILL-SHA256-{basis}"]
        retained = [rule for rule in data["baseline_rules"] if rule["action"] != "approved_drop"]
        for rule in retained:
            self.assertEqual(rule["candidate_evidence_ids"], expected)

    def test_lineage_lists_every_shipped_file(self):
        lineage = read_json("source-lineage.json")
        shipped = {
            path.relative_to(SKILL_DIR).as_posix()
            for path in SKILL_DIR.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        listed = {entry["path"] for entry in lineage["public_files"]}
        self.assertEqual(listed, shipped)


class TestDualFormatParity(unittest.TestCase):
    def test_behavior_formats_match(self):
        cases = read_json("cases.json")["cases"]
        portable = read_json("evals.json")["evals"]
        expected = []
        for case in cases:
            assertions = case["required"] + [f"The response does not: {item}" for item in case["veto"]]
            expected.append((case["prompt"], assertions))
        self.assertEqual([(item["prompt"], item["assertions"]) for item in portable], expected)

    def test_trigger_formats_match(self):
        cases = read_json("trigger-cases.json")["cases"]
        portable = read_json("trigger-queries.json")
        expected = [{"query": item["prompt"], "should_trigger": item["should_trigger"]} for item in cases]
        self.assertEqual(portable, expected)

    def test_public_version_is_synchronized(self):
        match = re.search(r"^  version: '([^']+)'$", read_skill(), re.MULTILINE)
        if match is None:
            self.fail("missing metadata.version")
        version = match.group(1)
        self.assertEqual(read_json("manifest.json")["public_version"], version)
        self.assertEqual(read_json("source-lineage.json")["public_version"], version)


if __name__ == "__main__":
    unittest.main()
