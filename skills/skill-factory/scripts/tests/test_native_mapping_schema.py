"""Exercise native clause mappings without rewriting their evidence or claims."""
import copy
import json
import sys
import unittest
from cli import SCRIPTS
sys.path.insert(0, str(SCRIPTS))
from standardization_mapping import repair_mapping_json


def fixture():
    mapping = {"schema_version": 1, "skill": "clock-anchor", "coverage": 1.0,
        "source_files": ["SKILL.md"], "source_case_ids": ["CLOCK-001"],
        "adaptations": [{"source_concept": "Native invocation", "portable_concept": "Public invocation",
                         "preserved": ["Observed clock"]}],
        "clauses": [{"id": "CLOCK-MAP-001", "source_path": "SKILL.md", "source_lines": "1-3",
                     "meaning": "Read the observed clock", "targets": ["SKILL.md"], "action": "keep"}]}
    files = {"SKILL.md": b"---\nname: clock-anchor\n---\nRead the observed clock.\n",
        "evals/source-lineage.json": json.dumps({"source_files": [{"path": "SKILL.md", "sha256": "1" * 64}],
                                                "source_case_ids": ["CLOCK-001"]}).encode()}
    return mapping, files


def _reject_mapping(self, mapping, files):
    with self.assertRaisesRegex(ValueError, "source mapping"):
        self.check(mapping, files)


def _TestNativeMappingSchema_check(self, mapping, files):
    files["evals/source-mapping.json"] = json.dumps(mapping).encode()
    before = copy.deepcopy(files)
    try:
        repair_mapping_json(files)
    finally:
        self.assertEqual(files, before)

def _TestNativeMappingSchema_test_bound_native_mapping_keeps_all_bytes(self):
    self.check(*fixture())

def _TestNativeMappingSchema_test_source_and_case_binding_changes_reject(self):
    for field, value in [("source_files", ["unknown.md"]), ("source_case_ids", ["another-case"]),
                         ("skill", "another-skill")]:
        with self.subTest(field=field):
            mapping, files = fixture(); mapping[field] = value
            _reject_mapping(self, mapping, files)

def _TestNativeMappingSchema_test_invalid_native_clauses_and_targets_reject(self):
    for field, value in [("action", "drop"), ("targets", ["../outside"]),
                         ("source_lines", "3-1"), ("meaning", "")]:
        with self.subTest(field=field):
            mapping, files = fixture(); mapping["clauses"][0][field] = value
            _reject_mapping(self, mapping, files)
    mapping, files = fixture(); mapping["clauses"] *= 2
    with self.assertRaisesRegex(ValueError, "source mapping"):
        self.check(mapping, files)

def _TestNativeMappingSchema_test_missing_required_schema_content_rejects(self):
    for field in ["adaptations", "clauses", "coverage"]:
        with self.subTest(field=field):
            mapping, files = fixture(); del mapping[field]
            _reject_mapping(self, mapping, files)


class TestNativeMappingSchema(unittest.TestCase):
    check = _TestNativeMappingSchema_check
    test_bound_native_mapping_keeps_all_bytes = _TestNativeMappingSchema_test_bound_native_mapping_keeps_all_bytes
    test_source_and_case_binding_changes_reject = _TestNativeMappingSchema_test_source_and_case_binding_changes_reject
    test_invalid_native_clauses_and_targets_reject = _TestNativeMappingSchema_test_invalid_native_clauses_and_targets_reject
    test_missing_required_schema_content_rejects = _TestNativeMappingSchema_test_missing_required_schema_content_rejects


if __name__ == "__main__":
    unittest.main()
