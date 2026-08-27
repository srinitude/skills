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


if __name__ == "__main__":
    unittest.main()
