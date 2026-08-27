"""Validate and expand input, intent, possibility, context, and time ledgers."""
from datetime import datetime

from .catalogs import catalog_leaves, check_enum, check_enum_list, enum_values

NEGATIVE_ROLES = {"counterexample", "anti-reference", "excluded-material"}
POSITIVE_INFLUENCE = {"exact-values", "structural-relationships", "semantic-roles", "component-anatomy", "state-behavior", "mode-behavior", "visual-traits"}


def parse_time(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def validate_input_item(item, index, catalog, errors):
    path = f"input_manifest.items[{index}]"
    if not isinstance(item, dict) or not item.get("id"):
        errors.append(f"{path} needs an id")
        return
    check_enum(item.get("source_class"), set(catalog["source_classes"]), f"{path}.source_class", errors)
    for facet, allowed in catalog["input_facets"].items():
        key = facet.replace("-", "_")
        value = item.get(key)
        if facet in {"sensory-channel", "access-method", "evidence-role"}:
            check_enum_list(value, set(allowed), f"{path}.{key}", errors)
        else:
            check_enum(value, set(allowed), f"{path}.{key}", errors)
    if item.get("source_class") == "unknown-or-future" and not item.get("extension_id"):
        errors.append(f"{path} unknown-or-future needs extension_id")


def validate_inputs(evidence, catalog, errors):
    manifest = evidence.get("input_manifest", {})
    items = manifest.get("items", []) if isinstance(manifest, dict) else []
    if manifest.get("catalog_version") != catalog.get("catalog_version"):
        errors.append("input manifest catalog version mismatch")
    ids = [item.get("id") for item in items if isinstance(item, dict)]
    if not items or len(ids) != len(set(ids)):
        errors.append("input manifest needs unique items")
    for index, item in enumerate(items):
        validate_input_item(item, index, catalog, errors)
    return {"status": "pass" if not errors else "fail", "expected": len(items), "accounted": len(set(ids)), "items": items}


def validate_request_intent(request, catalog, errors):
    facets = catalog["intent_facets"]
    check_enum(request.get("requested_operation"), set(facets["requested-operation"]), "intent_manifest.request.requested_operation", errors)
    check_enum(request.get("fidelity"), set(facets["fidelity"]), "intent_manifest.request.fidelity", errors)
    check_enum_list(request.get("target_scope"), set(facets["target-scope"]), "intent_manifest.request.target_scope", errors)
    check_enum(request.get("output_use"), set(facets["output-use"]), "intent_manifest.request.output_use", errors)
    check_enum(request.get("confidence_basis"), set(facets["confidence-basis"]), "intent_manifest.request.confidence_basis", errors)
    for key in ("desired_outcome", "audience_task"):
        if len(str(request.get(key, ""))) < 12:
            errors.append(f"intent_manifest.request.{key} is too short")


def validate_source_intent(item, index, input_ids, catalog, errors):
    path = f"intent_manifest.sources[{index}]"
    facets = catalog["intent_facets"]
    if item.get("source_id") not in input_ids:
        errors.append(f"{path}.source_id must match input manifest")
    check_enum_list(item.get("roles"), set(facets["source-role"]), f"{path}.roles", errors)
    check_enum(item.get("decision_authority"), set(facets["decision-authority"]), f"{path}.decision_authority", errors)
    check_enum_list(item.get("allowed_influence"), set(facets["allowed-influence"]), f"{path}.allowed_influence", errors)
    check_enum_list(item.get("target_scope"), set(facets["target-scope"]), f"{path}.target_scope", errors)
    check_enum(item.get("confidence_basis"), set(facets["confidence-basis"]), f"{path}.confidence_basis", errors)
    if set(item.get("roles", [])) & NEGATIVE_ROLES and set(item.get("allowed_influence", [])) & POSITIVE_INFLUENCE:
        errors.append(f"{path} negative intent cannot supply positive token influence")


def validate_intents(evidence, catalog, input_report, errors):
    manifest = evidence.get("intent_manifest", {})
    validate_request_intent(manifest.get("request", {}), catalog, errors)
    input_ids = {item.get("id") for item in input_report["items"]}
    sources = manifest.get("sources", [])
    for index, item in enumerate(sources):
        validate_source_intent(item, index, input_ids, catalog, errors)
    source_ids = [item.get("source_id") for item in sources]
    if set(source_ids) != input_ids or len(source_ids) != len(set(source_ids)):
        errors.append("intent manifest must account for every input exactly once")
    conflicts = manifest.get("conflicts", [])
    if any(item.get("material") and item.get("status") != "resolved" for item in conflicts):
        errors.append("material intent conflict is unresolved")
    return {"status": "pass" if not errors else "fail", "expected": len(input_ids) + 1, "accounted": len(set(source_ids)) + bool(manifest.get("request")), "sources": sources, "conflicts": conflicts}


def expand_possibilities(evidence, catalog, errors):
    ledger = evidence.get("possibility_ledger", {})
    leaves = catalog_leaves(catalog)
    default = ledger.get("default", {})
    overrides = ledger.get("overrides", [])
    ids = [item.get("id") for item in overrides]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        errors.append(f"duplicate possibility override: {', '.join(duplicates)}")
    records = {leaf: {"id": leaf, **default} for leaf in leaves}
    for item in overrides + ledger.get("extensions", []):
        if item.get("id") not in records and item not in ledger.get("extensions", []):
            errors.append(f"unknown possibility override {item.get('id')}")
        records[item.get("id")] = item
    valid = set(catalog["dispositions"])
    for record in records.values():
        if record.get("disposition") not in valid or not record.get("reason") or not record.get("evidence"):
            errors.append(f"possibility {record.get('id')} lacks a complete disposition")
        if record.get("disposition") == "included" and not record.get("tokens"):
            errors.append(f"included possibility {record.get('id')} needs token paths")
    counts = {name: sum(item.get("disposition") == name for item in records.values()) for name in sorted(valid)}
    return records, {"status": "fail" if errors else "pass", "total": len(records), "accounted": sum(counts.values()), "duplicates": duplicates, "dispositions": counts}


def build_narrowing(records, catalog):
    active = set(records)
    stages = []
    for name in catalog["stage_order"]:
        before = len(active)
        removed = sorted(item for item in active if records[item].get("stage") == name and records[item].get("disposition") != "included")
        active -= set(removed)
        stages.append({"name": name, "input_count": before, "output_count": len(active), "removed": removed, "subset_invariant": True})
    return stages


def validate_context(evidence, records, errors):
    requirements = evidence.get("context_requirements", [])
    for item in requirements:
        if item.get("confidence") == "high" and not item.get("tokens") and not item.get("omission_reason"):
            errors.append(f"high-confidence requirement {item.get('id')} lacks tokens or omission")
        for leaf in item.get("possibilities", []):
            if leaf not in records or records[leaf].get("disposition") != "included":
                errors.append(f"context requirement {item.get('id')} uses non-included possibility {leaf}")
    return {"status": "fail" if errors else "pass", "requirements": requirements, "expected": len(requirements), "accounted": len(requirements)}


def validate_temporal(evidence, errors):
    temporal = evidence.get("temporal_context", {})
    anchor = temporal.get("anchor", {})
    anchor_time = parse_time(anchor.get("captured_at"))
    required = {"captured_at", "date", "weekday", "timezone", "utc_offset", "source"}
    if not anchor_time or not required <= set(anchor):
        errors.append("temporal context needs one valid clock anchor")
    sources = temporal.get("current_sources", [])
    for item in sources:
        retrieved = parse_time(item.get("retrieved_at"))
        if anchor_time and retrieved and retrieved > anchor_time:
            errors.append(f"current source {item.get('id')} is future-dated")
        if not retrieved or item.get("primary") is not True or item.get("status") != "verified":
            errors.append(f"current source {item.get('id')} is not verified")
    return {"status": "fail" if errors else "pass", "anchor": anchor, "current_sources": sources, "pinned": temporal.get("pinned_specification"), "current": temporal.get("current_specification")}


def validate_accounting(evidence, possibility, inputs, metrics):
    errors = []
    input_report = validate_inputs(evidence, inputs, errors)
    intent_report = validate_intents(evidence, inputs, input_report, errors)
    records, possibility_report = expand_possibilities(evidence, possibility, errors)
    context_report = validate_context(evidence, records, errors)
    temporal_report = validate_temporal(evidence, errors)
    status = "pass" if not errors else "fail"
    for report in (input_report, intent_report, possibility_report, context_report, temporal_report):
        report["status"] = status if report["status"] == "pass" else report["status"]
    return {"errors": errors, "input_accounting": input_report, "intent_accounting": intent_report, "possibility_accounting": possibility_report, "narrowing_stages": build_narrowing(records, possibility), "context_coverage": context_report, "temporal_accounting": temporal_report, "possibility_records": list(records.values())}
