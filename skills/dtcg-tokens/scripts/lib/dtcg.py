"""Structural, value, alias, and cycle checks for DTCG 2025.10 JSON."""
import hashlib
import json
import re
from pathlib import Path

from .dtcg_resolution import ResolutionError, expand_document, reference_owner, references_in, resolve_token, whole_alias_target
from .dtcg_values import TYPES, validate_value

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
    if kind is not None and (not isinstance(kind, str) or kind not in TYPES):
        add_error(state, path, f"unknown DTCG type {kind}")


def check_metadata(state, node, path, token=False, root=False):
    if "$description" in node and not isinstance(node["$description"], str):
        add_error(state, path, "description must be a string")
    if "$extensions" in node and not isinstance(node["$extensions"], dict):
        add_error(state, path, "extensions must be an object")
    deprecated = node.get("$deprecated")
    if "$deprecated" in node and not isinstance(deprecated, (bool, str)):
        add_error(state, path, "deprecated must be a boolean or string")
    if token and "$ref" in node and (not isinstance(node["$ref"], str) or not node["$ref"].startswith("#/")):
        add_error(state, path, "token $ref must be a JSON Pointer beginning with #/")
    if not token and "$extends" in node and not isinstance(node["$extends"], str):
        add_error(state, path, "group $extends must be a reference string")
    if root and "$schema" in node and not isinstance(node["$schema"], str):
        add_error(state, path, "$schema must be a string")


def collect_token(state, node, path, inherited, pointer):
    if not isinstance(node, dict):
        add_error(state, path, "token must be an object")
        return
    extra = set(node) - TOKEN_KEYS
    if extra:
        add_error(state, path, f"token has unsupported keys: {', '.join(sorted(extra))}")
    if ("$value" in node) == ("$ref" in node):
        add_error(state, path, "token needs exactly one of $value or $ref")
    check_metadata(state, node, path, token=True)
    explicit = node.get("$type")
    check_type(state, path, explicit if explicit is not None else inherited)
    state["tokens"][path] = {"node": node, "explicit_type": explicit, "inherited_type": inherited, "pointer": pointer}
    state["pointer_tokens"][pointer] = path


def walk_member(state, name, child, path, pointer, group_type, allowed):
    if name.startswith("$"):
        if name not in allowed:
            add_error(state, path, f"unsupported group property {name}")
        elif name == "$root":
            collect_token(state, child, f"{path}.$root".strip("."), group_type, pointer + (name,))
        return
    child_path = f"{path}.{name}".strip(".")
    if not NAME.fullmatch(name):
        add_error(state, child_path, "invalid token or group name")
    walk(state, child, child_path, group_type, False, pointer + (name,))


def walk(state, node, path="", inherited=None, root=False, pointer=()):
    if not isinstance(node, dict):
        add_error(state, path, "group or token must be an object")
        return
    if "$value" in node or "$ref" in node:
        if root:
            add_error(state, path, "document root must be a group")
        collect_token(state, node, path, inherited, pointer)
        return
    check_metadata(state, node, path, root=root)
    group_type = node.get("$type", inherited)
    check_type(state, path, group_type)
    allowed = GROUP_KEYS | ({"$schema"} if root else set())
    for name, child in node.items():
        walk_member(state, name, child, path, pointer, group_type, allowed)


def append_reference(state, graph, path, reference):
    try:
        owner = reference_owner(state, reference)
        if owner:
            graph[path].append(owner)
    except ResolutionError as error:
        add_error(state, path, str(error))


def build_graph(state):
    graph = {path: [] for path in state["tokens"]}
    for path, record in state["tokens"].items():
        value = record["node"].get("$value", record["node"].get("$ref"))
        refs = references_in(value if "$value" in record["node"] else {"$ref": value})
        state["reference_count"] += len(refs)
        for reference in refs:
            append_reference(state, graph, path, reference)
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
    if record["explicit_type"]:
        return record["explicit_type"]
    active = (active or set()) | {path}
    try:
        target = whole_alias_target(state, path)
    except ResolutionError:
        target = None
    if target and target not in active:
        return resolved_type(state, graph, target, active)
    return record["inherited_type"]


def check_values(state, graph):
    counts = {}
    for path, record in state["tokens"].items():
        kind = resolved_type(state, graph, path)
        if not kind:
            add_error(state, path, "token type cannot be resolved")
            continue
        counts[kind] = counts.get(kind, 0) + 1
        try:
            value = resolve_token(state, path)
            state["errors"].extend(validate_value(kind, value, f"{path}.$value"))
            target = whole_alias_target(state, path)
            target_type = resolved_type(state, graph, target) if target else None
            if target_type and target_type != kind:
                add_error(state, path, f"alias type {target_type} does not match {kind}")
        except ResolutionError as error:
            add_error(state, path, str(error))
    return counts


def validate(path, schema_path=None):
    document, read_errors = read_json(path)
    expanded, extension_errors = expand_document(document)
    state = {"tokens": {}, "pointer_tokens": {}, "document": expanded, "reference_count": 0, "errors": list(read_errors) + extension_errors}
    if document is not None:
        walk(state, expanded, root=True)
    graph = build_graph(state)
    check_cycles(state, graph)
    counts = check_values(state, graph)
    schema_hash = hashlib.sha256(Path(schema_path).read_bytes()).hexdigest() if schema_path and Path(schema_path).is_file() else None
    errors = list(dict.fromkeys(state["errors"]))
    return {"valid": not errors, "specification": "DTCG 2025.10", "token_count": len(state["tokens"]), "resolved_references": state["reference_count"], "types": counts, "schema_sha256": schema_hash, "errors": errors}
