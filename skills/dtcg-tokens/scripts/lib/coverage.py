"""Build deterministic token, alias, type, composite, and variant coverage."""
import itertools
import json

from .dtcg import build_graph, resolved_type, walk
from .dtcg_values import TYPES, is_reference

COMPOSITE_FIELDS = {"border": ["color", "width", "style"], "transition": ["duration", "delay", "timingFunction"], "typography": ["fontFamily", "fontSize", "fontWeight", "letterSpacing", "lineHeight"]}


def token_state(document):
    state = {"tokens": {}, "errors": []}
    walk(state, document, root=True)
    graph = build_graph(state)
    return state, graph


def resolve_value(state, graph, path, active=None):
    active = (active or []) + [path]
    record = state["tokens"][path]
    value = record["node"].get("$value", record["node"].get("$ref"))
    if is_reference(value):
        target = value[1:-1]
        return None if target in active else resolve_value(state, graph, target, active)
    return value


def inventory(document):
    state, graph = token_state(document)
    records = []
    for path in sorted(state["tokens"]):
        node = state["tokens"][path]["node"]
        value = node.get("$value", node.get("$ref"))
        records.append({"path": path, "type": resolved_type(state, graph, path), "source_value": value, "resolved_value": resolve_value(state, graph, path), "alias_targets": graph.get(path, []), "specimen_id": f"token-{len(records) + 1:04d}"})
    return records, state["errors"]


def alias_edges(records):
    return [{"source": item["path"], "target": target, "status": "resolved", "type": item["type"]} for item in records for target in item["alias_targets"]]


def composite_parts(record):
    value = record["resolved_value"]
    kind = record["type"]
    if kind in COMPOSITE_FIELDS and isinstance(value, dict):
        return [{"path": record["path"], "type": kind, "member": key, "value": value.get(key)} for key in COMPOSITE_FIELDS[kind]]
    if kind == "shadow":
        layers = value if isinstance(value, list) else [value]
        return [{"path": record["path"], "type": kind, "member": f"layer-{index}", "value": layer} for index, layer in enumerate(layers)]
    if kind == "gradient" and isinstance(value, list):
        return [{"path": record["path"], "type": kind, "member": f"stop-{index}", "value": stop} for index, stop in enumerate(value)]
    return []


def stress_cells(records):
    by_type = {kind: [item for item in records if item["type"] == kind] for kind in TYPES}
    cells = [{"id": item["specimen_id"], "group": "primary", "tokens": [item["path"]]} for item in records]
    cells += [{"id": f"color-pair-{a}-{b}", "group": "color-pair", "tokens": [left["path"], right["path"]]} for a, left in enumerate(by_type["color"]) for b, right in enumerate(by_type["color"])]
    cells += [{"id": f"font-weight-{a}-{b}", "group": "font-weight", "tokens": [family["path"], weight["path"]]} for a, family in enumerate(by_type["fontFamily"]) for b, weight in enumerate(by_type["fontWeight"])]
    cells += [{"id": f"motion-{a}-{b}", "group": "duration-curve", "tokens": [duration["path"], curve["path"]]} for a, duration in enumerate(by_type["duration"]) for b, curve in enumerate(by_type["cubicBezier"])]
    return cells


def variant_groups(evidence, errors):
    space = evidence.get("permutation_space", {})
    axes = {item["id"]: item.get("values", []) for item in space.get("axes", [])}
    exclusions = {item.get("cell"): item for item in space.get("exclusions", [])}
    known = set()
    groups = []
    for group in space.get("groups", []):
        values = [axes.get(axis, []) for axis in group.get("axes", [])]
        cells = []
        for combo in itertools.product(*values):
            key = "|".join([group["id"], *combo])
            known.add(key)
            exclusion = exclusions.get(key)
            cells.append({"id": key, "values": list(combo), "status": "not_applicable" if exclusion else "rendered", "reason": exclusion.get("reason") if exclusion else None})
        groups.append({"id": group["id"], "axes": group.get("axes", []), "expected": len(cells), "rendered": len(cells), "cells": cells})
    for key in exclusions:
        if key not in known:
            errors.append(f"unknown permutation exclusion {key}")
    return groups


def context_errors(records, evidence):
    covered = {path for item in evidence.get("context_requirements", []) for path in item.get("tokens", [])}
    paths = {item["path"] for item in records}
    errors = [f"context requirement names missing token {path}" for path in sorted(covered - paths)]
    errors += [f"token {path} has no context requirement" for path in sorted(paths - covered)]
    return errors


def analyze_coverage(tokens, evidence):
    records, errors = inventory(tokens)
    errors += context_errors(records, evidence)
    groups = variant_groups(evidence, errors)
    types = [{"type": kind, "supplied": sum(item["type"] == kind for item in records), "rendered": sum(item["type"] == kind for item in records), "status": "present" if any(item["type"] == kind for item in records) else "not_present"} for kind in sorted(TYPES)]
    composites = [part for record in records for part in composite_parts(record)]
    stress = stress_cells(records)
    totals = {"tokens_expected": len(records), "tokens_rendered": len(records), "aliases": len(alias_edges(records)), "composite_members": len(composites), "stress_cells": len(stress), "variant_cells": sum(len(item["cells"]) for item in groups), "unexplained_skips": len(errors)}
    manifest = {"token_paths": records, "alias_edges": alias_edges(records), "type_coverage": types, "composite_members": composites, "stress_groups": stress, "variant_groups": groups, "totals": totals, "status": "pass" if not errors else "fail"}
    return manifest, errors
