"""Check captured document bytes and complete source/parent/clause locators."""
import hashlib
import json
from pathlib import Path

from agentic_request_contract import read_json

from review_ledger_context import require


def unique(items, key, label):
    result = {}
    for item in items:
        identifier = item[key]
        require(isinstance(identifier, str) and identifier and identifier not in result,
                "missing or duplicate " + label)
        result[identifier] = item
    return result


def captured_documents(data):
    documents = unique(data["packet_documents"], "name", "document identity")
    require(documents, "missing captured documents")
    captured = {}
    for name, record in documents.items():
        raw = record["text"].encode("utf-8")
        require(hashlib.sha256(raw).hexdigest() == record["sha256"], "captured document digest mismatch: " + name)
        require(type(record["bytes"]) is int and len(raw) == record["bytes"], "captured document byte count mismatch")
        require(type(record["lines"]) is int and len(raw.splitlines()) == record["lines"], "captured document line count mismatch")
        captured[name] = raw
    return documents, captured


def span(record, raw, lower, upper):
    start, end = record["byte_start"], record["byte_end_exclusive"]
    require(type(start) is int and type(end) is int and lower <= start < end <= upper,
            "invalid source or clause byte range")
    require(raw[start:end] == record["quote"].encode("utf-8"), "source or clause quotation mismatch")
    return start, end


def line_boundaries(raw):
    boundaries, offset = [0], 0
    for line in raw.splitlines(keepends=True):
        offset += len(line)
        boundaries.append(offset)
    return boundaries


def check_rows(data, raw):
    records = unique(data["source_records"], "id", "source identity")
    clauses, offset, boundaries = [], 0, line_boundaries(raw)
    require(records, "missing captured source records")
    for row in sorted(records.values(), key=lambda item: item["byte_start"]):
        start, end = span(row, raw, offset, len(raw))
        require(start == offset, "source rows omit or overlap bytes")
        first, last = row["line_start"], row["line_end"]
        require(type(first) is int and type(last) is int and 1 <= first <= last < len(boundaries), "invalid source line range")
        require(boundaries[first - 1] == start and boundaries[last] == end, "source line/byte range mismatch")
        require(row["source_sha256"] == data["source"]["sha256"], "source row digest mismatch")
        for clause in row.get("clauses", []):
            span(clause, raw, start, end)
            clauses.append(clause)
        offset = end
    require(offset == len(raw), "source records omit final source bytes")
    unique(clauses, "id", "clause identity")
    return len(records), len(clauses)


def check_capture(data):
    documents, captured = captured_documents(data)
    source = data["source"]
    matches = [name for name, record in documents.items() if record["sha256"] == source["sha256"]]
    require(matches, "missing matching captured source document")
    raw = captured[matches[0]]
    require(type(source["bytes"]) is int and len(raw) == source["bytes"], "source byte count mismatch")
    require(type(source["lines"]) is int and len(raw.splitlines()) == source["lines"], "source line count mismatch")
    rows, clauses = check_rows(data, raw)
    return {"documents": len(documents), "document_bytes": sum(map(len, captured.values())),
            "source_sha256": source["sha256"], "source_bytes": len(raw), "source_records": rows,
            "clauses": clauses, "scope": "captured bytes and locators only",
            "limit": "Checks the documents present and complete source byte partition. "
                     "No independent expected document inventory, live-original verification, "
                     "semantic completeness, evidence acceptance or protected-write claim."}


def read_file(binding):
    path = Path(binding["path"])
    require(path.is_absolute() and path.is_file() and not path.is_symlink(),
            "live source input must be an absolute regular non-symlink file")
    return path.read_bytes()


def frozen_inventory(data, document):
    inventory = read_json(document["text"])
    for key, value in [("source_sha256", data["source"]["sha256"]),
                       ("source_bytes", data["source"]["bytes"]), ("source_lines", data["source"]["lines"])]:
        require(type(inventory.get(key)) is type(value) and inventory[key] == value,
                "frozen inventory source identity mismatch")
    expected = {"records": unique(inventory["records"], "id", "frozen source identity")}
    current = {"records": unique(data["source_records"], "id", "source identity")}
    if "mapping_defaults" in inventory:
        expected["mapping_defaults"] = inventory["mapping_defaults"]
    if "source_mapping_defaults" in data:
        current["mapping_defaults"] = data["source_mapping_defaults"]
    require(json.dumps(current, sort_keys=True, ensure_ascii=False, allow_nan=False)
            == json.dumps(expected, sort_keys=True, ensure_ascii=False, allow_nan=False),
            "source records or defaults differ from the supplied frozen inventory")


def check_source_capture(data, request, files):
    result = check_capture(data)
    captured = {document["name"]: document for document in data["packet_documents"]}
    expected = unique(request["expected_documents"], "name", "expected document identity")
    require(set(expected) == set(captured), "supplied document inventory differs from capture")
    for name, binding in expected.items():
        require(binding["sha256"] == captured[name]["sha256"], "supplied document digest differs from capture")
        require(checked_capture(binding, files) == captured[name]["text"].encode(), "live document differs from captured bytes")
    original = request["original_source"]
    require(original["sha256"] == data["source"]["sha256"], "supplied original digest differs from captured source")
    source = next(document for document in captured.values() if document["sha256"] == original["sha256"])
    require(checked_capture(original, files) == source["text"].encode(), "original source differs from captured source bytes")
    require(request["inventory_document"] in captured, "missing supplied frozen inventory document")
    frozen_inventory(data, captured[request["inventory_document"]])
    return {**result, "scope": "supplied live bindings and frozen source inventory only",
            "limit": "Exact supplied document inventory, live document/original bytes and frozen source records. "
                     "The caller must establish the bindings' independent authority. No semantic completeness, "
                     "human or evidence acceptance, cross-file transaction, hostile-writer isolation or protected-write claim."}


def checked_capture(binding, files):
    raw = files[binding["path"]]
    require(hashlib.sha256(raw).hexdigest() == binding["sha256"], "captured live input digest mismatch")
    return raw


def check_sources(data, request):
    bindings = [*request["expected_documents"], request["original_source"]]
    files = {item["path"]: read_file(item) for item in bindings}
    return check_source_capture(data, request, files)
