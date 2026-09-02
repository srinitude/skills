"""Check current integrated evidence without judging design quality."""

from lib.render_validation import (
    check_render_contexts, is_parserless_mapping, is_typescript,
)


def check_requirements(record, problems):
    entries = record.get("requirements", [])
    ids = [item.get("id") for item in entries if isinstance(item, dict)]
    if not entries or len(ids) != len(set(ids)) or not all(ids):
        problems.append("requirements must be nonempty with unique ids")
    for index, item in enumerate(entries):
        if not item.get("request") or not item.get("owner"):
            problems.append(f"requirements[{index}] needs request and owner")
        if not isinstance(item.get("invalidated_by"), list):
            problems.append(f"requirements[{index}].invalidated_by must be a list")
        if item.get("disposition") not in {"use", "not_applicable"}:
            problems.append(f"requirements[{index}].disposition is invalid")
        if item.get("status") != "pass" or not item.get("evidence"):
            problems.append(f"requirements[{index}] needs current passing evidence")
        if item.get("disposition") == "not_applicable" and not item.get("reason"):
            problems.append(f"requirements[{index}].reason is required")


def check_quality(record, contract, problems):
    evidence = record.get("quality_evidence", {})
    token = evidence.get("token", {})
    if (token.get("status"), token.get("freshness"), token.get("scope")) != (
            "pass", "current", "token_and_proof_only"):
        problems.append("quality_evidence.token must be current token-only PASS")
    if not token.get("evidence"):
        problems.append("quality_evidence.token needs current evidence")
    design = evidence.get("design", {})
    expected = contract["quality_gate_ids"]
    gates = design.get("gates", [])
    ids = [item.get("id") for item in gates if isinstance(item, dict)]
    if ids != expected or any(item.get("status") != "pass" for item in gates):
        problems.append("quality_evidence.design gates must all pass in canonical order")
    if any(not item.get("evidence") for item in gates):
        problems.append("quality_evidence.design gates need gate evidence")
    actual = (design.get("status"), design.get("diagnosis"),
              design.get("freshness"), design.get("checkpoint"))
    if actual != ("pass", "PASS", "current", "integrated"):
        problems.append("quality_evidence.design must be a current integrated PASS")
    if any(not design.get(field) for field in contract["quality_visual_contexts"]):
        problems.append("quality_evidence.design needs all visual contexts")
    owner = contract["figma_app_pass_gate"]["vision_owner"]
    if design.get("vision_owner") != owner:
        problems.append("quality_evidence.design needs the same direct vision owner")


def check_property_dispositions(record, contract, problems):
    entries = record.get("property_kind_dispositions", [])
    expected = contract["component_property_kinds"]
    if [item.get("kind") for item in entries] != expected:
        problems.append("property_kind_dispositions must cover every canonical kind")
    for index, item in enumerate(entries):
        if item.get("disposition") not in contract["property_kind_dispositions"]:
            problems.append(f"property_kind_dispositions[{index}] is invalid")
        if not item.get("reason") or not item.get("evidence"):
            problems.append(f"property_kind_dispositions[{index}] needs reason and evidence")


def check_property(item, prop, contract, comparison_ids, problems):
    allowed = set(contract["component_property_kinds"])
    if item.get("kind") not in allowed or item.get("status") != "pass":
        problems.append(f"{prop} has invalid kind or status")
    if item.get("disposition") not in contract["property_dispositions"]:
        problems.append(f"{prop}.disposition is invalid")
    if not item.get("justification") or not item.get("figma_evidence"):
        problems.append(f"{prop} needs Figma evidence and justification")
    link_field = contract["property_comparison_link_field"]
    if item.get(link_field) not in comparison_ids:
        problems.append(f"{prop} needs a current comparison link")
    needed = ["code_evidence", "mapping_evidence"]
    if item.get("disposition") == "mapped" and not all(item.get(key) for key in needed):
        problems.append(f"{prop} needs code and mapping evidence")
    if item.get("disposition") == "mapped" and not is_typescript(item.get("code_evidence")):
        problems.append(f"{prop} needs TypeScript evidence")
    if item.get("disposition") == "mapped" and not is_parserless_mapping(item.get("mapping_evidence")):
        problems.append(f"{prop} needs parserless .figma.ts evidence")
    api_fields = ["figma_property", "react_prop", "api_evidence", "render_evidence"]
    if item.get("disposition") == "mapped" and not all(item.get(key) for key in api_fields):
        problems.append(f"{prop} needs API and render evidence")


def check_property_parity(record, contract, problems):
    components = record.get("property_parity", [])
    if not components:
        problems.append("property_parity must contain inspected components")
    entries = record.get("controlled_comparisons", {}).get("entries", [])
    comparison_ids = {item.get("id") for item in entries if isinstance(item, dict)}
    expected = contract["component_property_kinds"]
    owners = [(item.get("component_id"), item.get("figma_node")) for item in components]
    if len(owners) != len(set(owners)):
        problems.append("property_parity component owners must be unique")
    for position, component in enumerate(components):
        where = f"property_parity[{position}]"
        if not all(component.get(key) for key in ["component_id", "figma_node", "code_export"]):
            problems.append(f"{where} needs Figma and code owners")
        properties = component.get("properties", [])
        if [item.get("kind") for item in properties] != expected:
            problems.append(f"{where} canonical kind coverage mismatch")
        for index, item in enumerate(properties):
            check_property(item, f"{where}.properties[{index}]", contract,
                           comparison_ids, problems)


def check_governance(record, problems):
    entries = record.get("governance", [])
    expected = ["component", "mapping", "generator"]
    if [item.get("scope") for item in entries] != expected:
        problems.append("governance must cover component, mapping, and generator owners")
    paths = [item.get("path") for item in entries]
    if len(paths) != len(set(paths)):
        problems.append("governance needs unique owner paths")
    for index, item in enumerate(entries):
        if not all(item.get(key) for key in ["path", "parent_path"]):
            problems.append(f"governance[{index}] needs path and parent_path")
        if item.get("parent_required") is not True:
            problems.append(f"governance[{index}] must require its parent chain")
        if item.get("design_system_source_of_truth") is not True:
            problems.append(f"governance[{index}] must keep the design system as source truth")
        if item.get("status") != "pass":
            problems.append(f"governance[{index}] must pass")
        if not item.get("generated_owner"):
            problems.append(f"governance[{index}] needs a generated owner")


def check_figma_pass_header(item, gate, where, problems):
    checks = [
        (item.get("skills") == gate["required_skills"], "needs the fresh four-skill chain"),
        (item.get("skills_fresh_before_first_decision") is True, "needs skills before its first decision"),
        (item.get("source_receipts") == gate["required_sources"], "needs every source receipt"),
        (item.get("item_kinds") == gate["required_item_kinds"], "item kinds must cover the full Figma surface"),
        ((item.get("status"), item.get("freshness")) == ("pass", "current"), "must be a current pass"),
        (item.get("computer_control_capability") == gate["computer_control_capability"], "needs the required application control"),
        (item.get("vision_owner") == gate["vision_owner"], "needs the same direct vision owner"),
    ]
    problems.extend(f"{where} {message}" for passed, message in checks if not passed)


def check_figma_app_pass(item, gate, problems):
    where = f"figma app pass {item.get('id', '<missing>')}"
    check_figma_pass_header(item, gate, where, problems)
    records = item.get("items", [])
    kinds = [record.get("kind") for record in records]
    ids = [record.get("id") for record in records]
    if set(kinds) != set(gate["required_item_kinds"]) or len(ids) != len(set(ids)):
        problems.append(f"{where} item coverage must match its claimed kinds")
    if item.get("item_count") != len(records) or not item.get("inventory_digest"):
        problems.append(f"{where} needs a current inventory count and digest")
    needed = gate["required_evidence_fields"]
    if not needed or any(not item.get(field) for field in needed):
        problems.append(f"{where} needs before and after cleanliness evidence")
    for position, record in enumerate(records):
        path = f"{where}.items[{position}]"
        needed = ["id", "kind", "decision", "vision_evidence"]
        if not all(record.get(field) for field in needed):
            problems.append(f"{path} needs an item decision and direct vision")
        if record.get("source_receipts") != gate["required_sources"]:
            problems.append(f"{path} needs every item source receipt")
        if (record.get("decision"), record.get("freshness")) != ("pass", "current"):
            problems.append(f"{path} needs a current passing decision")
        check_item_page(record, path, problems)


def check_item_page(record, path, problems):
    expected = record.get("canonical_page_id")
    ancestry = record.get("ancestry", [])
    if not expected or record.get("actual_page_id") != expected:
        problems.append(f"{path} must resolve to its canonical page")
    if not ancestry or ancestry[0] != expected or ancestry[-1] != record.get("id"):
        problems.append(f"{path} needs current page ancestry")
    if not record.get("readback"):
        problems.append(f"{path} needs current node readback")


def check_figma_app_audit(record, contract, problems):
    audit = record.get("figma_app_audit", {})
    if audit.get("in_scope") is not True:
        if record.get("completion") == "pass":
            problems.append("completion pass requires a current Figma app audit")
        return
    passes = audit.get("passes", [])
    if not passes:
        problems.append("Figma app audit needs at least one recorded pass")
    for item in passes:
        check_figma_app_pass(item, contract["figma_app_pass_gate"], problems)


def check_integrated(record, contract, problems):
    check_figma_app_audit(record, contract, problems)
    if record.get("completion") != "pass":
        return
    stages = record.get("stages", [])
    if any(item.get("status") not in {"pass", "not_applicable"} for item in stages):
        problems.append("completion pass requires every stage to pass or be justified not applicable")
    lineage = record.get("lineage", [])
    if not lineage or any(item.get("status") != "pass" for item in lineage):
        problems.append("completion pass requires current passing lineage")
    check_requirements(record, problems)
    check_quality(record, contract, problems)
    check_property_dispositions(record, contract, problems)
    check_property_parity(record, contract, problems)
    check_governance(record, problems)
    check_render_contexts(record, contract, problems)
