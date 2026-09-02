import json
import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASPECTS = {"actors", "objects", "actions", "states", "invariants", "variants",
           "interfaces", "authorities", "failures", "recoveries", "evidence",
           "time", "resources", "quality", "terminology", "exclusions"}
PRIMITIVES = {"skill_body", "references", "assets", "scripts", "tests",
              "mise_tasks", "examples", "evals", "policies", "schemas", "records"}
PHASES = {"discover", "research", "experiment", "decide", "create", "inspect",
          "update", "validate", "accept", "restore", "deprecate", "retire"}
POLICY_TASKS = {"domain-research-policy", "use-case-policy", "mise-primitives-policy",
                "primitive-lifecycle-policy", "task-graph-policy", "decision-policy",
                "invocation-policy", "mise-latest", "mise-primitives-update"}


class TestTokenLifecyclePolicy(unittest.TestCase):
    def setUp(self):
        with (ROOT / "mise.toml").open("rb") as handle:
            self.tasks = tomllib.load(handle)["tasks"]

    def test_mise_owns_every_new_policy(self):
        self.assertTrue(POLICY_TASKS <= set(self.tasks))
        for name in POLICY_TASKS:
            self.assertIn("depends", self.tasks[name])
            self.assertIn("token", self.tasks[name]["description"].lower())

    def test_lifecycle_covers_every_token_aspect_and_primitive(self):
        data = json.loads((ROOT / "assets/primitive-lifecycle.json").read_text())
        self.assertEqual(set(data["required_phases"]), PHASES)
        self.assertEqual(set(data["aspects"]), ASPECTS)
        self.assertEqual(set(data["primitives"]), PRIMITIVES)
        for profile in data["profiles"].values():
            self.assertEqual(set(profile), PHASES)
            self.assertTrue(set(profile.values()) <= set(self.tasks))

    def test_skill_body_routes_mechanics_only_through_mise(self):
        body = (ROOT / "SKILL.md").read_text()
        self.assertIsNone(re.search(r"`?scripts/[^`\s|]+\.py", body))
        for task in ["token-run", "token-packet", "token-pass", "token-block",
                     "token-validate", "token-prove", "primitive-lifecycle-policy"]:
            self.assertIn(f"mise run {task}", body)
        for task in ["plan-standardize", "validate-target", "eval-target",
                     "invocation-policy"]:
            self.assertIn(f"mise run {task}", body)
        self.assertIn("skill-factory", body)

    def test_update_chain_is_deferred_and_rechecks_acceptance(self):
        update = self.tasks["mise-primitives-update"]
        self.assertEqual(update["depends"], ["mise-latest"])
        self.assertEqual(update["depends_post"], ["refresh-lineage"])


if __name__ == "__main__":
    unittest.main()
