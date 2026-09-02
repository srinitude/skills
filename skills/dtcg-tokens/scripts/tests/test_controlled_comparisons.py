import copy
import unittest


FIXED = [
    "specimen", "content", "state", "viewport", "input_path",
    "all_non_tested_tokens",
]
RELATIONSHIPS = [
    "related-item", "inset", "group", "section", "shell",
    "wide-aperture", "part-weight",
]


def pair(target, value_a, value_b, role="primitive"):
    return {
        "target": target,
        "role": role,
        "experiment_id": f"experiment:{target}",
        "changed_factor": target,
        "one_factor_only": True,
        "change_scale": "material_direction",
        "material_effect": "Changes hierarchy, task effort, meaning, or behavior at whole-view scale.",
        "micro_optimization": False,
        "threshold_exception": None,
        "fixed_conditions": FIXED,
        "a": {"value": value_a, "evidence": f"render:{target}:a"},
        "b": {"value": value_b, "evidence": f"render:{target}:b"},
        "vision": {
            "status": "pass", "freshness": "current",
            "evidence": [f"vision:{target}"],
        },
    }


def valid_inputs():
    tokens = {
        "primitive": {
            "color": {"ink": {"$type": "color", "$value": "#111111"}},
            "space": {"small": {"$type": "dimension", "$value": "8px"}},
        },
        "semantic": {"text": {"$type": "color", "$ref": "{primitive.color.ink}"}},
    }
    entries = [
        pair("primitive.color.ink", "#111111", "#222222"),
        pair("primitive.space.small", "8px", "10px"),
    ]
    relationships = [pair(role, "current", "candidate", role) for role in RELATIONSHIPS]
    evidence = {"controlled_comparisons": comparison_record(entries, relationships)}
    return tokens, evidence


def comparison_record(entries, relationships):
    all_pairs = entries + relationships
    return {
        "classification": "controlled_visual_comparison",
        "not_live_user_ab_test": True,
        "exploration_candidates": [{"id": f"candidate:{item['target']}"}
                                   for item in all_pairs],
        "experiments": [{
            "id": item["experiment_id"],
            "candidate_ids": [f"candidate:{item['target']}"],
            "hypothesis": "The one changed factor will make the owned role clearer.",
            "null_hypothesis": "The one changed factor will not improve the owned role.",
            "measure": "Current vision judgment under fixed conditions.",
            "falsifier": "The pair weakens use, access, or product meaning.",
            "frozen_before_view": True,
            "status": "run",
        } for item in all_pairs],
        "entries": entries,
        "relationship_trials": relationships,
        "token_layer_lock": {
            "status": "accepted_locked",
            "accepted_sequence": [
                "experiment_registered", "candidates_created",
                "experiment_run", "visually_judged", "accepted_locked",
                "canonical_created",
            ],
            "canonical_creation_after_experiments": True,
            "decision_owner": "direct_current_vision",
        },
    }


class ControlledComparisonTests(unittest.TestCase):
    def test_complete_one_factor_comparisons_pass(self):
        from lib.controlled_comparisons import validate_controlled_comparisons

        tokens, evidence = valid_inputs()
        report = validate_controlled_comparisons(tokens, evidence)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["primitive_count"], 2)
        self.assertEqual(report["relationship_count"], 7)

    def test_missing_primitive_pair_blocks_acceptance(self):
        from lib.controlled_comparisons import validate_controlled_comparisons

        tokens, evidence = valid_inputs()
        evidence["controlled_comparisons"]["entries"].pop()
        errors = validate_controlled_comparisons(tokens, evidence)["errors"]
        self.assertIn("primitive comparison coverage mismatch", errors)

    def test_changed_control_or_stale_vision_blocks_acceptance(self):
        from lib.controlled_comparisons import validate_controlled_comparisons

        tokens, evidence = valid_inputs()
        changed = copy.deepcopy(evidence)
        changed["controlled_comparisons"]["entries"][0]["fixed_conditions"].pop()
        stale = copy.deepcopy(evidence)
        stale["controlled_comparisons"]["entries"][0]["vision"]["freshness"] = "stale"
        self.assertTrue(validate_controlled_comparisons(tokens, changed)["errors"])
        self.assertTrue(validate_controlled_comparisons(tokens, stale)["errors"])

    def test_missing_exploration_or_experiment_link_blocks_acceptance(self):
        from lib.controlled_comparisons import validate_controlled_comparisons

        tokens, evidence = valid_inputs()
        evidence["controlled_comparisons"]["experiments"].pop()
        errors = validate_controlled_comparisons(tokens, evidence)["errors"]
        self.assertTrue(any("experiment link" in item for item in errors))

    def test_micro_optimization_without_threshold_evidence_is_rejected(self):
        from lib.controlled_comparisons import validate_controlled_comparisons

        tokens, evidence = valid_inputs()
        item = evidence["controlled_comparisons"]["entries"][0]
        item["change_scale"] = "micro_optimization"
        item["micro_optimization"] = True
        errors = validate_controlled_comparisons(tokens, evidence)["errors"]
        self.assertTrue(any("material change" in error for error in errors))

    def test_unrun_experiment_or_missing_token_lock_blocks_canonical_tokens(self):
        from lib.controlled_comparisons import validate_controlled_comparisons

        tokens, evidence = valid_inputs()
        evidence["controlled_comparisons"]["experiments"][0]["status"] = "registered"
        errors = validate_controlled_comparisons(tokens, evidence)["errors"]
        self.assertTrue(any("must run before canonical tokens" in item for item in errors))
        tokens, evidence = valid_inputs()
        evidence["controlled_comparisons"].pop("token_layer_lock")
        errors = validate_controlled_comparisons(tokens, evidence)["errors"]
        self.assertTrue(any("token layer lock" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
