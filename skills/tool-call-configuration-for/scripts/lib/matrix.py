"""Trace behavior rules against verified tool capabilities."""


def disposition(rule, tool):
    wanted = rule.get("enforcement", "instruction-only")
    available = tool["contract"]["capabilities"].get("enforcement_classes", [])
    if wanted == "instruction-only":
        return "instruction-only"
    if wanted in available:
        return "supported with conditions"
    return "requires additional integration"


def rule_matrix(tool, behavior):
    rows = []
    for rule in behavior["rules"]:
        status = disposition(rule, tool)
        rows.append({
            "rule_id": rule["id"], "source_locator": rule["source_locator"],
            "original": rule["original"], "requested_enforcement": rule["enforcement"],
            "disposition": status, "tool_contract_hash": tool["contract_hash"],
            "evidence": [item.get("locator") for item in tool["sources"]],
            "additional_integration": (
                "A verified host hook, policy layer, proxy, or tool implementation change."
                if status == "requires additional integration" else None),
        })
    return {"schema": "tool-call-config/rule-matrix/v1",
            "tool_identity_hash": tool["identity_hash"],
            "behavior_hash": behavior["behavior_hash"], "rules": rows}
