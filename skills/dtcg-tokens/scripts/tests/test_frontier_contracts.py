"""Pin source-frontier, exploration-corpus, transfer, and experiment contracts."""
import json
import hashlib
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]


def load(relative):
    path = SKILL_DIR / relative
    if not path.is_file():
        raise AssertionError(f"missing {relative}")
    return json.loads(path.read_text(encoding="utf-8"))


class SourceFrontierTests(unittest.TestCase):
    def test_frontier_has_breadth_distance_currentness_and_stop_rules(self):
        frontier = load("assets/creative-source-frontier.json")
        self.assertGreaterEqual(len(frontier["mechanism_families"]), 6)
        self.assertGreaterEqual(len(frontier["source_domains"]), 3)
        self.assertEqual(frontier["coverage"]["minimum_distant_domains"], 3)
        self.assertTrue(frontier["coverage"]["require_antithetical_source"])
        self.assertTrue(frontier["coverage"]["require_current_research_source"])
        self.assertEqual(frontier["stop_rule"]["unchanged_additions"], 2)
        self.assertEqual(frontier["budget_exhaustion"], "BLOCKED")

    def test_transfer_and_experiment_contracts_keep_lineage(self):
        transfer_path = SKILL_DIR / "references" / "creative-transfer.md"
        self.assertTrue(transfer_path.is_file(), "missing references/creative-transfer.md")
        transfer = transfer_path.read_text(encoding="utf-8")
        for marker in ["relational structure", "forbidden surface", "prediction", "falsifier", "token paths"]:
            self.assertIn(marker, transfer.lower())
        experiment = load("assets/experiment-contract.json")
        self.assertEqual(experiment["retention"]["minimum_tokens"], 3)
        self.assertEqual(experiment["retention"]["minimum_mechanism_families"], 3)
        self.assertTrue(experiment["retention"]["require_inversion_or_antithesis"])
        for field in ["question", "hypothesis", "null", "variables", "controls", "thresholds", "stop_rule", "rollback"]:
            self.assertIn(field, experiment["frozen_fields"])


class ExplorationCorpusTests(unittest.TestCase):
    def test_manifest_has_every_required_shard(self):
        manifest = load("assets/exploration-corpus/manifest.json")
        expected = {"primitives", "operators", "mechanisms", "concepts", "themes", "constraints", "questions", "technology", "negative-patterns"}
        self.assertTrue(expected.issubset(set(manifest["shards"])))
        for shard, record in manifest["shards"].items():
            path = SKILL_DIR / record["path"]
            self.assertTrue(path.is_file(), shard)
            self.assertEqual(record.get("sha256"), hashlib.sha256(path.read_bytes()).hexdigest(), shard)

    def test_synthesis_requires_four_lanes_before_evaluation(self):
        contract = load("assets/exploration-corpus/synthesis-contract.json")
        self.assertEqual(contract["minimum_candidates"], 12)
        self.assertEqual(contract["minimum_per_lane"], 3)
        self.assertEqual(set(contract["lanes"]), {"combinational", "exploratory", "transformational", "antithetical"})
        self.assertTrue(contract["freeze_before_evaluation"])
        for field in ["source_relations", "primitive", "operator", "mechanism", "theme_or_tension", "constraint", "question", "predicted_effect", "falsifier", "token_paths"]:
            self.assertIn(field, contract["candidate_fields"])


if __name__ == "__main__":
    unittest.main()
