"""Check captured document bytes and complete source/parent/clause locators."""
import hashlib

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
