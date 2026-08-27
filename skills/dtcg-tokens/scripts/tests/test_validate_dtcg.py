"""Behavior tests for the DTCG validator command."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = SKILL_DIR / "scripts" / "validate_dtcg.py"
FIXTURES = SKILL_DIR / "evals" / "files"


def run_fixture(name):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES / name)],
        capture_output=True,
        text=True,
        timeout=30,
    )


def run_document(document):
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / "tokens.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True, timeout=30)


class TestValidTokens(unittest.TestCase):
    def test_valid_file_reports_resolved_tokens(self):
        result = run_fixture("sample.tokens.json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["valid"])
        self.assertGreaterEqual(report["token_count"], 12)
        self.assertGreaterEqual(report["resolved_references"], 4)
        self.assertIn("color", report["types"])

    def test_property_level_json_pointer_is_resolved(self):
        document = {
            "base": {"$type": "dimension", "$value": {"value": 16, "unit": "px"}},
            "derived": {"$type": "dimension", "$value": {"value": {"$ref": "#/base/$value/value"}, "unit": "rem"}},
        }
        result = run_document(document)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_group_extension_contributes_inherited_tokens(self):
        document = {
            "base": {"$type": "dimension", "space": {"$value": {"value": 8, "unit": "px"}}},
            "compact": {"$extends": "{base}"},
        }
        result = run_document(document)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["token_count"], 2)

    def test_single_gradient_stop_and_clamped_position_are_valid(self):
        document = {"wash": {"$type": "gradient", "$value": [{"color": {"colorSpace": "srgb", "components": [1, 0, 0]}, "position": 2}]}}
        result = run_document(document)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_alias_type_precedes_parent_group_type(self):
        document = {
            "ink": {"$type": "color", "$value": {"colorSpace": "srgb", "components": [0, 0, 0]}},
            "dimensions": {"$type": "dimension", "alias": {"$value": "{ink}"}},
        }
        result = run_document(document)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["types"]["color"], 2)


class TestInvalidTokens(unittest.TestCase):
    def test_invalid_name_is_rejected(self):
        result = run_fixture("invalid-name.tokens.json")
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertIn("invalid token or group name", " ".join(report["errors"]))

    def test_reference_cycle_is_rejected(self):
        result = run_fixture("cycle.tokens.json")
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertIn("reference cycle", " ".join(report["errors"]))

    def test_wrong_dimension_shape_is_rejected(self):
        result = run_fixture("invalid-dimension.tokens.json")
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertIn("dimension", " ".join(report["errors"]))

    def test_malformed_font_weight_returns_a_report(self):
        document = {"weight": {"$type": "fontWeight", "$value": {"value": 700}}}
        result = run_document(document)
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertIn("fontWeight", " ".join(report["errors"]))

    def test_srgb_component_outside_unit_range_is_rejected(self):
        document = {"red": {"$type": "color", "$value": {"colorSpace": "srgb", "components": [1.2, 0, 0]}}}
        result = run_document(document)
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertIn("component", " ".join(report["errors"]))

    def test_group_extension_cycle_is_rejected(self):
        document = {"a": {"$extends": "{b}"}, "b": {"$extends": "{a}"}}
        result = run_document(document)
        self.assertEqual(result.returncode, 1)
        self.assertIn("group extension cycle", " ".join(json.loads(result.stdout)["errors"]))

    def test_invalid_metadata_shapes_are_rejected(self):
        document = {"group": {"$description": 42, "token": {"$type": "number", "$value": 1}}}
        result = run_document(document)
        self.assertEqual(result.returncode, 1)
        self.assertIn("description must be a string", " ".join(json.loads(result.stdout)["errors"]))

    def test_nested_reference_type_mismatch_is_rejected(self):
        document = {
            "size": {"$type": "dimension", "$value": {"value": 4, "unit": "px"}},
            "bad": {"$type": "border", "$value": {"color": "{size}", "width": {"value": 1, "unit": "px"}, "style": "solid"}},
        }
        result = run_document(document)
        self.assertEqual(result.returncode, 1)
        self.assertIn("color", " ".join(json.loads(result.stdout)["errors"]))

    def test_missing_curly_reference_reports_instead_of_crashing(self):
        document = {"missing": {"$type": "color", "$value": "{does.not.exist}"}}
        result = run_document(document)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout, result.stderr)
        self.assertIn("reference target does not exist", " ".join(json.loads(result.stdout)["errors"]))

    def test_document_root_cannot_be_a_token(self):
        result = run_document({"$type": "number", "$value": 1})
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout, result.stderr)
        self.assertIn("document root must be a group", " ".join(json.loads(result.stdout)["errors"]))

    def test_standard_value_rejects_extra_properties(self):
        document = {"space": {"$type": "dimension", "$value": {"value": 8, "unit": "px", "extra": True}}}
        result = run_document(document)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported properties", " ".join(json.loads(result.stdout)["errors"]))


if __name__ == "__main__":
    unittest.main()
