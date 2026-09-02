"""Check one changed design pair."""

FIXED_CONDITIONS = [
    "specimen", "content", "state", "viewport", "input_path",
    "all_non_tested_tokens",
]
ACTION_LAYERS = {
    "state_judgment": {"states", "flows"},
    "atom_judgment": {"atoms"},
    "part_design": {"molecules", "organisms"},
    "screen_design": {"design-composition-templates", "screens", "flows"},
    "motion_judgment": {"transitions"},
}


def check_experiment_link(entry, option_ids, action, problems):
    linked = entry.get("exploration_option_ids", [])
    experiment = entry.get("experiment", {})
    needed = ["id", "hypothesis", "null_hypothesis", "measure", "falsifier"]
    if not linked or any(item not in option_ids for item in linked):
        problems.append(f"{action} experiment link needs exploration options")
    if any(not experiment.get(field) for field in needed):
        problems.append(f"{action} experiment link needs frozen decision fields")
    if experiment.get("frozen_before_view") is not True:
        problems.append(f"{action} experiment link must be frozen before view")
    if experiment.get("status") != "run":
        problems.append(f"{action} experiment must run before retention")


def check_decision_lock(entry, action, problems):
    lock = entry.get("decision_lock", {})
    if lock.get("status") != "accepted_locked":
        problems.append(f"{action} decision must be accepted and locked")
    if lock.get("canonical_creation_after_experiment") is not True:
        problems.append(f"{action} canonical creation must follow experiment")
    if lock.get("decision_owner") != "direct_current_vision":
        problems.append(f"{action} direct current vision must own the decision")
    if not lock.get("lower_owner_locks"):
        problems.append(f"{action} lower owner locks are required")


def check_entry(entry, action, allowed, option_ids, problems):
    if entry.get("layer") not in allowed:
        problems.append(f"{action} pair layer")
    if not entry.get("target_id") or not entry.get("changed_factor"):
        problems.append(f"{action} pair id")
    if entry.get("one_factor_only") is not True:
        problems.append(f"{action} one change")
    if entry.get("fixed_conditions") != FIXED_CONDITIONS:
        problems.append(f"{action} fixed pair facts")
    if not entry.get("a_evidence") or not entry.get("b_evidence"):
        problems.append(f"{action} A and B views")
    if entry.get("a_evidence") == entry.get("b_evidence"):
        problems.append(f"{action} different A and B views")
    vision = entry.get("vision", {})
    if (vision.get("status"), vision.get("freshness")) != ("PASS", "current"):
        problems.append(f"{action} fresh vision")
    if not vision.get("evidence") or not entry.get("decision") or not entry.get("reason"):
        problems.append(f"{action} pair choice")
    check_experiment_link(entry, option_ids, action, problems)
    check_decision_lock(entry, action, problems)


def valid_controlled_comparisons(record, action):
    if action not in ACTION_LAYERS:
        return []
    entries = record.get("controlled_comparisons")
    if not isinstance(entries, list) or not entries:
        return [f"{action} design pair"]
    problems = []
    option_ids = {item.get("id") for item in record.get("options", [])
                  if isinstance(item, dict) and item.get("id")}
    ids = [item.get("target_id") for item in entries if isinstance(item, dict)]
    if len(ids) != len(set(ids)) or not all(ids):
        problems.append(f"{action} unique pair ids")
    for entry in entries:
        check_entry(entry, action, ACTION_LAYERS[action], option_ids, problems)
    return sorted(set(problems))
