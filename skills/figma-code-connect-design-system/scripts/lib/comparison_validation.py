"""Validate exhaustive current material design-system comparisons."""


def check_entry(item, contract, problems):
    where = f"controlled comparison {item.get('id', '<missing>')}"
    if item.get("level") not in contract["comparison_levels"]:
        problems.append(f"{where} has an invalid level")
    if not item.get("changed_factor") or item.get("one_factor_only") is not True:
        problems.append(f"{where} must change one named factor")
    if item.get("fixed_conditions") != contract["comparison_fixed_conditions"]:
        problems.append(f"{where} fixed conditions mismatch")
    left, right = item.get("a_evidence"), item.get("b_evidence")
    if not left or not right or left == right:
        problems.append(f"{where} needs distinct A and B evidence")
    vision = item.get("vision", {})
    if (vision.get("status"), vision.get("freshness")) != ("pass", "current"):
        problems.append(f"{where} needs current vision")
    if not vision.get("evidence") or item.get("status") != "pass":
        problems.append(f"{where} needs current passing evidence")
    if any(not item.get(field) for field in contract["comparison_required_links"]):
        problems.append(f"{where} needs an experiment link and exploration sources")
    check_materiality(item, contract, where, problems)
    check_decision_lock(item, where, problems)


def check_decision_lock(item, where, problems):
    if item.get("experiment_status") != "run":
        problems.append(f"{where} must run before canonical creation")
    lock = item.get("decision_lock", {})
    expected = ("accepted_locked", True, "direct_current_vision")
    actual = (lock.get("status"), lock.get("canonical_creation_after_experiment"),
              lock.get("decision_owner"))
    if actual != expected:
        problems.append(f"{where} needs an accepted layer lock")
    if item.get("level") != "dtcg-tokens" and not lock.get("lower_owner_locks"):
        problems.append(f"{where} needs a lower owner lock")


def check_materiality(item, contract, where, problems):
    if not item.get("material_effect"):
        problems.append(f"{where} needs a material change effect")
    expected = contract["comparison_change_scale"]
    if item.get("change_scale") == expected and not item.get("micro_optimization"):
        return
    exception = item.get("threshold_exception")
    if not isinstance(exception, dict):
        problems.append(f"{where} needs a material change or proved threshold exception")
        return
    if exception.get("reason") not in contract["comparison_threshold_reasons"]:
        problems.append(f"{where} threshold reason is invalid")
    if not exception.get("evidence") or exception.get("crosses_required_threshold") is not True:
        problems.append(f"{where} threshold exception needs current crossing evidence")


def check_controlled_comparisons(record, contract, problems):
    inventory = record.get("comparison_inventory", [])
    comparison = record.get("controlled_comparisons", {})
    entries = comparison.get("entries", [])
    if not inventory and not entries:
        if record.get("completion") == "pass":
            problems.append("completion pass requires controlled comparisons")
        return
    if comparison.get("classification") != "controlled_visual_comparison":
        problems.append("controlled comparisons need the visual-comparison classification")
    if comparison.get("not_live_user_ab_test") is not True:
        problems.append("controlled comparisons cannot claim randomized user causality")
    inventory_ids = [item.get("id") for item in inventory if isinstance(item, dict)]
    entry_ids = [item.get("id") for item in entries if isinstance(item, dict)]
    if inventory_ids != entry_ids or len(inventory_ids) != len(set(inventory_ids)):
        problems.append("controlled comparison inventory coverage mismatch")
    if record.get("completion") == "pass":
        levels = {item.get("level") for item in inventory}
        if levels != set(contract["comparison_levels"]):
            problems.append("completion pass requires every comparison level")
    for item in entries:
        check_entry(item, contract, problems)
