"""Structural, value, alias, and cycle checks for DTCG 2025.10 JSON."""
import hashlib
import json
import re
from pathlib import Path

from .dtcg_values import TYPES, is_reference, validate_value

NAME = re.compile(r"^[^${}.][^{}.]*$")
TOKEN_KEYS = {"$value", "$ref", "$type", "$description", "$extensions", "$deprecated"}
GROUP_KEYS = {"$description", "$type", "$extensions", "$extends", "$deprecated", "$root"}


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")), []
    except (OSError, json.JSONDecodeError) as error:
        return None, [f"{path}: {error}"]


def add_error(state, path, message):
    state["errors"].append(f"{path or '<root>'}: {message}")


def check_type(state, path, kind):
    if kind is not None and kind not in TYPES:
        add_error(state, path, f"unknown DTCG type {kind}")


def collect_token(state, node, path, inherited):
    extra = set(node) - TOKEN_KEYS
    if extra:
        add_error(state, path, f"token has unsupported keys: {', '.join(sorted(extra))}")
    if "$value" in node and "$ref" in node:
        add_error(state, path, "token cannot contain both $value and $ref")
    kind = node.get("$type", inherited)
    check_type(state, path, kind)
    state["tokens"][path] = {"node": node, "declared_type": kind}


def walk_member(state, name, child, path, group_type, allowed):
    if name.startswith("$"):
        if name not in allowed:
            add_error(state, path, f"unsupported group property {name}")
        elif name == "$root":
            collect_token(state, child, f"{path}.$root".strip("."), group_type)
        return
    child_path = f"{path}.{name}".strip(".")
    if not NAME.fullmatch(name):
        add_error(state, child_path, "invalid token or group name")
    walk(state, child, child_path, group_type)


def walk(state, node, path="", inherited=None, root=False):
    if not isinstance(node, dict):
        add_error(state, path, "group or token must be an object")
        return
    if "$value" in node or "$ref" in node:
        collect_token(state, node, path, inherited)
        return
    group_type = node.get("$type", inherited)
    check_type(state, path, group_type)
    allowed = GROUP_KEYS | ({"$schema"} if root else set())
    for name, child in node.items():
        walk_member(state, name, child, path, group_type, allowed)


def references_in(value):
    if is_reference(value):
        return [value[1:-1]]
    if isinstance(value, dict):
        refs = [item[1:] for key, item in value.items() if key == "$ref" and isinstance(item, str) and item.startswith("#/")]
        return refs + sum((references_in(item) for key, item in value.items() if key != "$ref"), [])
    if isinstance(value, list):
        return sum((references_in(item) for item in value), [])
    return []


def pointer_path(pointer):
    return pointer.replace("~1", "/").replace("~0", "~").replace("/", ".").lstrip(".").removesuffix(".$value")


def build_graph(state):
    graph = {}
    for path, record in state["tokens"].items():
        value = record["node"].get("$value", record["node"].get("$ref"))
        refs = [pointer_path(item) if item.startswith("/") else item for item in references_in(value)]
        graph[path] = refs
        for target in refs:
            if target not in state["tokens"]:
                add_error(state, path, f"reference target does not exist: {target}")
    return graph


def find_cycle(graph, node, active, done):
    if node in active:
        return active[active.index(node):] + [node]
    if node in done:
        return None
    active.append(node)
    for target in graph.get(node, []):
        cycle = find_cycle(graph, target, active, done)
        if cycle:
            return cycle
    active.pop()
    done.add(node)
    return None


def check_cycles(state, graph):
    done = set()
    for path in graph:
        cycle = find_cycle(graph, path, [], done)
        if cycle:
            add_error(state, path, f"reference cycle: {' -> '.join(cycle)}")
            return


def resolved_type(state, graph, path, active=None):
    record = state["tokens"].get(path)
    if not record:
        return None
    if record["declared_type"]:
        return record["declared_type"]
    active = (active or set()) | {path}
    target = next(iter(graph.get(path, [])), None)
    return None if not target or target in active else resolved_type(state, graph, target, active)


def check_values(state, graph):
    counts = {}
    for path, record in state["tokens"].items():
        kind = resolved_type(state, graph, path)
        if not kind:
            add_error(state, path, "token type cannot be resolved")
            continue
        counts[kind] = counts.get(kind, 0) + 1
        value = record["node"].get("$value", {"$ref": record["node"].get("$ref")})
        state["errors"].extend(validate_value(kind, value, f"{path}.$value"))
        if is_reference(value):
            target = value[1:-1]
            target_type = resolved_type(state, graph, target)
            if target_type and target_type != kind:
                add_error(state, path, f"alias type {target_type} does not match {kind}")
    return counts


def validate(path, schema_path=None):
    document, read_errors = read_json(path)
    state = {"tokens": {}, "errors": list(read_errors)}
    if document is not None:
        walk(state, document, root=True)
    graph = build_graph(state)
    check_cycles(state, graph)
    counts = check_values(state, graph)
    schema_hash = hashlib.sha256(Path(schema_path).read_bytes()).hexdigest() if schema_path and Path(schema_path).is_file() else None
    return {"valid": not state["errors"], "specification": "DTCG 2025.10", "token_count": len(state["tokens"]), "resolved_references": sum(map(len, graph.values())), "types": counts, "schema_sha256": schema_hash, "errors": state["errors"]}
