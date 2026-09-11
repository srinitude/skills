"""Document-presence guards and machine policy contracts, not semantic acceptance."""
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]


def _TestDeterministicBoundary_test_factory_and_recursive_contract_put_programmatic_work_in_mise(self):
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    contract = (SKILL_DIR / "references" / "generation-contract.md").read_text()
    self.assertIn("## Mise task graph", skill)
    for phrase in ["[Mise][mise] owns public commands, pinned environments and outer prerequisites",
                   "[Mastra][mastra] owns substantive domain control, state and recovery",
                   "Existing tested scripts perform repeatable leaves",
                   "Keep one owner for scheduling, retries, caching, state, effects and cleanup, with explicit handoffs",
                   "Never add competing recursive [Mise][mise] graphs"]:
        self.assertIn(phrase, skill)
    self.assertNotIn("python3 scripts/", skill)
    for phrase in ["Mise for public entry/environment/outer prerequisites",
                   "Mastra for actual domain steps", "scripts for mechanics",
                   "fresh baseline", "evaluator", "Pareto",
                   "restore accepted bytes and verify their digest",
                   "Choose structures/algorithms from measured",
                   "every trial measures or justifies non-use"]:
        self.assertIn(phrase, contract)

def _TestDeterministicBoundary_test_mise_preserves_model_capabilities(self):
    paths = [SKILL_DIR / "SKILL.md",
             SKILL_DIR / "references" / "generation-contract.md",
             SKILL_DIR / "assets" / "skill-template.md"]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        self.assertIn("caller", text.lower())
        self.assertIn("authorized", text)
        self.assertIn("creative", text)
        self.assertIn("judgment", text)
        self.assertNotIn("Mise owns every deterministic command", text)
    for path in [paths[0], paths[2]]:
        text = path.read_text(encoding="utf-8")
        if path.name == "SKILL.md":
            self.assertIn("Preserve all relevant authorized modalities", text)
            self.assertIn("Use a capable real runner for binary media", text)
            self.assertIn("Availability alone grants no extra provider, cloud, voice, memory or multi-agent system", text)
            self.assertIn("Preserve existing languages, caller-controlled runners and faithful modalities", text)
        else:
            self.assertIn("Preserve selected host models/tools, modalities", text)
            self.assertIn("no separate Agent, provider, account, model policy", text)

def _TestDeterministicBoundary_test_factory_has_machine_readable_improvement_contract(self):
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


class TestDeterministicBoundary(unittest.TestCase):
    test_factory_and_recursive_contract_put_programmatic_work_in_mise = _TestDeterministicBoundary_test_factory_and_recursive_contract_put_programmatic_work_in_mise
    test_mise_preserves_model_capabilities = _TestDeterministicBoundary_test_mise_preserves_model_capabilities
    test_factory_has_machine_readable_improvement_contract = _TestDeterministicBoundary_test_factory_has_machine_readable_improvement_contract


def _TestFactoryOperations_setUp(self):
    self.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    path = SKILL_DIR / "references" / "generation-contract.md"
    self.contract = path.read_text(encoding="utf-8")

def _TestFactoryOperations_test_create_update_and_standardize_are_first_class_commands(self):
    for command in ["new <prompt>", "update <path> <prompt>",
                    "standardize <path>", "import <source> <destination>"]:
        self.assertIn(command, self.skill)
    self.assertIn("Preserve purpose, accepted behavior, source bytes, authorized scope", self.skill)
    self.assertIn("baseline_digest", self.skill)

def _TestFactoryOperations_test_portable_import_contract_names_canonical_owners(self):
    for phrase in ["AGENTS.md", ".agents/", "Preserve source bytes unless",
                   "Reject retained platform assumptions or lost source behavior"]:
        self.assertIn(phrase, self.contract)

def _TestFactoryOperations_test_required_concept_order_is_explicit(self):
    ordered = ["Outcome", "Motivation", "Evidence", "Mise task",
               "Steps", "Assets", "Evals"]
    positions = [self.contract.index(f"**{name}") for name in ordered]
    self.assertEqual(positions, sorted(positions))

def _TestFactoryOperations_test_resource_and_experiment_reference_is_owned(self):
    path = SKILL_DIR / "references" / "resource-and-experiment-design.md"
    text = path.read_text(encoding="utf-8")
    for phrase in ["Access pattern", "Format", "Resource", "Mise",
                   "Fresh baseline", "human review"]:
        self.assertIn(phrase, text)

def _TestFactoryOperations_test_help_example_matches_every_public_command(self):
    path = SKILL_DIR / "examples" / "example-help.md"
    example = path.read_text(encoding="utf-8")
    commands = ["new <prompt>", "update <path> <prompt>",
                "standardize <path>", "import <source> <destination>",
                "validate <path>", "eval <path>", "doctor"]
    for command in commands:
        self.assertIn(command, example)
    self.assertNotIn("commands that replace it", example)

def _TestFactoryOperations_test_registry_does_not_claim_a_fixed_live_inventory(self):
    path = SKILL_DIR / "references" / "registry.md"
    registry = path.read_text(encoding="utf-8")
    self.assertNotIn("currently ships two skills", registry)
    self.assertIn("mise run source-corpus", registry)


class TestFactoryOperations(unittest.TestCase):
    setUp = _TestFactoryOperations_setUp
    test_create_update_and_standardize_are_first_class_commands = _TestFactoryOperations_test_create_update_and_standardize_are_first_class_commands
    test_portable_import_contract_names_canonical_owners = _TestFactoryOperations_test_portable_import_contract_names_canonical_owners
    test_required_concept_order_is_explicit = _TestFactoryOperations_test_required_concept_order_is_explicit
    test_resource_and_experiment_reference_is_owned = _TestFactoryOperations_test_resource_and_experiment_reference_is_owned
    test_help_example_matches_every_public_command = _TestFactoryOperations_test_help_example_matches_every_public_command
    test_registry_does_not_claim_a_fixed_live_inventory = _TestFactoryOperations_test_registry_does_not_claim_a_fixed_live_inventory


def _TestImprovementLifecycle_test_declared_lifecycle_rejects_each_missing_or_weakened_gate(self):
    import sys
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    from check_improvement_contract import load_contract, problems
    policy = load_contract(SKILL_DIR)
    self.assertEqual(policy["lifecycle"]["adoption"],
                     "pending_next_invocation_confirmation")
    self.assertEqual(problems(policy), [])
    for key in policy["lifecycle"]:
        candidate = json.loads(json.dumps(policy))
        del candidate["lifecycle"][key]
        self.assertTrue(problems(candidate), key)
        candidate["lifecycle"][key] = "optional"
        self.assertTrue(problems(candidate), key)
    for invalid in [None, False, [], "accepted"]:
        candidate = dict(policy, lifecycle=invalid)
        self.assertTrue(problems(candidate))

def _TestImprovementLifecycle_test_every_published_dimension_has_a_distinct_source_bound_id(self):
    import re
    text = (SKILL_DIR / "references/improvement-dimensions.md").read_text()
    from scaffold_skill import source_files
    from standardize_registry_skill import COPIES
    name = "references/improvement-dimensions.md"
    self.assertIn((name, name, False), source_files())
    self.assertIn((name, name), COPIES)
    parent = (SKILL_DIR / "references/resource-and-experiment-design.md").read_text()
    self.assertIn("(improvement-dimensions.md)", parent)
    for content in [text, parent]:
        self.assertLess(len(content), 20_000)
        self.assertLess(len(content.rstrip().splitlines()), 200)
    ids = re.findall(r"^\| (Q[0-9]+) \|", text, re.MULTILINE)
    self.assertEqual(ids, [f"Q{number:02}" for number in range(1, 65)])
    for path in [SKILL_DIR / "SKILL.md", SKILL_DIR / "assets/skill-template.md"]:
        self.assertIn("pending next-invocation confirmation", path.read_text())


class TestImprovementLifecycle(unittest.TestCase):
    test_declared_lifecycle_rejects_each_missing_or_weakened_gate = _TestImprovementLifecycle_test_declared_lifecycle_rejects_each_missing_or_weakened_gate
    test_every_published_dimension_has_a_distinct_source_bound_id = _TestImprovementLifecycle_test_every_published_dimension_has_a_distinct_source_bound_id


if __name__ == "__main__":
    unittest.main()
