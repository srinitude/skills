"""Validate the required experimental token partition and artifact coverage."""
import json
from pathlib import Path

NAMESPACE = "org.dtcg-tokens.experimental"
REQUIRED_META = {
    "experiment_id",
    "exploration_strategy",
    "hypothesis",
    "intended_context",
    "status",
    "invariant_disposition",
}
STATUSES = {"retained_unproven", "active_experiment", "validated_candidate"}


def strategy_ids():
    path = Path(__file__).resolve().parents[2] / "assets" / "exploration-strategy-catalog.json"
    catalog = json.loads(path.read_text(encoding="utf-8"))
    return {item["id"] for item in catalog["strategies"]}


def token_nodes(node, path=()):
    records = []
    if not isinstance(node, dict):
        return records
    if "$value" in node or "$ref" in node:
        return [(".".join(path), node)]
    for key, value in node.items():
        if not key.startswith("$"):
            records.extend(token_nodes(value, path + (key,)))
    return records


def experimental_records(tokens, errors):
    partition = tokens.get("experimental", {}) if isinstance(tokens, dict) else {}
    policy = partition.get("$extensions", {}).get(NAMESPACE, {})
    expected_policy = {"required": True, "policy_version": "1.0", "strategy_catalog_version": "1.0.0", "minimum_retained_tokens": 2, "minimum_distinct_strategies": 2}
    if any(policy.get(key) != value for key, value in expected_policy.items()):
        errors.append("experimental partition needs required policy metadata")
    records = token_nodes(partition, ("experimental",))
    if len(records) < 2:
        errors.append("final token output needs at least two experimental tokens")
    allowed = strategy_ids()
    strategies = set()
    for path, node in records:
        metadata = node.get("$extensions", {}).get(NAMESPACE, {})
        if not REQUIRED_META <= set(metadata):
            errors.append(f"experimental token {path} needs experiment metadata")
        if metadata.get("status") not in STATUSES:
            errors.append(f"experimental token {path} has invalid experiment status")
        strategy = metadata.get("exploration_strategy")
        if strategy not in allowed:
            errors.append(f"experimental token {path} has invalid exploration strategy")
        else:
            strategies.add(strategy)
    if len(strategies) < 2:
        errors.append("experimental output needs two distinct exploration strategies")
    return records, strategies


def ledger_paths(evidence, errors):
    ledger = evidence.get("possibility_ledger", {})
    items = ledger.get("overrides", []) + ledger.get("extensions", [])
    retained = [item for item in items if item.get("experimental") is True]
    paths = {path for item in retained for path in item.get("tokens", [])}
    if not retained or any(item.get("disposition") != "included" for item in retained):
        errors.append("experimental possibilities must be retained as included")
    return paths


def evidence_paths(evidence, errors):
    output = evidence.get("experimental_output", {})
    expected_policy = {"required": True, "policy_version": "1.0", "strategy_catalog_version": "1.0.0", "minimum_retained_tokens": 2, "minimum_distinct_strategies": 2}
    if any(output.get(key) != value for key, value in expected_policy.items()):
        errors.append("evidence needs required experimental output policy")
    entries = output.get("entries", [])
    paths = [item.get("path") for item in entries if isinstance(item, dict)]
    if not paths or len(paths) != len(set(paths)):
        errors.append("experimental output entries need unique token paths")
    allowed = strategy_ids()
    for item in entries:
        if not item.get("experiment_id") or not item.get("hypothesis"):
            errors.append(f"experimental output {item.get('path')} needs identity and hypothesis")
        if item.get("exploration_strategy") not in allowed:
            errors.append(f"experimental output {item.get('path')} has invalid exploration strategy")
        if item.get("artifact_disposition") != "visible_specimen_required":
            errors.append(f"experimental output {item.get('path')} must require a visible specimen")
    return set(paths)


def check_manifest_match(records, evidence, errors):
    entries = {item.get("path"): item for item in evidence.get("experimental_output", {}).get("entries", [])}
    fields = REQUIRED_META
    for path, node in records:
        metadata = node.get("$extensions", {}).get(NAMESPACE, {})
        entry = entries.get(path, {})
        for field in fields:
            if entry.get(field) != metadata.get(field):
                errors.append(f"experimental output {path} mismatches token {field}")


def final_review_paths(evidence, token_paths, errors):
    review = evidence.get("artifact_review", {}).get("experimental_review", {})
    paths = review.get("reviewed_paths", [])
    if review.get("status") != "pass" or set(paths) != token_paths or len(paths) != len(set(paths)):
        errors.append("experimental artifact review coverage mismatch")
    if len(str(review.get("findings", ""))) < 30:
        errors.append("experimental artifact review needs located findings")


def validate_experimental_output(tokens, evidence, final=False):
    errors = []
    records, strategies = experimental_records(tokens, errors)
    token_paths = {path for path, _ in records}
    recorded_paths = evidence_paths(evidence, errors)
    retained_paths = ledger_paths(evidence, errors)
    if token_paths != recorded_paths or token_paths != retained_paths:
        errors.append("experimental token coverage mismatch")
    check_manifest_match(records, evidence, errors)
    if final:
        final_review_paths(evidence, token_paths, errors)
    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "token_count": len(token_paths),
        "strategies": sorted(strategies),
        "token_paths": sorted(token_paths),
        "evidence_paths": sorted(recorded_paths),
    }
