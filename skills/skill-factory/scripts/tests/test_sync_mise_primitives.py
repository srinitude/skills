"""Retain schema field extraction and disposition checks under current file reviews."""
import json
import unittest

import test_catalog_review as reviewed


class TestSyncMisePrimitives(unittest.TestCase):
    setUp = reviewed.TestCatalogReview.setUp
    prepare = reviewed.TestCatalogReview.prepare
    package = reviewed.TestCatalogReview.package

    def invoke(self, *extra):
        return reviewed.TestCatalogReview.invoke(self, *extra, review='--check' not in extra)

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
        self.assertIn("missing primitive group", result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual((self.root / "assets" /
                          "mise-primitives-catalog.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
