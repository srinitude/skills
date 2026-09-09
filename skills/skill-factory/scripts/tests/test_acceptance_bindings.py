"""Source coverage rejects altered or omitted bytes before downstream acceptance."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_use_case_contract import contract, write_skill

SOURCE = b"# Rules\nKeep scope. Keep evidence.\n"


def digest(value):
    return hashlib.sha256(value).hexdigest()


def coverage():
    rows, offset = [], 0
    for line, value in enumerate(SOURCE.splitlines(keepends=True), 1):
        record = {"id": f"ROW-{line}", "kind": "context:heading" if line == 1 else "obligation",
                  "line_start": line, "line_end": line, "byte_start": offset,
                  "byte_end_exclusive": offset + len(value), "quote": value.decode(),
                  "source_sha256": digest(SOURCE)}
        rows.append(record)
        offset += len(value)
    rows[1]["clauses"] = [
        {"id": "ROW-2-C1", "byte_start": 8, "byte_end_exclusive": 19, "quote": "Keep scope."},
        {"id": "ROW-2-C2", "byte_start": 20, "byte_end_exclusive": 34, "quote": "Keep evidence."},
    ]
    return {"source_sha256": digest(SOURCE), "source_bytes": len(SOURCE),
            "source_lines": 2, "records": rows}


class TestSourceCoverage(unittest.TestCase):
    def invoke(self, mutate=None, source=SOURCE, bind_original=False):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve() / "release-notes"
            root.mkdir()
            write_skill(root, contract())
            data = coverage()
            original = json.dumps(data).encode()
            if mutate:
                mutate(data)
            raw = json.dumps(data).encode()
            source_path, map_path = root.parent / "source.md", root.parent / "coverage.json"
            source_path.write_bytes(source)
            map_path.write_bytes(raw)
            before = {p: p.read_bytes() for p in Path(temp).rglob('*') if p.is_file()}
            result = run("check_use_case_contract.py", root, "--source", source_path,
                         "--coverage", map_path, "--source-sha256", digest(SOURCE),
                         "--coverage-sha256", digest(original if bind_original else raw))
            self.assertEqual(before, {p: p.read_bytes() for p in Path(temp).rglob('*') if p.is_file()})
            self.assertNotIn("Traceback", result.stderr)
            return result

    def test_complete_coverage_can_progress_without_claiming_semantic_acceptance(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("coverage mechanics", result.stdout)

    def test_source_bytes_cannot_be_replaced(self):
        result = self.invoke(source=SOURCE + b"Changed.")
        self.assertEqual(result.returncode, 1)
        self.assertIn("source digest", result.stdout)

    def test_frozen_coverage_cannot_be_reclassified(self):
        result = self.invoke(lambda d: d["records"][1].update(kind="context:note"), bind_original=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("coverage digest", result.stdout)

    def test_missing_rows_quotes_clauses_and_duplicate_ids_are_rejected(self):
        edits = [lambda d: d["records"].pop(),
                 lambda d: d["records"][1].update(quote="Changed."),
                 lambda d: d["records"][1]["clauses"].pop(),
                 lambda d: d["records"][1]["clauses"].append(copy.deepcopy(d["records"][1]["clauses"][0])),
                 lambda d: d["records"][1].update(id="ROW-1"),
                 lambda d: d["records"][1].update(byte_start=True),
                 lambda d: d["records"][1].update(line_end=5)]
        for edit in edits:
            with self.subTest(edit=edit):
                result = self.invoke(edit)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_partial_bindings_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, contract())
            result = run("check_use_case_contract.py", root, "--source-sha256", digest(SOURCE))
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_restoration_allows_the_same_control_again(self):
        self.assertEqual(self.invoke(source=b"tampered").returncode, 1)
        self.assertEqual(self.invoke().returncode, 0)
