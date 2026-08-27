"""Pin source identity, runtime delegation, screen space, and vision qualification."""
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]


def load(relative):
    path = SKILL_DIR / relative
    if not path.is_file():
        raise AssertionError(f"missing {relative}")
    return json.loads(path.read_text(encoding="utf-8"))


class IdentityAndOrchestrationTests(unittest.TestCase):
    def test_claims_stay_separate_and_global_uniqueness_is_false(self):
        contract = load("assets/originality-analysis-contract.json")
        expected = {"source_specificity", "source_distinctiveness", "source_originality", "output_originality", "output_identifiability", "corpus_uniqueness", "memorability", "authorship_provenance", "bounded_one_of_a_kind", "globally_unique"}
        self.assertEqual(set(contract["claims"]), expected)
        self.assertFalse(contract["claims"]["globally_unique"]["allowed"])
        for relation in ["spatial", "temporal", "causal", "hierarchical", "rhythmic", "material", "interaction", "crossmodal"]:
            self.assertIn(relation, contract["identity_graph"]["edge_types"])

    def test_runtime_workers_have_typed_packets_and_sequential_fallback(self):
        contract = load("assets/subagent-task-contract.json")
        for field in ["task_id", "role", "objective", "inputs", "input_hashes", "dependencies", "allowed_actions", "forbidden_actions", "output_schema", "evidence", "completion_rule", "status"]:
            self.assertIn(field, contract["task_packet_fields"])
        self.assertEqual(contract["write_policy"], "one_writer_per_mutable_deliverable")
        self.assertTrue(contract["delegate_when_eligible"])
        self.assertEqual(contract["unavailable_fallback"], "run_same_roles_sequentially_with_same_records")
        self.assertTrue(contract["lead_rechecks_current_bytes"])


class ScreenSpaceTests(unittest.TestCase):
    def test_screen_space_covers_human_and_device_axes(self):
        space = load("assets/screen-possibility-space.json")
        for axis in ["surface", "viewport", "render_medium", "composition", "time", "state", "input", "action", "feedback", "body", "environment", "accessibility", "task", "source_intent"]:
            self.assertIn(axis, space["axes"])
        self.assertEqual(set(space["dispositions"]), {"applicable", "not_applicable", "unknown", "extension"})
        self.assertEqual(set(space["invariant_classes"]), {"sight", "perception", "touch", "access", "system"})
        self.assertTrue(space["creative_freedom"]["unfamiliar_structures_allowed"])
        self.assertFalse(space["creative_freedom"]["invariants_choose_aesthetic"])


class VisionProbeTests(unittest.TestCase):
    def test_probe_uses_pixels_regions_negative_controls_and_fail_closed_delegation(self):
        probe = load("assets/vision-probe-manifest.json")
        for family in ["overlap_clipping", "typography", "contrast_perception", "responsive", "interaction", "source_identity", "taste_originality", "hallucination_control"]:
            self.assertIn(family, probe["families"])
        self.assertEqual(probe["pass_rule"]["hard_veto_recall"], 1.0)
        self.assertGreaterEqual(probe["pass_rule"]["major_defect_recall"], 0.9)
        self.assertEqual(probe["pass_rule"]["invented_elements"], 0)
        self.assertTrue(probe["requires_actual_pixels"])
        self.assertTrue(probe["requires_region_ids"])
        pair_path = probe.get("fixture_pairs")
        self.assertTrue(pair_path, "vision probe needs bounded negative/countercondition pairs")
        pairs = load(pair_path)
        self.assertGreaterEqual(len(pairs["pairs"]), 5)
        for pair in pairs["pairs"]:
            for field in ["id", "negative_fixture", "region_id", "probe_family", "expected_failure", "pass_countercondition"]:
                self.assertTrue(pair.get(field), f"{pair.get('id')} missing {field}")
        self.assertEqual(probe["failure"], "BLOCKED: E_VISION")
        self.assertTrue(probe["delegate_all_judgment_when_active_path_fails"])


if __name__ == "__main__":
    unittest.main()
