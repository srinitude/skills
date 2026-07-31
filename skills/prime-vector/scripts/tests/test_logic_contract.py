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

    def test_behavior_claims_use_the_local_proof_contract(self):
        text = read_skill()
        shipped_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in SKILL_DIR.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        )
        for removed_companion in ["would-" + "humans-actually", "would-" + "agents-actually"]:
            self.assertNotIn(removed_companion, shipped_text)
        self.assertIn("For a human-action claim", text)
        self.assertIn("eligible population", text)
        self.assertIn("observed target action", text)
        self.assertIn("For an automated-action claim", text)
        self.assertIn("exact system", text)
        self.assertIn("representative task set", text)
        self.assertIn("external state readback", text)
        self.assertIn("Keep the verdict `UNVALIDATED`", text)


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
    def test_video_source_and_every_learning_cluster_are_bound(self):
        video = read_json("video-learning-map.json")
        self.assertEqual(
            video["video"]["transcript_full_text_sha256"],
            "2ed6f87c5342ffd8ee1cee9cebbd7f6491b61d39acee301ca6e513947ae43ce3",
        )
        self.assertEqual(len(video["learnings"]), 25)
        self.assertEqual(set(video["candidate_map"]), {item["id"] for item in video["learnings"]})
        self.assertNotIn("missing", set(video["candidate_map"].values()))
        self.assertTrue(all(item["timestamps"] for item in video["learnings"]))

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
    def test_case_taxonomy_declares_every_used_value(self):
        data = read_json("cases.json")
        self.assertTrue(all(item["group"] in data["groups"] for item in data["cases"]))
        self.assertTrue(
            all(item["decision"] in data["decision_labels"] for item in data["cases"])
        )

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
