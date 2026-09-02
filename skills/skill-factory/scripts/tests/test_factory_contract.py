"""Contracts for factory boundaries, operations, and improvement policy."""
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]


class TestDeterministicBoundary(unittest.TestCase):
    def test_factory_and_recursive_contract_put_programmatic_work_in_mise(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        contract = (SKILL_DIR / "references" / "generation-contract.md").read_text()
        self.assertIn("## Deterministic and model-owned boundary", skill)
        self.assertIn("Mise owns every deterministic command", skill)
        self.assertNotIn("python3 scripts/", skill)
        for phrase in ["schemas, parsing, validation, file generation, state transitions",
                       "model-owned boundary", "one owning Mise task",
                       "fresh baseline", "frozen evaluator", "Pareto",
                       "restore the last accepted version",
                       "data structures and algorithms",
                       "measure or justify as not applicable"]:
            self.assertIn(phrase, contract)

    def test_mise_preserves_model_capabilities(self):
        paths = [SKILL_DIR / "SKILL.md",
                 SKILL_DIR / "references" / "generation-contract.md",
                 SKILL_DIR / "assets" / "skill-template.md"]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertIn("Mise is an orchestration boundary, not a capability ceiling", text)
            self.assertIn("every available, authorized capability", text)
            self.assertIn("never replace direct judgment with a proxy", text)

    def test_factory_has_machine_readable_improvement_contract(self):
        path = SKILL_DIR / "assets" / "improvement-contract.json"
        policy = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(policy["acceptance"], "pareto_non_regression")
        self.assertEqual(policy["failure"], "restore_last_accepted_version")
        self.assertEqual(policy["trial"]["change"], "one_named_dimension")
        self.assertEqual(policy["resource_policy"],
                         "measure_or_justify_not_applicable")
        for group in ["time", "cpu", "memory", "storage", "network", "cache",
                      "context", "process", "concurrency", "accelerator", "cost",
                      "human_attention"]:
            self.assertIn(group, policy["resource_catalog"])
        for dimension in ["simplicity", "plain_language"]:
            self.assertIn(dimension, policy["protected_dimensions"])


class TestFactoryOperations(unittest.TestCase):
    def setUp(self):
        self.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        path = SKILL_DIR / "references" / "generation-contract.md"
        self.contract = path.read_text(encoding="utf-8")

    def test_create_update_and_standardize_are_first_class_commands(self):
        for command in ["new <prompt>", "update <path> <prompt>",
                        "standardize <path>", "import <source> <destination>"]:
            self.assertIn(command, self.skill)
        self.assertIn("preserve its domain purpose", self.skill)
        self.assertIn("baseline_digest", self.skill)

    def test_portable_import_contract_names_canonical_owners(self):
        for phrase in ["AGENTS.md", ".agents/", "source stays unchanged",
                       "platform-specific assumptions"]:
            self.assertIn(phrase, self.contract)

    def test_required_concept_order_is_explicit(self):
        ordered = ["Outcome", "Motivation", "Evidence", "Mise task",
                   "Steps", "Assets", "Evals"]
        positions = [self.contract.index(f"**{name}") for name in ordered]
        self.assertEqual(positions, sorted(positions))

    def test_resource_and_experiment_reference_is_owned(self):
        path = SKILL_DIR / "references" / "resource-and-experiment-design.md"
        text = path.read_text(encoding="utf-8")
        for phrase in ["Access pattern", "Format", "Resource", "Mise",
                       "Fresh baseline", "human review"]:
            self.assertIn(phrase, text)

    def test_help_example_matches_every_public_command(self):
        path = SKILL_DIR / "examples" / "example-help.md"
        example = path.read_text(encoding="utf-8")
        commands = ["new <prompt>", "update <path> <prompt>",
                    "standardize <path>", "import <source> <destination>",
                    "validate <path>", "eval <path>", "doctor"]
        for command in commands:
            self.assertIn(command, example)
        self.assertNotIn("commands that replace it", example)

    def test_registry_does_not_claim_a_fixed_live_inventory(self):
        path = SKILL_DIR / "references" / "registry.md"
        registry = path.read_text(encoding="utf-8")
        self.assertNotIn("currently ships two skills", registry)
        self.assertIn("mise run source-corpus", registry)


if __name__ == "__main__":
    unittest.main()
