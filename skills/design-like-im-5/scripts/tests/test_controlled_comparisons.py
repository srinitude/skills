import copy
import unittest


FIXED = [
    "specimen", "content", "state", "viewport", "input_path",
    "all_non_tested_tokens",
]


def experiment():
    return {
        "id": "experiment:button-weight",
        "hypothesis": "The new weight will make the main act easier to find.",
        "null_hypothesis": "The new weight will not aid the main act.",
        "measure": "Current eye, brain, and touch review.",
        "falsifier": "The new weight harms use, access, or product fit.",
        "frozen_before_view": True,
        "status": "run",
    }


def comparison(layer):
    return {
        "target_id": "button.primary",
        "layer": layer,
        "exploration_option_ids": ["option-1"],
        "experiment": experiment(),
        "changed_factor": "visual-weight",
        "one_factor_only": True,
        "fixed_conditions": FIXED,
        "a_evidence": "render:button:a",
        "b_evidence": "render:button:b",
        "vision": {
            "status": "PASS", "freshness": "current",
            "evidence": ["vision:button-pair"],
        },
        "decision": "A",
        "reason": "This weight makes the main act clear.",
        "decision_lock": {
            "status": "accepted_locked",
            "canonical_creation_after_experiment": True,
            "decision_owner": "direct_current_vision",
            "lower_owner_locks": ["tokens"],
        },
    }


def record(layer="atoms"):
    return {"options": [{"id": "option-1"}],
            "controlled_comparisons": [comparison(layer)]}


class ControlledComparisonTests(unittest.TestCase):
    def test_atom_record_accepts_one_current_pair(self):
        from lib.controlled_comparisons import valid_controlled_comparisons

        self.assertEqual(
            valid_controlled_comparisons(record(), "atom_judgment"), [])

    def test_missing_pair_blocks_a_design_layer_item(self):
        from lib.controlled_comparisons import valid_controlled_comparisons

        self.assertIn(
            "atom_judgment design pair",
            valid_controlled_comparisons({}, "atom_judgment"),
        )

    def test_multi_factor_or_stale_pair_blocks_acceptance(self):
        from lib.controlled_comparisons import valid_controlled_comparisons

        multi = record()
        multi["controlled_comparisons"][0]["one_factor_only"] = False
        stale = copy.deepcopy(record())
        stale["controlled_comparisons"][0]["vision"]["freshness"] = "stale"
        self.assertTrue(valid_controlled_comparisons(multi, "atom_judgment"))
        self.assertTrue(valid_controlled_comparisons(stale, "atom_judgment"))

    def test_wrong_layer_blocks_the_action(self):
        from lib.controlled_comparisons import valid_controlled_comparisons

        errors = valid_controlled_comparisons(record("screens"), "atom_judgment")
        self.assertIn("atom_judgment pair layer", errors)

    def test_pair_needs_an_exploration_and_frozen_experiment_link(self):
        from lib.controlled_comparisons import valid_controlled_comparisons

        missing = record()
        missing["controlled_comparisons"][0].pop("exploration_option_ids")
        errors = valid_controlled_comparisons(missing, "atom_judgment")
        self.assertTrue(any("experiment link" in item for item in errors))

    def test_unrun_experiment_or_missing_lower_lock_blocks_retention(self):
        from lib.controlled_comparisons import valid_controlled_comparisons

        pending = record()
        pending["controlled_comparisons"][0]["experiment"]["status"] = "registered"
        self.assertTrue(any("run before retention" in item for item in
                            valid_controlled_comparisons(pending, "atom_judgment")))
        unlocked = record()
        unlocked["controlled_comparisons"][0]["decision_lock"]["lower_owner_locks"] = []
        self.assertTrue(any("lower owner locks" in item for item in
                            valid_controlled_comparisons(unlocked, "atom_judgment")))


if __name__ == "__main__":
    unittest.main()
