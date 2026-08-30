"""Basic run checks."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = SKILL_DIR / "scripts" / "run_pipeline.py"
INTAKE = SKILL_DIR / "evals" / "files" / "valid-intake.json"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True, timeout=120)


class TestRunPipeline(unittest.TestCase):
    def test_start_is_safe_to_run_twice(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = run("start", "--intake", INTAKE, "--run-dir", tmp)
            second = run("start", "--intake", INTAKE, "--run-dir", tmp)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)

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

    def test_packet_is_built_for_one_known_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            start = run("start", "--intake", INTAKE, "--run-dir", tmp)
            packet = run("packet", "--run-dir", tmp,
                         "--action", "source_meaning")
            saved = pathlib.Path(tmp) / "packets" / "source_meaning.json"
            data = json.loads(saved.read_text(encoding="utf-8"))
        self.assertEqual(start.returncode, 0, start.stderr)
        self.assertEqual(packet.returncode, 0, packet.stderr)
        self.assertEqual(data["action"], "source_meaning")

    def test_packet_contains_the_full_context_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            result = run("packet", "--run-dir", tmp,
                         "--action", "source_meaning")
            saved = pathlib.Path(tmp) / "packets" / "source_meaning.json"
            data = json.loads(saved.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("context_bundle", data)
        bundle = data["context_bundle"]
        self.assertEqual(set(bundle["support"]),
                         {"references", "scripts", "assets", "examples", "evals"})
        self.assertTrue(bundle["required_paths"])
        self.assertTrue(bundle["do_not_substitute"])

    def test_record_requires_context_acknowledgement(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            run("packet", "--run-dir", tmp, "--action", "source_meaning")
            path = pathlib.Path(tmp) / "source-result.json"
            path.write_text(json.dumps({
                "action": "source_meaning", "decision": "PASS",
                "evidence": ["source:1"], "reason": "The source is current.",
                "counterevidence": [], "uncertainty": "None found.",
                "affected": [], "missing_context": []
            }), encoding="utf-8")
            result = run("record", "--run-dir", tmp, "--result", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("context acknowledgement", result.stderr)

    def test_record_accepts_every_required_context_path(self):
        fixture = SKILL_DIR / "evals" / "files" / "valid-context-record.json"
        self.assertTrue(fixture.is_file(), "missing valid context fixture")
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            run("packet", "--run-dir", tmp, "--action", "source_meaning")
            result = run("record", "--run-dir", tmp, "--result", fixture)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_record_accepts_named_missing_context_only_when_blocked(self):
        fixture = SKILL_DIR / "evals" / "files" / "missing-context-record.json"
        self.assertTrue(fixture.is_file(), "missing blocked context fixture")
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            run("packet", "--run-dir", tmp, "--action", "source_meaning")
            result = run("record", "--run-dir", tmp, "--result", fixture)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_record_rejects_a_path_as_both_used_and_missing(self):
        fixture = SKILL_DIR / "evals" / "files" / "valid-context-record.json"
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            run("packet", "--run-dir", tmp, "--action", "source_meaning")
            data = json.loads(fixture.read_text(encoding="utf-8"))
            data["decision"] = "BLOCKED"
            data["missing_context"] = [data["context_acknowledgements"][0]]
            path = pathlib.Path(tmp) / "overlap.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = run("record", "--run-dir", tmp, "--result", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("both used and missing", result.stderr)

    def test_record_rejects_an_unrouted_context_path(self):
        fixture = SKILL_DIR / "evals" / "files" / "valid-context-record.json"
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            run("packet", "--run-dir", tmp, "--action", "source_meaning")
            data = json.loads(fixture.read_text(encoding="utf-8"))
            data["context_acknowledgements"].append("references/unrouted.md")
            path = pathlib.Path(tmp) / "unrouted.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            result = run("record", "--run-dir", tmp, "--result", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unrouted context path", result.stderr)

    def test_packet_can_name_one_view(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            result = run("packet", "--run-dir", tmp,
                         "--action", "visual_review", "--item-id", "narrow-error")
            saved = pathlib.Path(tmp) / "packets" / "visual_review--narrow-error.json"
            data = json.loads(saved.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(data["item_id"], "narrow-error")
        self.assertEqual(data["output_schema"], "assets/review-record.schema.json")

    def test_visual_review_packet_names_model_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            result = run("packet", "--run-dir", tmp,
                         "--action", "visual_review")
            saved = pathlib.Path(tmp) / "packets" / "visual_review.json"
            data = json.loads(saved.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(data["review_owner"], "model")
        self.assertEqual(data["review_checklist"], "review-checklist.json")

    def test_creative_packet_primes_open_exploration(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            result = run("packet", "--run-dir", tmp,
                         "--action", "screen_design")
            saved = pathlib.Path(tmp) / "packets" / "screen_design.json"
            data = json.loads(saved.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        contract = data["exploration_contract"]
        self.assertEqual(contract["option_owner"], "model")
        self.assertEqual(contract["choice_owner"], "model")
        self.assertGreaterEqual(len(contract["required_directions"]), 4)
        self.assertIsNone(contract["maximum_options"])
        self.assertTrue(contract["may_add_directions"])
        self.assertTrue(contract["may_combine_directions"])
        self.assertTrue(contract["constraints_are_vetoes"])
        self.assertGreaterEqual(len(contract["exploration_axes"]), 10)
        paths = {item["path"] for item in data["judgment_context"]}
        for path in ["run.json", "state-matrix.json", "source-queue.json",
                     "review-checklist.json", "dependency-manifest.json"]:
            self.assertIn(path, paths)

    def test_creative_record_blocks_a_choice_without_options(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            run("packet", "--run-dir", tmp, "--action", "screen_design")
            path = pathlib.Path(tmp) / "screen-result.json"
            path.write_text(json.dumps({
                "action": "screen_design", "decision": "PASS",
                "evidence": ["render:1"], "reason": "The view fits.",
                "counterevidence": [], "uncertainty": "No doubt shown.",
                "affected": []
            }), encoding="utf-8")
            result = run("record", "--run-dir", tmp, "--result", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("four design options", result.stderr)
        self.assertIn("model choice", result.stderr)


if __name__ == "__main__":
    unittest.main()
