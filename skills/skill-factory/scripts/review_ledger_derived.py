"""Project declared source structure and reading order, never execution readiness."""
import json
from graphlib import TopologicalSorter

from agentic_request_contract import read_json
from review_ledger_context import require
from review_ledger_source import check_capture, unique


def relation(identifier, kind, provider, consumer, meaning, condition, basis_kind):
    return {"id": identifier, "type": kind, "from": provider, "to": consumer,
            "basis": [provider, consumer], "meaning": meaning, "condition": condition,
            "review_state": "reviewed", "reviewer": "Captured declaration predicate; no semantic or execution acceptance",
            "basis_kind": basis_kind}


def source_edges(data):
    check_capture(data)
    rows = sorted(data["source_records"], key=lambda row: row["byte_start"])
    lines = {row["line_start"]: "source:" + row["id"] for row in rows}
    documents = unique(data["packet_documents"], "name", "document identity")
    require("source-links.json" in documents, "missing captured source definition inventory")
    definitions = read_json(documents["source-links.json"]["text"])["definitions"]
    condition = "Declared source structure only. Retain whole-source and parent conditions; no execution or acceptance claim."
    for row in rows:
        current = "source:" + row["id"]
        yield relation("STRUCT:group:" + row["id"], "part-of", current, "group:" + row["owner_group"],
                       "The captured row belongs to its declared owner group.", condition, "captured-source-structure")
        heading = row["section"]["line"]
        require(type(heading) is int and heading in lines, "missing source section context")
        if heading != row["line_start"]:
            yield relation("STRUCT:section:" + row["id"], "contextualizes", lines[heading], current,
                           "The declared containing heading supplies source context.", condition, "captured-source-structure")
        for clause in row.get("clauses", []):
            yield relation("STRUCT:parent:" + clause["id"], "part-of", "clause:" + clause["id"], current,
                           "The clause is a retained component; its parent conjunction stays active.", condition, "captured-source-structure")
        for number, label in enumerate(row["source_references"]):
            require(label in definitions, "missing source reference definition: " + label)
            line = definitions[label]["source_line"]
            require(type(line) is int and line in lines, "missing source definition row")
            edge = relation(f"STRUCT:reference:{row['id']}:{number}", "references", current, lines[line],
                            "The declared label resolves to its captured definition.", condition, "captured-source-structure")
            yield {**edge, "source_label": label, "reference_ordinal": number}


def prerequisites(record, default=()):
    values = record.get("reading_prerequisites", list(default))
    require(isinstance(values, list) and all(isinstance(item, str) and item for item in values)
            and len(values) == len(set(values)), "invalid or duplicate reading prerequisite")
    return values


def reading_graph(data, index):
    graph, kinds = {}, {}
    for group in data.get("source_owner_groups", []):
        node = "group:" + group["id"]
        graph[node] = ["group:" + item for item in prerequisites(group)]
        kinds[node] = "declared-group-reading"
    observations = data.get("dependency_snapshot", {}).get("files", {})
    for node, record in index.items():
        if not node.startswith("file:"):
            continue
        name, baseline = record["path"], record["baseline"] or {}
        default = ["SKILL.md"] if name != "SKILL.md" else []
        providers = set(prerequisites(baseline, default))
        kinds[node] = "historical-file-reading-declaration" if baseline else "body-first-unreviewed-file"
        observed = observations.get(name)
        if observed is not None:
            require(record["current"] is not None and observed["sha256"] == record["current"]["sha256"],
                    "dependency observation differs from recorded current file")
            old_imports = {path for item in baseline.get("syntax_imports", []) for path in item["resolved_local_files"]}
            current_imports = {path for item in observed["syntax_imports"] for path in item["resolved_local_files"]}
            providers = (providers - old_imports) | current_imports
            kinds[node] = "recorded-current-import-reading"
        graph[node] = ["file:" + path for path in sorted(providers)]
    require(all(provider in graph for providers in graph.values() for provider in providers), "unknown reading prerequisite")
    return graph, kinds


def reading_edges(data, index):
    graph, kinds = reading_graph(data, index)
    for consumer in TopologicalSorter(graph).static_order():
        for provider in graph[consumer]:
            identifier = "READ:" + json.dumps([provider, consumer], ensure_ascii=False, separators=(",", ":"))
            edge = relation(identifier, "read-before", provider, consumer,
                           "Read the recorded provider before its dependent subject.",
                           "No execution, effect, acceptance or live-file readiness is asserted. Historical declarations "
                           "retain that scope. Current import observations are syntax candidates, including conditional imports; "
                           "dynamic imports, external resolution and semantic dependencies need separate review.", kinds[consumer])
            record = index[consumer]
            declaration = record if consumer.startswith("group:") else record["baseline"] or {}
            yield {**edge, "declaration_scope": "captured-group" if consumer.startswith("group:") else "historical-file",
                   "declared_context": {key: declaration[key] for key in
                       ("reading_prerequisites", "reading_order_basis", "reading_order_limit") if key in declaration}}


def derived_edges(data, index):
    profile = data["semantic_model"].get("derived_relationships")
    if profile is None:
        return
    require(isinstance(profile, dict) and type(profile.get("version")) is int and profile["version"] == 1,
            "unsupported derived relationship profile")
    require(isinstance(profile.get("rules"), dict) and set(profile["rules"]) ==
            {"clause-parent", "row-group", "section-context", "reference-definition"},
            "unsupported derived source rule; preserve it for implementation and review")
    yield from source_edges(data)
    yield from reading_edges(data, index)
