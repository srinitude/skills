"""Views of asserted ledger relationships; capture and semantic acceptance are separate."""
from collections import deque


def require(condition, message):
    if not condition:
        raise ValueError(message)


def endpoints(value):
    values = value if isinstance(value, list) else [value]
    require(values and all(isinstance(x, str) and x for x in values), "invalid relationship endpoints")
    return values


def file_subjects(data):
    result = {"file:" + f["path"]: f for f in data.get("functional_file_map", [])}
    for change in data["semantic_model"].get("review_changes", []):
        snapshot = change.get("previous", {}).get("package_snapshot") or {}
        result.update({"file:" + name: record for name, record in snapshot.get("files", {}).items()})
    result.update({"file:" + name: record for name, record in data.get("package_snapshot", {}).get("files", {}).items()})
    result["file-set:governed"] = {"members": sorted(result)}
    for name, file in data.get("dependency_snapshot", {}).get("files", {}).items():
        for task, declaration in (file.get("mise_tasks") or {}).items():
            result[f"task:{name}#{task}"] = {"file": name, "name": task, "declaration": declaration}
    return result


def subjects(data):
    result = {}
    for kind, field, key in [("source", "source_records", "id"), ("group", "source_owner_groups", "id"),
                             ("message", "message_requirements", "id"), ("document", "packet_documents", "name")]:
        for record in data.get(field, []):
            identifier = kind + ":" + record[key]
            require(identifier not in result, "duplicate ledger subject: " + identifier)
            result[identifier] = record
    for row in data.get("source_records", []):
        for clause in row.get("clauses", []):
            identifier = "clause:" + clause["id"]
            require(identifier not in result, "duplicate ledger clause: " + identifier)
            result[identifier] = clause
    for document in data.get("packet_documents", []):
        for line, text in enumerate(document["text"].splitlines(True), 1):
            result[f"document-line:{document['name']}@{line}"] = {"line": line, "text": text}
    result.update(file_subjects(data))
    return result


def validate_graph(data, index):
    model = data["semantic_model"]
    definitions = model["relationship_types"]
    require(isinstance(definitions, dict) and definitions, "relationship catalog must be a nonempty object")
    for definition in definitions.values():
        require(all(isinstance(definition.get(k), str) and definition[k].strip()
                    for k in ["family", "meaning", "transitivity", "review_state"]), "incomplete relationship definition")
        require(all(x in index for x in definition.get("source_basis", [])), "unknown definition basis")
    require(isinstance(model["relationships"], list), "relationships must be an array")
    seen = set()
    for edge in model["relationships"]:
        require(isinstance(edge.get("id"), str) and edge["id"] and edge["id"] not in seen, "missing or duplicate relationship ID")
        seen.add(edge["id"])
        require(edge["type"] in definitions, "unknown relationship type")
        require(edge["review_state"] in {"candidate", "reviewed", "rejected", "stale"}, "invalid relationship review state")
        require(all(isinstance(edge.get(k), str) and edge[k].strip() for k in ["meaning", "condition"]), "missing relationship meaning or condition")
        require(isinstance(edge.get("basis"), list) and edge["basis"], "missing relationship basis")
        require(all(x in index for x in endpoints(edge["from"]) + endpoints(edge["to"]) + edge["basis"]), "unknown relationship subject or basis")
        require(edge["review_state"] != "reviewed" or edge.get("reviewer"), "reviewed relationship lacks reviewer")


def resolved_ends(edge, side, index):
    declared = endpoints(edge[side])
    members = [member for node in declared for member in
               (index[node]["members"] if node == "file-set:governed" else [node])]
    return list(dict.fromkeys(declared + members))


def filtered_edges(data, relation_type):
    model = data["semantic_model"]
    require(relation_type is None or relation_type in model["relationship_types"], "unknown relationship type filter")
    return [edge for edge in model["relationships"] if relation_type is None or edge["type"] == relation_type]


def follow(edge, node, direction, index):
    before, after = resolved_ends(edge, "from", index), resolved_ends(edge, "to", index)
    return ((after if direction in {"out", "both"} and node in before else [])
            + (before if direction in {"in", "both"} and node in after else []))


def trace(data, index, selector, direction, depth, relation_type):
    edges = filtered_edges(data, relation_type)
    adjacency = {}
    for edge in edges:
        for node in set(resolved_ends(edge, "from", index) + resolved_ends(edge, "to", index)):
            adjacency.setdefault(node, []).append(edge)
    queue, seen, found = deque([(selector, 0)]), {selector}, {}
    while queue:
        node, distance = queue.popleft()
        if distance >= depth:
            continue
        for edge in adjacency.get(node, []):
            following = follow(edge, node, direction, index)
            if following:
                found[edge["id"]] = edge
            queue.extend((target, distance + 1) for target in dict.fromkeys(following) if target not in seen)
            seen.update(following)
    return {"start": selector, "direction": direction, "depth": depth,
            "nodes": sorted(seen), "edges": list(found.values())}


def view(data, request):
    index = subjects(data)
    validate_graph(data, index)
    action, selector = request["action"], request.get("selector")
    if action == "catalog":
        return {key: value for key, value in data["semantic_model"].items()
                if key in {"facets", "relationship_types", "themes", "rule_types", "traversals", "body_hub", "entry_defaults"}}
    require(selector in index, "unknown ledger subject")
    if action == "show":
        return {"id": selector, "entry": index[selector], "review": data["semantic_model"].get("entry_reviews", {}).get(selector)}
    direction, relation_type = request.get("direction", "both"), request.get("relation_type")
    require(direction in {"in", "out", "both"}, "invalid relationship direction")
    if action == "relations":
        return [edge for edge in filtered_edges(data, relation_type) if follow(edge, selector, direction, index)]
    require(action == "trace", "unknown ledger action")
    depth = request.get("depth", 1)
    require(type(depth) is int and depth >= 0, "trace depth must be a nonnegative integer")
    return trace(data, index, selector, direction, depth, relation_type)
