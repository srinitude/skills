"""Resolve higher-order records and their required two-dimensional view."""
import hashlib
import json
from pathlib import Path

from human_combinations import spaces
from human_matrix_records import (canonicalize, correspondences, extensions, groups,
                                  interactions, occurrences, records, shape)
from source_coverage import bound_bytes, parse_json, require


def inspect(path, expected, inventory, concepts):
    raw = bound_bytes(path, expected, "matrix")
    document = parse_json(raw)
    shape(document, {"version", "comparator", "locale", "extensions", "correspondences", "occurrences",
                     "groups", "records", "interactions", "selectors"}, "matrix")
    require(type(document["version"]) is int and document["version"] == 1, "unsupported matrix schema version")
    require(document["comparator"] == "unicode-codepoint" and document["locale"] == "und",
            "matrix needs its declared unicode-codepoint comparator and und locale")
    resolved = records(document["records"], Path(path).resolve().parent)
    extensions(document["extensions"], concepts, resolved)
    correspondences(document["correspondences"], concepts, resolved)
    instances = occurrences(document["occurrences"], concepts, resolved)
    selections = groups(document["groups"], instances)
    interactions(document["interactions"], selections.keys() | instances.keys(), resolved)
    selectors = spaces(document["selectors"], concepts, inventory["catalogs"], resolved)
    canonical = canonicalize(document)
    digest = hashlib.sha256(json.dumps(canonical, ensure_ascii=False, sort_keys=True,
                                      separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    ids = {item["concept"] for item in instances.values()} | {item["id"] for item in document["extensions"]}
    return {**inventory, "matrix_sha256": expected, "canonical_sha256": digest, "matrix": canonical,
            "concepts": {identifier: concepts[identifier] for identifier in sorted(ids)}, "records": resolved,
            "spaces": selectors, "view": [{"interaction": item["id"], "study": item["study"], "work": item["work"]}
                                          for item in canonical["interactions"]],
            "coverage": {"vocabulary": "complete-declared-inventories", "representation": "validated-records",
                         "evidence": "not-evaluated", "executed_tests": "not-evaluated"},
            "enumeration": {"state": "not-requested"}, "acceptance": "pending"}
