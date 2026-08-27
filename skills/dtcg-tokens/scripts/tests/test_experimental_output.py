import copy
import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "evals" / "files"
sys.path.insert(0, str(ROOT / "scripts"))


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ExperimentalOutputTests(unittest.TestCase):
    def test_strategy_catalog_pins_selection_minimums(self):
        catalog = json.loads((ROOT / "assets" / "exploration-strategy-catalog.json").read_text(encoding="utf-8"))
        policy = catalog["selection_policy"]
        ids = [item["id"] for item in catalog["strategies"]]
        self.assertEqual(policy["minimum_retained_tokens"], 2)
        self.assertEqual(policy["minimum_distinct_strategies"], 2)
        self.assertEqual(policy["selection_order"], ids)
        self.assertEqual(len(ids), len(set(ids)))

    def test_sample_embeds_a_required_experimental_partition(self):
        from lib.experiments import validate_experimental_output

        report = validate_experimental_output(load("sample.tokens.json"), load("sample.evidence.json"))
        self.assertEqual(report["errors"], [])
        self.assertGreaterEqual(report["token_count"], 2)
        self.assertGreaterEqual(len(report["strategies"]), 2)
        self.assertEqual(report["token_paths"], report["evidence_paths"])

    def test_one_experiment_cannot_satisfy_the_minimum(self):
        from lib.experiments import validate_experimental_output

        tokens = load("sample.tokens.json")
        evidence = load("sample.evidence.json")
        kept_name = next(iter(tokens["experimental"]["tokens"]))
        kept_path = f"experimental.tokens.{kept_name}"
        tokens["experimental"]["tokens"] = {kept_name: tokens["experimental"]["tokens"][kept_name]}
        evidence["experimental_output"]["entries"] = [item for item in evidence["experimental_output"]["entries"] if item["path"] == kept_path]
        evidence["possibility_ledger"]["extensions"] = [item for item in evidence["possibility_ledger"]["extensions"] if item.get("tokens") == [kept_path]]
        errors = validate_experimental_output(tokens, evidence)["errors"]
        self.assertIn("at least two experimental tokens", " | ".join(errors))

    def test_missing_experimental_token_blocks_output(self):
        from lib.experiments import validate_experimental_output

        tokens = load("sample.tokens.json")
        evidence = load("sample.evidence.json")
        removed = next(iter(tokens["experimental"]["tokens"]))
        del tokens["experimental"]["tokens"][removed]
        errors = validate_experimental_output(tokens, evidence)["errors"]
        self.assertIn("experimental token coverage mismatch", " | ".join(errors))

    def test_experimental_token_needs_machine_readable_metadata(self):
        from lib.experiments import validate_experimental_output

        tokens = load("sample.tokens.json")
        evidence = load("sample.evidence.json")
        first = next(iter(tokens["experimental"]["tokens"].values()))
        first.pop("$extensions")
        errors = validate_experimental_output(tokens, evidence)["errors"]
        self.assertIn("needs experiment metadata", " | ".join(errors))

    def test_experiments_need_two_distinct_strategies(self):
        from lib.experiments import validate_experimental_output

        tokens = load("sample.tokens.json")
        evidence = load("sample.evidence.json")
        entries = list(tokens["experimental"]["tokens"].values())
        namespace = "org.dtcg-tokens.experimental"
        strategy = entries[0]["$extensions"][namespace]["exploration_strategy"]
        entries[1]["$extensions"][namespace]["exploration_strategy"] = strategy
        evidence["experimental_output"]["entries"][1]["exploration_strategy"] = strategy
        errors = validate_experimental_output(tokens, evidence)["errors"]
        self.assertIn("two distinct exploration strategies", " | ".join(errors))

    def test_final_review_accounts_for_every_experiment(self):
        from lib.experiments import validate_experimental_output

        tokens = load("sample.tokens.json")
        evidence = load("sample.evidence.json")
        paths = [item["path"] for item in evidence["experimental_output"]["entries"]]
        evidence["artifact_review"]["experimental_review"] = {
            "status": "pass",
            "reviewed_paths": paths,
            "findings": "Every experimental token has a visible specimen and an explicit use boundary.",
        }
        self.assertEqual(validate_experimental_output(tokens, evidence, final=True)["errors"], [])
        evidence["artifact_review"]["experimental_review"]["reviewed_paths"].pop()
        errors = validate_experimental_output(tokens, evidence, final=True)["errors"]
        self.assertIn("experimental artifact review coverage mismatch", " | ".join(errors))


if __name__ == "__main__":
    unittest.main()
