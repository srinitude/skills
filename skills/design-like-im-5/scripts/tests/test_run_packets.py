"""Runner packet checks."""
import json
import pathlib
import tempfile
import unittest

from pipeline_test_support import INTAKE, run, set_next


class TestRunPackets(unittest.TestCase):
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
        bundle = data["context_bundle"]
        self.assertEqual(set(bundle["support"]),
                         {"references", "scripts", "assets", "examples", "evals"})
        self.assertTrue(bundle["required_paths"])
        self.assertTrue(bundle["do_not_substitute"])

    def test_packet_blocks_an_action_before_its_turn(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            result = run("packet", "--run-dir", tmp,
                         "--action", "screen_design")
        self.assertEqual(result.returncode, 1)
        self.assertIn("next action is source_meaning", result.stderr)

    def test_packet_can_name_one_view(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            set_next(tmp, "visual_review")
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
            set_next(tmp, "visual_review")
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
            set_next(tmp, "screen_design")
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


if __name__ == "__main__":
    unittest.main()
