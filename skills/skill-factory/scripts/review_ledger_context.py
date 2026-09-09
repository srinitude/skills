"""Recorded ledger context, with historical observations and explicit inheritance."""
from graphlib import TopologicalSorter


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relation(identifier, kind, provider, consumer, meaning, condition, basis_kind):
    return {"id": identifier, "type": kind, "from": provider, "to": consumer,
            "basis": [provider, consumer], "meaning": meaning, "condition": condition,
            "review_state": "reviewed", "reviewer": "Captured declaration predicate; no semantic or execution acceptance",
            "basis_kind": basis_kind}


def file_subjects(data):
    baseline, history = {}, {}
    for record in data.get("functional_file_map", []):
        name = record["path"]
        require(name not in baseline, "duplicate functional file owner: " + name)
        baseline[name] = record
    for number, change in enumerate(data["semantic_model"].get("review_changes", [])):
        snapshot = change.get("previous", {}).get("package_snapshot") or {}
        for name, record in snapshot.get("files", {}).items():
            history.setdefault(name, []).append({"review_change": number, "record": record})
    snapshot = data.get("package_snapshot")
    current = snapshot["files"] if snapshot is not None else {}
    names = sorted(set(baseline) | set(history) | set(current))
    result = {"file:" + name: {
        "path": name, "baseline": baseline.get(name), "history": history.get(name, []),
        "current": current.get(name),
        "dependency_observation": data.get("dependency_snapshot", {}).get("files", {}).get(name),
        "recorded_package_state": ("not-observed" if snapshot is None else "present" if name in current else "missing"),
        "limit": "Recorded package observations only; no live file existence or semantic judgment."}
        for name in names}
    result["file-set:governed"] = {"members": sorted(result)}
    return result


def reviewed_facets(data, index):
    model, graph, effective = data["semantic_model"], {}, {}
    reviews = model.get("entry_reviews", {})
    require(isinstance(reviews, dict), "semantic reviews must be an object")
    for selector, review in reviews.items():
        require(selector in index, "unknown reviewed subject: " + selector)
        parents, own = review.get("inherits", []), review.get("facets", {})
        require(isinstance(parents, list) and all(isinstance(p, str) for p in parents)
                and len(parents) == len(set(parents)), "invalid review inheritance")
        require(all(p in reviews for p in parents), "missing inherited review")
        require(isinstance(own, dict) and set(own) <= set(model.get("facets", {})), "unknown semantic facet")
        require(all(isinstance(v, str) and v.strip() for v in own.values()), "empty semantic facet")
        graph[selector] = parents
    for selector in TopologicalSorter(graph).static_order():
        merged, own = {}, reviews[selector].get("facets", {})
        for parent in graph[selector]:
            inherited = effective[parent]
            conflicts = [key for key in inherited if key in merged and merged[key] != inherited[key] and key not in own]
            require(not conflicts, "conflicting inherited facets need explicit resolution: " + ", ".join(conflicts))
            merged.update(inherited)
        effective[selector] = {**merged, **own}
    return reviews, graph, effective


def context_parents(data, review_graph, selector):
    parents = {key: list(values) for key, values in review_graph.items()}
    owners = {}
    for group in data.get("source_owner_groups", []):
        parents.setdefault("group:" + group["id"], []).extend(
            "group:" + prerequisite for prerequisite in group.get("reading_prerequisites", []))
    source_documents = ["document:" + doc["name"] for doc in data.get("packet_documents", [])
                        if doc.get("sha256") == data["source"]["sha256"]]
    for row in data.get("source_records", []):
        node = "source:" + row["id"]
        groups = ([row["owner_group"]] if row.get("owner_group") else [])
        groups += row.get("dependencies", {}).get("context_sections", [])
        parents.setdefault(node, []).extend(["group:" + g for g in groups] + source_documents)
        for clause in row.get("clauses", []):
            child = "clause:" + clause["id"]
            parents.setdefault(child, []).append(node)
            owners[child] = node
    if selector.startswith("document-line:"):
        document = "document:" + selector.removeprefix("document-line:").rsplit("@", 1)[0]
        parents.setdefault(selector, []).append(document)
        owners[selector] = document
    return parents, owners.get(selector, selector)


def detail_context(data, index, selector):
    reviews, review_graph, effective = reviewed_facets(data, index)
    parents, facet_owner = context_parents(data, review_graph, selector)
    if selector.startswith("task:"):
        parents.setdefault(selector, []).append("file:" + index[selector]["file"])
    pending, selected = [selector], {}
    while pending:
        node = pending.pop()
        require(node in index, "unknown context subject: " + node)
        if node in selected:
            continue
        selected[node] = list(dict.fromkeys(parents.get(node, [])))
        pending.extend(selected[node])
    order = list(TopologicalSorter(selected).static_order())
    return {"subjects": order, "entries": {node: index[node] for node in order},
            "reviews": {node: reviews[node] for node in order if node in reviews},
            "facet_owner": facet_owner, "effective_facets": effective.get(facet_owner, {}),
            "limit": "Recorded source parents, source documents and explicit review inheritance. "
                     "Context keeps its own identity; no inherited relationship truth or acceptance. "
                     "Unrecorded context, live source identity and complete derived relationships require separate checks."}
