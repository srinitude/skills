"""Behavior contracts for input, intent, possibility, and coverage accounting."""
import copy
import json
import pathlib
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = SKILL_DIR / "evals" / "files"
ASSETS = SKILL_DIR / "assets"
sys.path.insert(0, str(SKILL_DIR / "scripts"))


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sample():
    return load(FIXTURES / "sample.evidence.json")


def catalogs():
    return load(ASSETS / "token-possibility-catalog.json"), load(ASSETS / "multimodal-input-catalog.json"), load(ASSETS / "quality-metric-catalog.json")


class TestInputAndIntentAccounting(unittest.TestCase):
    def test_sample_manifests_reconcile(self):
        from lib.accounting import validate_accounting
        possibility, inputs, metrics = catalogs()
        report = validate_accounting(sample(), possibility, inputs, metrics)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["input_accounting"]["status"], "pass")
        self.assertEqual(report["intent_accounting"]["status"], "pass")
        self.assertEqual(report["temporal_accounting"]["status"], "pass")

    def test_identical_format_can_have_negative_intent(self):
        from lib.accounting import validate_accounting
        document = sample()
        item = copy.deepcopy(document["input_manifest"]["items"][0])
        item.update({"id": "ref-negative", "locator": "negative.svg"})
        document["input_manifest"]["items"].append(item)
        document["intent_manifest"]["sources"].append({"source_id": "ref-negative", "roles": ["counterexample"], "decision_authority": "prohibited", "allowed_influence": ["no-token-influence"], "target_scope": ["whole-system"], "confidence_basis": "explicit-request", "status": "resolved"})
        report = validate_accounting(document, *catalogs())
        self.assertEqual(report["errors"], [])

    def test_negative_source_cannot_supply_exact_values(self):
        from lib.accounting import validate_accounting
        document = sample()
        intent = document["intent_manifest"]["sources"][0]
        intent.update({"roles": ["counterexample"], "decision_authority": "prohibited", "allowed_influence": ["exact-values"]})
        report = validate_accounting(document, *catalogs())
        self.assertIn("negative intent cannot supply positive token influence", " | ".join(report["errors"]))

    def test_material_unresolved_intent_blocks(self):
        from lib.accounting import validate_accounting
        document = sample()
        document["intent_manifest"]["conflicts"] = [{"id": "conflict-1", "material": True, "status": "unresolved", "evidence": "Two explicit source roles disagree."}]
        report = validate_accounting(document, *catalogs())
        self.assertIn("material intent conflict", " | ".join(report["errors"]))


class TestPossibilityAndContextAccounting(unittest.TestCase):
    def test_sample_expands_every_catalog_leaf_once(self):
        from lib.accounting import validate_accounting
        report = validate_accounting(sample(), *catalogs())
        accounting = report["possibility_accounting"]
        self.assertEqual(accounting["status"], "pass")
        self.assertEqual(accounting["accounted"], accounting["total"])
        self.assertEqual(accounting["duplicates"], [])

    def test_duplicate_override_blocks(self):
        from lib.accounting import validate_accounting
        document = sample()
        document["possibility_ledger"]["overrides"].append(copy.deepcopy(document["possibility_ledger"]["overrides"][0]))
        report = validate_accounting(document, *catalogs())
        self.assertIn("duplicate possibility override", " | ".join(report["errors"]))

    def test_missing_required_token_blocks_context(self):
        from lib.accounting import validate_accounting
        document = sample()
        document["context_requirements"][0]["tokens"] = []
        report = validate_accounting(document, *catalogs())
        self.assertIn("high-confidence requirement", " | ".join(report["errors"]))


if __name__ == "__main__":
    unittest.main()
