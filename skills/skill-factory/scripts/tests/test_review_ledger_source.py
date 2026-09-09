"""Captured-byte consistency is distinct from live-source and semantic proof."""
import copy
import hashlib
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_ledger_source import check_capture


class TestCapturedSource(unittest.TestCase):
    def setUp(self):
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

    def test_all_source_bytes_and_clause_locators_are_checked(self):
        result = check_capture(self.data)
        self.assertEqual(result["source_bytes"], len(self.data["packet_documents"][0]["text"].encode()))
        self.assertEqual(result["source_records"], 2)
        self.assertEqual(result["clauses"], 1)
        self.assertEqual(result["scope"], "captured bytes and locators only")
        self.assertEqual(self.data["packet_documents"][0]["text"], "λ first\r\nSecond line\n")

    def test_omitted_changed_or_overlapping_source_rows_reject_then_recover(self):
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

    def test_mismatched_document_and_clause_bindings_reject_then_recover(self):
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

    def test_missing_capture_and_duplicate_identities_reject(self):
        for change in [lambda d: d.update(packet_documents=[]),
                       lambda d: d["packet_documents"].append(copy.deepcopy(d["packet_documents"][0])),
                       lambda d: d["source_records"][1].update(id="1"),
                       lambda d: d["source_records"][1].update(clauses=[{"id": "first", "quote": "Second", "byte_start": d["source_records"][1]["byte_start"], "byte_end_exclusive": d["source_records"][1]["byte_start"] + 6}])]:
            candidate = copy.deepcopy(self.data)
            change(candidate)
            with self.assertRaises(ValueError):
                check_capture(candidate)


if __name__ == "__main__":
    unittest.main()
