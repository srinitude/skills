from lib.controlled_comparisons import (
    ACCEPTED_SEQUENCE, FIXED_CONDITIONS, RELATIONSHIP_ROLES, primitive_paths,
)


def pair(target, value_a, value_b, role="primitive"):
    return {
        "target": target, "role": role,
        "experiment_id": f"experiment:{target}", "changed_factor": target,
        "one_factor_only": True, "fixed_conditions": FIXED_CONDITIONS,
        "change_scale": "material_direction",
        "material_effect": "Changes hierarchy, task effort, meaning, or behavior at whole-view scale.",
        "micro_optimization": False,
        "threshold_exception": None,
        "a": {"value": value_a, "evidence": f"render:{target}:a"},
        "b": {"value": value_b, "evidence": f"render:{target}:b"},
        "vision": {"status": "pass", "freshness": "current",
                   "evidence": [f"vision:{target}"]},
    }


def add_controlled_comparisons(evidence, tokens):
    entries = [pair(path, "current", "candidate")
               for path in primitive_paths(tokens)]
    relationships = [pair(role, "current", "candidate", role)
                     for role in RELATIONSHIP_ROLES]
    pairs = entries + relationships
    evidence["controlled_comparisons"] = {
        "classification": "controlled_visual_comparison",
        "not_live_user_ab_test": True,
        "exploration_candidates": [
            {"id": f"candidate:{item['target']}"} for item in pairs],
        "experiments": [experiment(item) for item in pairs],
        "entries": entries, "relationship_trials": relationships,
        "token_layer_lock": {
            "status": "accepted_locked",
            "accepted_sequence": ACCEPTED_SEQUENCE,
            "canonical_creation_after_experiments": True,
            "decision_owner": "direct_current_vision",
        },
    }
    return evidence


def experiment(item):
    return {
        "id": item["experiment_id"],
        "candidate_ids": [f"candidate:{item['target']}"],
        "hypothesis": "The one change will clarify the owned role.",
        "null_hypothesis": "The one change will not clarify the owned role.",
        "measure": "Current vision judgment under fixed conditions.",
        "falsifier": "The change harms use, access, or product meaning.",
        "frozen_before_view": True,
        "status": "run",
    }
