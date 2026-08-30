"""Check proof ladder rules."""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[2]
CHECKER = SKILL / "scripts" / "check_proof_ladder.py"
RUNG_IDS = [
    "atomic", "mutation", "metamorphic", "judgment_pilot", "combinatorial",
    "representative", "whole_skill",
]
AGREEMENT_FIELDS = [
    "action_order", "context_accounting", "evidence_classes", "vetoes",
    "status",
]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class TestProofLadder(unittest.TestCase):
    def test_ladder_has_ordered_bounded_rungs(self):
        ladder = load(SKILL / "assets" / "proof-ladder.json")
        self.assertEqual(ladder["checked_date"], "2026-08-30")
        self.assertEqual([rung["id"] for rung in ladder["rungs"]], RUNG_IDS)
        for rung in ladder["rungs"]:
            for key in ["owner", "proves", "does_not_prove", "advance_when",
                        "evidence", "mise_task", "support"]:
                self.assertTrue(rung[key], f"{rung['id']} missing {key}")
        self.assertEqual(ladder["rungs"][3]["owner"], "judgment")

    def test_repeatability_compares_invariants_not_copy(self):
        repeatability = load(SKILL / "assets" / "proof-ladder.json")[
            "repeatability"]
        self.assertEqual(repeatability["runs"], 2)
        self.assertTrue(repeatability["clean_context"])
        self.assertTrue(repeatability["same_fixture"])
        self.assertEqual(repeatability["compare"], AGREEMENT_FIELDS)
        self.assertIn("wording", repeatability["allowed_variation"])
        self.assertIn("creative_direction", repeatability["allowed_variation"])
        self.assertEqual(repeatability["disagreement_status"], "STALE")

    def test_pilots_seed_one_fault_and_bound_each_claim(self):
        pilots = load(SKILL / "evals" / "pilot-cases.json")
        self.assertGreaterEqual(len(pilots["cases"]), 5)
        for case in pilots["cases"]:
            for key in ["fault_seed", "expected_detection", "claim_scope",
                        "blocked_claim", "expansion_trigger", "review_records"]:
                self.assertTrue(case[key], f"{case['id']} missing {key}")
            self.assertEqual(len(case["fault_seed"]), 1)
            self.assertEqual(case["repeatability_runs"], 2)
            self.assertEqual(case["agreement_fields"], AGREEMENT_FIELDS)
        self.assertEqual(pilots["coverage"]["strength"], 2)

    def test_checker_rejects_scope_inflation(self):
        self.assertTrue(CHECKER.is_file(), "missing proof-ladder checker")
        good = subprocess.run(
            [sys.executable, str(CHECKER), str(SKILL)],
            capture_output=True, text=True, timeout=120)
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / "skill"
            shutil.copytree(SKILL, copy)
            path = copy / "assets" / "proof-ladder.json"
            data = load(path)
            data["rungs"][0]["does_not_prove"] = []
            path.write_text(json.dumps(data), encoding="utf-8")
            bad = subprocess.run(
                [sys.executable, str(copy / "scripts" / "check_proof_ladder.py"),
                 str(copy)], capture_output=True, text=True, timeout=120)
        self.assertEqual(bad.returncode, 1)
        self.assertIn("does_not_prove", bad.stdout)

    def test_checker_kills_a_changed_rung_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / "skill"
            shutil.copytree(SKILL, copy)
            path = copy / "assets" / "proof-ladder.json"
            data = load(path)
            data["rungs"][0], data["rungs"][1] = (
                data["rungs"][1], data["rungs"][0])
            path.write_text(json.dumps(data), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(copy / "scripts" /
                 "check_proof_ladder.py"), str(copy)],
                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 1)
        self.assertIn("rung order", result.stdout)

    def test_case_order_does_not_change_the_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / "skill"
            shutil.copytree(SKILL, copy)
            path = copy / "evals" / "pilot-cases.json"
            data = load(path)
            data["cases"].reverse()
            path.write_text(json.dumps(data), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(copy / "scripts" /
                 "check_proof_ladder.py"), str(copy)],
                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_checker_rejects_a_lost_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / "skill"
            shutil.copytree(SKILL, copy)
            path = copy / "evals" / "pilot-cases.json"
            data = load(path)
            data["coverage"]["rows"][1]["values"] = dict(
                data["coverage"]["rows"][0]["values"])
            path.write_text(json.dumps(data), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(copy / "scripts" /
                 "check_proof_ladder.py"), str(copy)],
                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 1)
        self.assertIn("pairwise", result.stdout)

    def test_mise_ladder_is_forced_by_complete(self):
        config = tomllib.loads((SKILL / "mise.toml").read_text())
        tasks = config["tasks"]
        self.assertIn("proof-ladder", tasks)
        self.assertIn("proof-ladder", tasks["proof"]["depends"])
        self.assertIn("check_proof_ladder.py", tasks["proof-ladder"]["run"])

    def test_body_routes_the_ladder_through_mise(self):
        body = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for path in ["references/proof-ladder.md", "assets/proof-ladder.json",
                     "examples/proof-ladder.md", "evals/pilot-cases.json"]:
            self.assertIn(path, body)
        self.assertIn("mise run proof-ladder", body)
        self.assertNotIn("check_proof_ladder.py", body)
        phrase_parts = [("less", "capable"), ("more", "capable"),
                        ("model", "capability"), ("weaker", "model"),
                        ("stronger", "model")]
        for phrase in (" ".join(parts) for parts in phrase_parts):
            self.assertNotIn(phrase, body.lower())


if __name__ == "__main__":
    unittest.main()
