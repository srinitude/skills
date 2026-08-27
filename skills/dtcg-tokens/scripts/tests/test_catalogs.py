"""Contracts for the input, token, metric, and time catalogs."""
import json
import pathlib
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
ASSETS = SKILL_DIR / "assets"
TYPES = {"color", "dimension", "fontFamily", "fontWeight", "duration", "cubicBezier", "number", "strokeStyle", "border", "transition", "shadow", "gradient", "typography"}
sys.path.insert(0, str(SKILL_DIR / "scripts"))


def load(name):
    return json.loads((ASSETS / name).read_text(encoding="utf-8"))


class TestTokenPossibilityCatalog(unittest.TestCase):
    def test_catalog_has_full_standard_surface(self):
        catalog = load("token-possibility-catalog.json")
        domains = catalog["domains"]
        self.assertEqual(set(domains["dtcg-type"]), TYPES)
        self.assertGreaterEqual(len(domains["design-family"]), 20)
        self.assertGreaterEqual(len(domains["state"]), 35)
        self.assertGreaterEqual(len(domains["mode"]), 20)
        self.assertIn("invalid-structure", domains["value-domain-partition"])
        self.assertEqual(len(catalog["dispositions"]), 7)

    def test_catalog_leaf_ids_are_unique_and_counted(self):
        from lib.catalogs import catalog_leaves
        catalog = load("token-possibility-catalog.json")
        leaves = catalog_leaves(catalog)
        self.assertEqual(len(leaves), len(set(leaves)))
        self.assertEqual(catalog["leaf_count"], len(leaves))
        self.assertGreater(len(leaves), 150)


class TestMultimodalCatalog(unittest.TestCase):
    def test_catalog_partitions_format_and_intent(self):
        catalog = load("multimodal-input-catalog.json")
        facets = catalog["input_facets"]
        intents = catalog["intent_facets"]
        self.assertIn("unknown-or-future", catalog["source_classes"])
        self.assertIn("native-visual-inspection", facets["access-method"])
        self.assertIn("negative", catalog["intent_classes"])
        self.assertIn("counterexample", intents["source-role"])
        self.assertIn("exact-values", intents["allowed-influence"])
        self.assertIn("unresolved", intents["decision-authority"])

    def test_catalog_enumerates_mixed_and_live_inputs(self):
        catalog = load("multimodal-input-catalog.json")
        classes = catalog["source_classes"]
        required = {"written-symbolic", "documents-pages", "static-visual", "time-based-visual", "audio", "editable-creative", "code-executable", "structured-data", "interactive-runtime", "spatial-physical", "accessibility-alternate", "metadata-provenance", "collections-mixed", "unknown-or-future"}
        self.assertEqual(set(classes), required)


class TestMetricAndTimeCatalogs(unittest.TestCase):
    def test_metric_catalog_has_all_claim_families(self):
        catalog = load("quality-metric-catalog.json")
        families = {item["family"] for item in catalog["metrics"]}
        required = {"work-integrity", "design-integrity", "automated-genericity", "source-specificity", "corpus-distinctiveness", "visual-integrity", "temporal-currency"}
        self.assertEqual(families, required)
        self.assertEqual(len({item["id"] for item in catalog["metrics"]}), len(catalog["metrics"]))
        self.assertTrue(all("threshold" in item and "veto" in item for item in catalog["metrics"]))

    def test_time_policy_requires_one_current_anchor(self):
        policy = load("current-date-policy.json")
        self.assertEqual(policy["anchor_count"], 1)
        self.assertTrue(policy["current_claims_require_live_primary_source"])
        self.assertTrue(policy["show_pinned_and_current_versions"])
        self.assertEqual(policy["future_dated_evidence"], "blocked")


if __name__ == "__main__":
    unittest.main()
