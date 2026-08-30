"""Resolve one tool and normalize behavior without dropping source text."""
import json
import re
from pathlib import Path

from common import (InputError, WorkflowError, at_path, canonical_json,
                    digest_text, load_json)

ORIGINS = {"established-mcp", "owned-mcp", "native", "custom"}
TOOL_FIELDS = ["origin_class", "callable_name", "provider_or_owner",
               "runtime_or_server", "namespace", "discovery_route"]
RULE_DEFAULTS = {
    "timing": "unspecified", "trigger": "in scope", "actor": "agent",
    "target": "selected tool call", "strength": "required", "input": "unspecified",
    "transformation": "none stated", "action": "follow original wording",
    "output": "unspecified", "state": "none stated", "ordering": "source order",
    "dependencies": [], "precedence": 0, "repetition": "per in-scope call",
    "concurrency": "unspecified", "authorization": "current user authority",
    "privacy": "preserve stated boundaries", "cost": "unknown",
    "reversibility": "unknown", "destination": "none stated",
    "success_evidence": "rule is traceable in output", "failure_branch": "stop and report",
    "fallback": "none stated", "stop_condition": "rule cannot be followed",
    "cleanup": "none stated", "enforcement": "instruction-only",
}


def require_tool_fields(tool):
    missing = [name for name in TOOL_FIELDS if not tool.get(name)]
    if missing:
        raise InputError("tool descriptor missing: " + ", ".join(missing))
    if tool["origin_class"] not in ORIGINS:
        raise InputError(f"unsupported origin class: {tool['origin_class']}")
    if not isinstance(tool.get("input_schema"), dict):
        raise InputError("tool descriptor needs input_schema")
    if not isinstance(tool.get("capabilities"), dict):
        raise InputError("tool descriptor needs capabilities")


def tool_profile(tool):
    require_tool_fields(tool)
    sources = tool.get("sources")
    if not isinstance(sources, list) or not sources:
        raise InputError("tool descriptor needs at least one source")
    if not any(item.get("status") == "verified" for item in sources
               if isinstance(item, dict)):
        raise WorkflowError("tool contract has no verified source")
    identity = {name: tool.get(name) for name in TOOL_FIELDS}
    identity["version"] = tool.get("version")
    contract = {"input_schema": tool.get("input_schema"),
                "output_schema": tool.get("output_schema"),
                "capabilities": tool.get("capabilities")}
    contract_hash = digest_text(canonical_json(contract))
    if not identity["version"]:
        identity["contract_hash"] = contract_hash
    identity_hash = digest_text(canonical_json(identity))
    return {"schema": "tool-call-config/tool-profile/v1", "identity": identity,
            "identity_hash": identity_hash, "contract_hash": contract_hash,
            "contract": contract, "sources": sources}


def resolve_tool(reference, registry=None):
    if reference.startswith("@"):
        value = load_json(at_path(reference), "tool descriptor")
        if not isinstance(value, dict) or "callable_name" not in value:
            raise InputError("tool reference must describe exactly one callable tool")
        return tool_profile(value)
    if not registry:
        raise InputError("an exact name needs --registry with a live or captured listing")
    value = load_json(at_path(registry), "tool registry")
    tools = value.get("tools", []) if isinstance(value, dict) else []
    matches = [item for item in tools if item.get("callable_name") == reference]
    if len(matches) != 1:
        raise InputError(f"{reference!r} resolved to {len(matches)} tools; need exactly one")
    return tool_profile(matches[0])


def markdown_rules(text):
    rules = []
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = re.sub(r"^\s*(?:[-*+] |\d+[.)] )", "", line).strip()
        if stripped and not stripped.startswith("#"):
            rules.append({"original": stripped, "source_locator": f"line:{number}"})
    return rules


def yaml_rules(text):
    rules, current = [], None
    for number, line in enumerate(text.splitlines(), start=1):
        hit = re.match(r"\s*-\s+original:\s*(.+)", line)
        field = re.match(r"\s+([a-z_]+):\s*(.+)", line)
        if hit:
            current = {"original": hit.group(1).strip(' "\''),
                       "source_locator": f"line:{number}"}
            rules.append(current)
        elif field and current:
            current[field.group(1)] = field.group(2).strip(' "\'')
    return rules or markdown_rules(text)


def structured_rules(value):
    if not isinstance(value, dict) or not isinstance(value.get("rules"), list):
        raise InputError("behavior JSON needs a rules array")
    rules = []
    for index, item in enumerate(value["rules"], start=1):
        if not isinstance(item, dict) or not str(item.get("original", "")).strip():
            raise InputError(f"behavior rule {index} needs original wording")
        rule = dict(item)
        rule["source_locator"] = item.get("source_locator", f"rules:{index}")
        rules.append(rule)
    return rules


def read_behavior(value):
    if value.startswith("@"):
        path = at_path(value)
        text = path.read_text(encoding="utf-8")
        suffix, locator = path.suffix.lower(), str(path)
    else:
        text, suffix, locator = value, ".md", "inline"
    if not text.strip():
        raise InputError("behavior input is empty")
    if suffix == ".json":
        try:
            rules = structured_rules(json.loads(text))
        except json.JSONDecodeError as error:
            raise InputError(f"invalid behavior JSON: {error}") from error
    else:
        rules = yaml_rules(text) if suffix in {".yaml", ".yml"} else markdown_rules(text)
    if not rules:
        raise InputError("behavior input has no rules")
    return normalize_behavior(text, locator, rules)


def normalize_behavior(text, locator, rules):
    normalized = []
    for rule in rules:
        merged = {**RULE_DEFAULTS, **rule}
        seed = f"{merged['source_locator']}\n{merged['original']}"
        merged["id"] = "B-" + digest_text(seed)[:12]
        normalized.append(merged)
    check_conflicts(normalized)
    core = {"source_text": text, "source_locator": locator, "rules": normalized}
    core["behavior_hash"] = digest_text(canonical_json(core))
    return {"schema": "tool-call-config/behavior-profile/v1", **core}


def check_conflicts(rules):
    strengths = {}
    for rule in rules:
        action = str(rule.get("action", "")).strip().lower()
        if action:
            strengths.setdefault(action, set()).add(rule.get("strength"))
    for action, values in strengths.items():
        if {"required", "prohibited"} <= values:
            raise WorkflowError(f"behavior conflict for action: {action}")
