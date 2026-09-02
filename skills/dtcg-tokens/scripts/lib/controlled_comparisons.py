"""Validate one-factor token and relationship comparison evidence."""

FIXED_CONDITIONS = [
    "specimen", "content", "state", "viewport", "input_path",
    "all_non_tested_tokens",
]
RELATIONSHIP_ROLES = [
    "related-item", "inset", "group", "section", "shell",
    "wide-aperture", "part-weight",
]
THRESHOLD_REASONS = {
    "safety", "accessibility", "legibility", "target_reach",
    "compliance", "platform_geometry",
}
ACCEPTED_SEQUENCE = [
    "experiment_registered", "candidates_created", "experiment_run",
    "visually_judged", "accepted_locked", "canonical_created",
]


def primitive_paths(node, path=()):
    if not isinstance(node, dict):
        return []
    if "$value" in node:
        return [".".join(path)]
    paths = []
    for key, value in node.items():
        if not key.startswith("$"):
            paths.extend(primitive_paths(value, path + (key,)))
    return paths


def check_pair(item, target, errors):
    prefix = f"controlled comparison {target}"
    if item.get("changed_factor") != target:
        errors.append(f"{prefix} must change only its target")
    if item.get("one_factor_only") is not True:
        errors.append(f"{prefix} must be one-factor-only")
    if item.get("fixed_conditions") != FIXED_CONDITIONS:
        errors.append(f"{prefix} fixed conditions mismatch")
    left, right = item.get("a", {}), item.get("b", {})
    if left.get("value") == right.get("value"):
        errors.append(f"{prefix} needs two different values")
    if not left.get("evidence") or not right.get("evidence"):
        errors.append(f"{prefix} needs visible A and B evidence")
    vision = item.get("vision", {})
    if (vision.get("status"), vision.get("freshness")) != ("pass", "current"):
        errors.append(f"{prefix} needs current passing vision")
    if not vision.get("evidence"):
        errors.append(f"{prefix} needs located vision evidence")
    check_materiality(item, prefix, errors)


def check_materiality(item, prefix, errors):
    if not item.get("material_effect"):
        errors.append(f"{prefix} needs a material change effect")
    if item.get("change_scale") == "material_direction" and not item.get("micro_optimization"):
        return
    exception = item.get("threshold_exception")
    if not isinstance(exception, dict):
        errors.append(f"{prefix} needs a material change or proved threshold exception")
        return
    if exception.get("reason") not in THRESHOLD_REASONS:
        errors.append(f"{prefix} threshold reason is invalid")
    if not exception.get("evidence") or exception.get("crosses_required_threshold") is not True:
        errors.append(f"{prefix} threshold exception needs current crossing evidence")


def experiment_index(record, errors):
    candidates = record.get("exploration_candidates", [])
    candidate_ids = [item.get("id") for item in candidates if isinstance(item, dict)]
    experiments = record.get("experiments", [])
    experiment_ids = [item.get("id") for item in experiments if isinstance(item, dict)]
    if not candidate_ids or len(candidate_ids) != len(set(candidate_ids)):
        errors.append("controlled comparisons need unique exploration candidates")
    if not experiment_ids or len(experiment_ids) != len(set(experiment_ids)):
        errors.append("controlled comparisons need unique experiment links")
    return set(candidate_ids), {item.get("id"): item for item in experiments}


def check_experiment_link(item, candidate_ids, experiments, errors):
    where = f"controlled comparison {item.get('target', '<missing>')} experiment link"
    experiment = experiments.get(item.get("experiment_id"), {})
    linked = experiment.get("candidate_ids", [])
    needed = ["hypothesis", "null_hypothesis", "measure", "falsifier"]
    if not linked or any(candidate not in candidate_ids for candidate in linked):
        errors.append(f"{where} needs valid exploration candidates")
    if any(not experiment.get(field) for field in needed):
        errors.append(f"{where} needs frozen decision fields")
    if experiment.get("frozen_before_view") is not True:
        errors.append(f"{where} must be frozen before view")
    if experiment.get("status") != "run":
        errors.append(f"{where} must run before canonical tokens")


def check_token_layer_lock(record, errors):
    lock = record.get("token_layer_lock", {})
    if lock.get("status") != "accepted_locked":
        errors.append("token layer lock must be accepted before canonical tokens")
    if lock.get("accepted_sequence") != ACCEPTED_SEQUENCE:
        errors.append("token layer lock sequence mismatch")
    if lock.get("canonical_creation_after_experiments") is not True:
        errors.append("token layer lock must precede canonical creation")
    if lock.get("decision_owner") != "direct_current_vision":
        errors.append("token layer lock needs current direct vision")


def check_collection(items, expected, errors, label, candidates, experiments):
    targets = [item.get("target") for item in items if isinstance(item, dict)]
    if targets != expected or len(targets) != len(set(targets)):
        errors.append(f"{label} comparison coverage mismatch")
    by_target = {item.get("target"): item for item in items if isinstance(item, dict)}
    for target in expected:
        item = by_target.get(target, {})
        check_pair(item, target, errors)
        check_experiment_link(item, candidates, experiments, errors)


def validate_controlled_comparisons(tokens, evidence):
    errors = []
    record = evidence.get("controlled_comparisons", {})
    if record.get("classification") != "controlled_visual_comparison":
        errors.append("controlled comparisons need the visual-comparison classification")
    if record.get("not_live_user_ab_test") is not True:
        errors.append("controlled comparisons must not claim randomized user causality")
    candidates, experiments = experiment_index(record, errors)
    check_token_layer_lock(record, errors)
    primitives = primitive_paths(tokens)
    check_collection(
        record.get("entries", []), primitives, errors, "primitive",
        candidates, experiments,
    )
    check_collection(
        record.get("relationship_trials", []), RELATIONSHIP_ROLES,
        errors, "relationship", candidates, experiments,
    )
    return {
        "status": "pass" if not errors else "fail", "errors": errors,
        "primitive_count": len(primitives),
        "relationship_count": len(RELATIONSHIP_ROLES),
    }
