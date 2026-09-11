"""Captured-byte consistency is distinct from live-source and semantic proof."""
import copy
import hashlib
import json
import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_ledger_source import check_capture, check_sources


def _TestCapturedSource_setUp(self):
    text = "λ first\r\nSecond line\n"
    raw = text.encode()
    digest = hashlib.sha256(raw).hexdigest()
    rows, start = [], 0
    for number, line in enumerate(raw.splitlines(keepends=True), 1):
        rows.append({"id": str(number), "source_sha256": digest,
                     "byte_start": start, "byte_end_exclusive": start + len(line),
                     "line_start": number, "line_end": number,
                     "quote": line.decode(), "clauses": []})
        start += len(line)
    rows[0]["clauses"] = [{"id": "first", "byte_start": 0,
                             "byte_end_exclusive": 2, "quote": "λ"}]
    self.data = {"source": {"sha256": digest, "bytes": len(raw), "lines": 2},
                 "packet_documents": [{"name": "source.txt", "text": text,
                                       "sha256": digest, "bytes": len(raw), "lines": 2}],
                 "source_records": rows}

def _TestCapturedSource_test_all_source_bytes_and_clause_locators_are_checked(self):
    result = check_capture(self.data)
    self.assertEqual(result["source_bytes"], len(self.data["packet_documents"][0]["text"].encode()))
    self.assertEqual(result["source_records"], 2)
    self.assertEqual(result["clauses"], 1)
    self.assertEqual(result["scope"], "captured bytes and locators only")
    self.assertEqual(self.data["packet_documents"][0]["text"], "λ first\r\nSecond line\n")

def _TestCapturedSource_test_missing_capture_and_duplicate_identities_reject(self):
    for change in [lambda d: d.update(packet_documents=[]),
                   lambda d: d["packet_documents"].append(copy.deepcopy(d["packet_documents"][0])),
                   lambda d: d["source_records"][1].update(id="1"),
                   lambda d: d["source_records"][1].update(clauses=[{"id": "first", "quote": "Second", "byte_start": d["source_records"][1]["byte_start"], "byte_end_exclusive": d["source_records"][1]["byte_start"] + 6}])]:
        candidate = copy.deepcopy(self.data)
        change(candidate)
        with self.assertRaises(ValueError):
            check_capture(candidate)

def _TestCapturedSource_test_omitted_changed_or_overlapping_source_rows_reject_then_recover(self):
    for change in [lambda d: d["source_records"].pop(),
                   lambda d: d["source_records"][0].update(quote="altered"),
                   lambda d: d["source_records"][1].update(byte_start=0),
                   lambda d: d["source_records"][1].update(line_start=1),
                   lambda d: d["source_records"][0].update(source_sha256="0" * 64)]:
        candidate = copy.deepcopy(self.data)
        change(candidate)
        with self.assertRaises(ValueError):
            check_capture(candidate)
    self.test_all_source_bytes_and_clause_locators_are_checked()

def _TestCapturedSource_test_mismatched_document_and_clause_bindings_reject_then_recover(self):
    for change in [lambda d: d["packet_documents"][0].update(sha256="0" * 64),
                   lambda d: d["packet_documents"][0].update(bytes=0),
                   lambda d: d["packet_documents"][0].update(lines=1),
                   lambda d: d["source_records"][0]["clauses"][0].update(quote="x"),
                   lambda d: d["source_records"][0]["clauses"][0].update(byte_end_exclusive=999),
                   lambda d: d["source_records"][0]["clauses"][0].update(byte_start=False)]:
        candidate = copy.deepcopy(self.data)
        change(candidate)
        with self.assertRaises(ValueError):
            check_capture(candidate)
    self.test_all_source_bytes_and_clause_locators_are_checked()


class TestCapturedSource(unittest.TestCase):
    setUp = _TestCapturedSource_setUp
    test_all_source_bytes_and_clause_locators_are_checked = _TestCapturedSource_test_all_source_bytes_and_clause_locators_are_checked
    test_omitted_changed_or_overlapping_source_rows_reject_then_recover = _TestCapturedSource_test_omitted_changed_or_overlapping_source_rows_reject_then_recover
    test_mismatched_document_and_clause_bindings_reject_then_recover = _TestCapturedSource_test_mismatched_document_and_clause_bindings_reject_then_recover
    test_missing_capture_and_duplicate_identities_reject = _TestCapturedSource_test_missing_capture_and_duplicate_identities_reject


def _TestLiveSource_setUp(self):
    TestCapturedSource.setUp(self)
    temporary = tempfile.TemporaryDirectory()
    self.addCleanup(temporary.cleanup)
    self.root = Path(temporary.name)
    self.data["source_mapping_defaults"] = {"preserve": True, "limit": 1}
    inventory = {"source_sha256": self.data["source"]["sha256"],
                 "source_bytes": self.data["source"]["bytes"], "source_lines": 2,
                 "records": copy.deepcopy(self.data["source_records"]),
                 "mapping_defaults": copy.deepcopy(self.data["source_mapping_defaults"])}
    for name, text in [("coverage.json", json.dumps(inventory)), ("empty-context.txt", "")]:
        raw = text.encode()
        self.data["packet_documents"].append({"name": name, "text": text,
            "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw),
            "lines": len(raw.splitlines())})
    expected = []
    for document in self.data["packet_documents"]:
        path = self.root / document["name"]
        path.write_bytes(document["text"].encode())
        expected.append({"name": document["name"], "path": str(path), "sha256": document["sha256"]})
    original = self.root / "original.txt"
    original.write_bytes(self.data["packet_documents"][0]["text"].encode())
    self.request = {"expected_documents": expected, "inventory_document": "coverage.json",
                    "original_source": {"path": str(original), "sha256": self.data["source"]["sha256"]}}

def _TestLiveSource_test_supplied_live_inventory_original_and_frozen_records_pass(self):
    before = {p.name: p.read_bytes() for p in self.root.iterdir()}
    result = check_sources(self.data, self.request)
    self.assertEqual(result["documents"], 3)
    self.assertEqual(result["source_records"], 2)
    self.assertEqual(result["scope"], "supplied live bindings and frozen source inventory only")
    self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

def _TestLiveSource_test_dependency_order_can_differ_from_frozen_source_order(self):
    self.data["source_records"].reverse()
    self.assertEqual(check_sources(self.data, self.request)["source_records"], 2)

def _TestLiveSource_test_frozen_defaults_preserve_values_types_and_presence(self):
    for change in [lambda d: d.pop("source_mapping_defaults"),
                   lambda d: d["source_mapping_defaults"].update(preserve=1),
                   lambda d: d["source_mapping_defaults"].update(limit=1.0),
                   lambda d: d["source_mapping_defaults"].update(extra="unbound")]:
        changed = copy.deepcopy(self.data)
        change(changed)
        with self.assertRaises(ValueError):
            check_sources(changed, self.request)
    check_sources(self.data, self.request)

def _TestLiveSource_test_external_bindings_reject_capture_omission_live_drift_and_symlink(self):
    changed = copy.deepcopy(self.data)
    changed["packet_documents"].pop()
    with self.assertRaises(ValueError):
        check_sources(changed, self.request)
    for path in [self.root / "source.txt", self.root / "original.txt"]:
        valid = path.read_bytes()
        path.write_bytes(valid + b"changed")
        with self.assertRaises(ValueError):
            check_sources(self.data, self.request)
        path.write_bytes(valid)
    path = self.root / "empty-context.txt"
    path.unlink()
    path.symlink_to(self.root / "source.txt")
    with self.assertRaises(ValueError):
        check_sources(self.data, self.request)
    path.unlink()
    path.write_bytes(b"")
    check_sources(self.data, self.request)

def _TestLiveSource_test_frozen_inventory_rejects_renamed_omitted_or_rebound_records(self):
    for change in [lambda d: d["source_records"][0].update(id="renamed"),
                   lambda d: d["source_records"][0].update(clauses=[]),
                   lambda d: d["source_records"][0].update(kind="discarded-context")]:
        changed = copy.deepcopy(self.data)
        change(changed)
        check_capture(changed)
        with self.assertRaises(ValueError):
            check_sources(changed, self.request)
    expected = copy.deepcopy(self.request)
    expected["expected_documents"][0]["sha256"] = "0" * 64
    with self.assertRaises(ValueError):
        check_sources(self.data, expected)
    check_sources(self.data, self.request)


class TestLiveSource(unittest.TestCase):
    setUp = _TestLiveSource_setUp
    test_supplied_live_inventory_original_and_frozen_records_pass = _TestLiveSource_test_supplied_live_inventory_original_and_frozen_records_pass
    test_dependency_order_can_differ_from_frozen_source_order = _TestLiveSource_test_dependency_order_can_differ_from_frozen_source_order
    test_frozen_defaults_preserve_values_types_and_presence = _TestLiveSource_test_frozen_defaults_preserve_values_types_and_presence
    test_external_bindings_reject_capture_omission_live_drift_and_symlink = _TestLiveSource_test_external_bindings_reject_capture_omission_live_drift_and_symlink
    test_frozen_inventory_rejects_renamed_omitted_or_rebound_records = _TestLiveSource_test_frozen_inventory_rejects_renamed_omitted_or_rebound_records


if __name__ == "__main__":
    unittest.main()
