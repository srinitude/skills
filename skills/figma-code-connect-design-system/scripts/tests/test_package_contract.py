"""Package-level contract tests for the public workflow."""

import hashlib
import json
import pathlib
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]


class TestPackageContract(unittest.TestCase):
    def test_capability_registry_has_every_reference_mechanism(self):
        path = SKILL_DIR / "assets" / "code-connect-mechanisms.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        ids = [item["id"] for item in doc["mechanisms"]]
        self.assertEqual(len(ids), 47)
        self.assertEqual(len(ids), len(set(ids)))

    def test_three_template_kinds_are_not_collapsed(self):
        path = SKILL_DIR / "assets" / "run-contract.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            doc["template_kinds"],
            ["design-composition", "workflow", "code-connect"],
        )

    def test_cumulative_hierarchy_is_exact(self):
        path = SKILL_DIR / "assets" / "run-contract.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(
            doc["hierarchy"],
            ["dtcg-tokens", "atoms", "molecules", "organisms", "design-composition-templates", "screens"],
        )

    def test_focus_intent_contract_covers_hierarchy_and_parity(self):
        path = SKILL_DIR / "assets" / "run-contract.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(doc["focus_intent_levels"], doc["comparison_levels"])
        self.assertEqual(doc["focus_intent_fields"], [
            "user_task", "focus_target", "focus_location", "focus_timing",
            "focus_mechanism", "focus_reason", "attention_sequence",
            "competing_signals", "defocus_and_recovery", "failure_evidence",
        ])
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("focus-intent record", skill)
        self.assertIn("Figma, TypeScript production behavior, and Code Connect", skill)

    def test_integrated_contract_owns_required_parity_and_quality_evidence(self):
        path = SKILL_DIR / "assets" / "run-contract.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        for key in [
            "component_property_kinds", "quality_checkpoints", "quality_gate_ids",
            "nested_governance_required", "quality_visual_contexts",
            "render_context_fields", "render_proof_fields",
        ]:
            self.assertIn(key, doc)
        self.assertEqual(
            doc["component_property_kinds"],
            ["TEXT", "BOOLEAN", "VARIANT", "INSTANCE_SWAP", "SLOT", "NESTED_CONNECTED"],
        )
        self.assertEqual(
            doc["quality_checkpoints"], ["direction", "artifact", "integrated"]
        )
        self.assertEqual(
            doc["quality_gate_ids"],
            [
                "truth", "access", "task", "perception", "familiarity",
                "standards", "uniqueness", "craft", "resilience",
            ],
        )
        self.assertTrue(doc["nested_governance_required"])

    def test_figma_app_gate_keeps_goal_provenance_outside_the_skill(self):
        path = SKILL_DIR / "assets" / "run-contract.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        required = doc["figma_app_pass_gate"]["required_sources"]
        expected = [
            "current direct vision", "current web research", "Mobbin",
            "Refero", "Lazyweb", "project-owned inspiration source",
            "product API specification", "event or webhook specification",
            "runtime primitive documentation",
        ]
        excluded = [
            "current product board or FigJam source",
            "originating audiovisual source",
            "originating transcript",
        ]
        self.assertEqual(required, expected)
        skill = (SKILL_DIR / "SKILL.md").read_text()
        for role in excluded:
            self.assertNotIn(role, required)
            self.assertNotIn(role, skill)

    def test_figma_app_gate_uses_portable_control_and_same_agent_vision(self):
        doc = json.loads(
            (SKILL_DIR / "assets" / "run-contract.json").read_text(encoding="utf-8")
        )
        gate = doc["figma_app_pass_gate"]
        self.assertEqual(gate["computer_control_capability"],
                         "platform-neutral local application control")
        self.assertEqual(gate["vision_owner"],
                         "same invoking strong vision-capable executor")
        self.assertEqual(gate["missing_capability_disposition"], "blocked")
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("paramount visual-proof rule", skill)
        self.assertIn("every applicable available vision capability", skill)
        self.assertIn("before and after", skill)
        self.assertIn("directly inspect the Figma application", skill)

    def test_package_has_no_project_specific_or_retired_owner_names(self):
        project = "Goal" + "steel"
        retired = "visual-design" + "-system-extractor"
        for path in SKILL_DIR.rglob("*"):
            if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn(project, text, str(path))
            self.assertNotIn(retired, text, str(path))

    def test_source_lineage_hashes_are_current(self):
        path = SKILL_DIR / "evals" / "source-lineage.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        cases = json.loads(
            (SKILL_DIR / "evals" / "cases.json").read_text(encoding="utf-8")
        )
        self.assertEqual(doc["source_case_ids"],
                         [item["source_id"] for item in cases["cases"]])
        current = {
            item.relative_to(SKILL_DIR).as_posix()
            for item in SKILL_DIR.rglob("*")
            if item.is_file()
            and "__pycache__" not in item.parts
            and item != path
        }
        claimed = {item["path"] for item in doc["source_files"]}
        self.assertEqual(claimed, current)
        public = {item["path"] for item in doc["public_files"]}
        self.assertEqual(public, current)
        for item in doc["source_files"]:
            source = SKILL_DIR / item["path"]
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            self.assertEqual(digest, item["sha256"], item["path"])

    def test_mise_gates_one_nonregressing_skill_improvement(self):
        path = SKILL_DIR / "assets" / "improvement-contract.json"
        policy = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(policy["cli_owner"], "mise")
        self.assertEqual(policy["acceptance"], "pareto_non_regression")
        self.assertEqual(policy["failure"], "restore_last_accepted_version")
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Optional final step", skill)
        self.assertIn("one named skill part", skill)
        self.assertIn("restore the last passed version", skill)
        self.assertIn("mise run complete", skill)

    def test_markdown_routes_script_operations_through_mise(self):
        violations = []
        for path in SKILL_DIR.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            if "scripts/" in text:
                violations.append(path.relative_to(SKILL_DIR).as_posix())
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
