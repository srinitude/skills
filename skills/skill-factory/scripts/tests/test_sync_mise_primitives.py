"""Behavior tests for version-bound Mise primitive catalog updates."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run


def schema():
    return {
        "properties": {"tasks": {}, "tools": {}, "min_version": {}},
        "$defs": {
            "task_props": {"properties": {"run": {}, "depends": {}}},
            "task": {"oneOf": [{}, {}, {"allOf": [{}, {
                "properties": {"extends": {}}}]}]},
            "task_config": {"properties": {"dir": {}}},
            "tool_options": {"properties": {"version": {}, "os": {}}},
            "tool": {"oneOf": [{}, {"allOf": [{}, {
                "properties": {"lazy": {}, "postinstall": {}}}]}]},
        },
    }


class TestSyncMisePrimitives(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        assets = self.root / "assets"
        assets.mkdir()
        self.schema_path = self.root / "schema.json"
        self.schema_path.write_text(json.dumps(schema()), encoding="utf-8")
        (assets / "mise-primitives-catalog.json").write_text(
            json.dumps({"version": "old", "groups": {}}), encoding="utf-8")
        self.decisions = assets / "mise-primitives.json"
        self.decisions.write_text('{"keep":"unchanged"}', encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def invoke(self, *extra):
        return run("sync_mise_primitives.py", self.root, "--version", "9.9.9",
                   "--schema-file", self.schema_path, *extra)

    def test_update_extracts_every_supported_schema_field(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        catalog = json.loads((self.root / "assets" /
                              "mise-primitives-catalog.json").read_text())
        self.assertEqual(catalog["version"], "9.9.9")
        self.assertEqual(catalog["groups"]["config"],
                         ["min_version", "tasks", "tools"])
        self.assertIn("extends", catalog["groups"]["task"])
        self.assertIn("postinstall", catalog["groups"]["tool"])

    def test_update_does_not_rewrite_domain_dispositions(self):
        before = self.decisions.read_bytes()
        result = self.invoke()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.decisions.read_bytes(), before)

    def test_check_reports_stale_catalog_without_writing(self):
        before = (self.root / "assets" /
                  "mise-primitives-catalog.json").read_bytes()
        result = self.invoke("--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("stale", result.stdout)
        self.assertEqual((self.root / "assets" /
                          "mise-primitives-catalog.json").read_bytes(), before)

    def test_empty_schema_fails_without_replacing_catalog(self):
        before = (self.root / "assets" /
                  "mise-primitives-catalog.json").read_bytes()
        self.schema_path.write_text("{}", encoding="utf-8")
        result = self.invoke()
        self.assertEqual(result.returncode, 2)
        self.assertIn("missing primitive group", result.stdout)
        self.assertEqual((self.root / "assets" /
                          "mise-primitives-catalog.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
