"""Check end state and part links."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

from pipeline_test_support import (
    CHECKLIST, INTAKE, LINEAGE, SELECT, SKILL_DIR, passing_record, run)

ACTIONS = [
    "source_meaning", "state_judgment", "atom_judgment", "part_design",
    "screen_design", "motion_judgment", "visual_review", "plain_readback",
]


class TestRunCompletion(unittest.TestCase):
    def test_check_requires_current_lineage_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            data = json.loads((root / "run.json").read_text())
            data["rules_selected"] = True
            data["next"] = "final_check"
            (root / "run.json").write_text(json.dumps(data))
            (root / "records").mkdir()
            for action in ACTIONS:
                (root / "records" / f"{action}.json").write_text(
                    json.dumps({"action": action, "decision": "PASS"}))
            result = run("check", "--run-dir", tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("check_lineage", result.stdout)

    def test_lineage_step_records_proof_and_advances(self):
        lineage = SKILL_DIR / "evals" / "files" / "valid-lineage.json"
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            data = json.loads((root / "run.json").read_text())
            data["next"] = "check_lineage"
            (root / "run.json").write_text(json.dumps(data))
            result = subprocess.run(
                [sys.executable, str(LINEAGE), str(lineage), "--run-dir", tmp],
                capture_output=True, text=True, timeout=120)
            proof = json.loads((root / "lineage-check.json").read_text())
            current = json.loads((root / "run.json").read_text())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(proof["status"], "PASS")
        self.assertEqual(current["next"], "final_check")

    def test_full_fixture_run_cannot_skip_an_ordered_action(self):
        checklist_result = subprocess.run(
            [sys.executable, str(CHECKLIST)], capture_output=True, text=True,
            timeout=120)
        checklist = json.loads(checklist_result.stdout)
        lineage = SKILL_DIR / "evals" / "files" / "valid-lineage.json"
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            results = [run("start", "--intake", INTAKE, "--run-dir", tmp)]
            for action in ACTIONS:
                results.extend(self.run_action(root, tmp, action, checklist))
                if action == "state_judgment":
                    results.append(self.select_rules(tmp))
            lineage_result = subprocess.run(
                [sys.executable, str(LINEAGE), str(lineage), "--run-dir", tmp],
                capture_output=True, text=True, timeout=120)
            final = run("check", "--run-dir", tmp)
            final_data = json.loads(final.stdout)
        for result in [*results, lineage_result, final]:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(final_data["status"], "PASS")

    def run_action(self, root, tmp, action, checklist):
        packet_result = run("packet", "--run-dir", tmp, "--action", action)
        packet = json.loads(
            (root / "packets" / f"{action}.json").read_text())
        result_path = root / f"{action}-result.json"
        result_path.write_text(json.dumps(passing_record(packet, checklist)))
        recorded = run("record", "--run-dir", tmp, "--result", result_path)
        return [packet_result, recorded]

    def select_rules(self, tmp):
        return subprocess.run(
            [sys.executable, str(SELECT), "--run-dir", tmp],
            capture_output=True, text=True, timeout=120)


if __name__ == "__main__":
    unittest.main()
