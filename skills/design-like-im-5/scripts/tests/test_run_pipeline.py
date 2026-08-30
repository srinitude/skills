"""Check how a run starts."""
import json
import pathlib
import tempfile
import unittest

from pipeline_test_support import INTAKE, SKILL_DIR, run


class TestRunStart(unittest.TestCase):
    def test_start_is_safe_to_run_twice(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = run("start", "--intake", INTAKE, "--run-dir", tmp)
            second = run("start", "--intake", INTAKE, "--run-dir", tmp)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)

    def test_start_does_not_reset_an_existing_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            data = json.loads((root / "run.json").read_text())
            data["next"] = "state_judgment"
            (root / "run.json").write_text(json.dumps(data))
            result = run("start", "--intake", INTAKE, "--run-dir", tmp)
            current = json.loads((root / "run.json").read_text())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(current["next"], "state_judgment")

    def test_start_blocks_a_different_intake_in_the_same_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            data = json.loads(INTAKE.read_text())
            data["audience"] = "People who own an account and came back."
            changed = root / "changed-intake.json"
            changed.write_text(json.dumps(data))
            result = run("start", "--intake", changed, "--run-dir", tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("different intake", result.stderr)

    def test_start_blocks_a_missing_field(self):
        bad = SKILL_DIR / "evals" / "files" / "missing-proof.json"
        with tempfile.TemporaryDirectory() as tmp:
            result = run("start", "--intake", bad, "--run-dir", tmp)
        self.assertEqual(result.returncode, 1)
        self.assertIn("proof_threshold", result.stderr)

    def test_start_writes_the_full_scaffold(self):
        names = {"capabilities.json", "source-queue.json",
                 "retrieval-manifest.json", "render-plan.json",
                 "viewport-matrix.json", "state-matrix.json",
                 "review-checklist.json", "dependency-manifest.json",
                 "dtcg-route.json", "rebuild-queue.json", "run-log.json"}
        with tempfile.TemporaryDirectory() as tmp:
            result = run("start", "--intake", INTAKE, "--run-dir", tmp)
            made = {path.name for path in pathlib.Path(tmp).glob("*")}
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(names <= made)

    def test_start_freezes_the_context_route_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run("start", "--intake", INTAKE, "--run-dir", tmp)
            data = json.loads((pathlib.Path(tmp) / "run.json").read_text())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("context_routing_sha256", data)
        self.assertRegex(data["context_routing_sha256"], r"^[0-9a-f]{64}$")

    def test_start_leaves_rule_selection_for_its_ordered_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run("start", "--intake", INTAKE, "--run-dir", tmp)
            data = json.loads((pathlib.Path(tmp) / "run.json").read_text())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(data["rules_selected"])
        self.assertTrue(data["rules"])


if __name__ == "__main__":
    unittest.main()
