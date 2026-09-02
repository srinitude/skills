"""Tests for factory-owned legacy contract migration."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from cli import SCRIPTS

import sys
sys.path.insert(0, str(SCRIPTS))

from standardization_mapping import (
    repair_mapping_json,
    rewritten_assertion,
    snapshot_public_lines,
)
from standardization_markdown import rewrite_markdown, rewrite_script_text, script_task_map
from standardization_mise import normalize_mise
from standardization_rewrites import apply_rewrites, apply_section_rewrites
from standardize_registry_skill import planned_paths


class TestMappingMigration(unittest.TestCase):
    def test_rewrite_preserves_text_after_old_paragraph_boundary(self):
        profile = {"text_rewrites": {"SKILL.md": [{
            "old": "old deterministic wording inside.",
            "new": "new task wording."
        }]}}
        actual = rewritten_assertion(
            "inside. Judgment stays with the model.", "SKILL.md", {}, profile)
        self.assertEqual(actual, "new task wording. Judgment stays with the model.")

    def test_rewrite_preserves_text_before_old_sentence_boundary(self):
        profile = {"text_rewrites": {"SKILL.md": [{
            "old": "Old mechanical sentence.",
            "new": "New task sentence."
        }]}}
        actual = rewritten_assertion(
            "Visible context. Old mechanical sentence", "SKILL.md", {}, profile)
        self.assertEqual(actual, "Visible context. New task sentence.")

    def test_plan_accounts_for_source_mapping_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            mapping = root / "evals/source-mapping.json"
            self.assertIn(mapping, planned_paths(root, {}))

    def test_rewritten_public_line_refreshes_mapping_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            root = repo / "skills/example"
            (root / "evals").mkdir(parents=True)
            evidence = repo / "evidence/ports/example/native"
            evidence.mkdir(parents=True)
            source = "Run `scripts/check.py` before release."
            expected = "Run `mise run check` before release."
            (evidence / "SKILL.native.md").write_text(source + "\n")
            (root / "SKILL.md").write_text(source + "\n")
            mapping = {"entries": [{"source_line": 1,
                "evidence_target": "native/SKILL.native.md",
                "public_targets": ["SKILL.md"],
                "public_text_sha256": hashlib.sha256(source.encode()).hexdigest()}]}
            (root / "evals/source-mapping.json").write_text(json.dumps(mapping))
            prior = snapshot_public_lines(root)
            (root / "SKILL.md").write_text(expected + "\n")
            repair_mapping_json(root, {"check.py": "check"}, {}, prior)
            saved = json.loads((root / "evals/source-mapping.json").read_text())
            digest = hashlib.sha256(expected.encode()).hexdigest()
            self.assertEqual(saved["entries"][0]["public_text_sha256"], digest)

    def test_rewrite_repairs_a_routed_mise_link(self):
        profile = {"line_task_routes": [{
            "contains": "secret-shaped strings", "tasks": ["scan-secrets"]
        }]}
        value = "`mise run validate`](`mise run validate`): secret-shaped strings"
        actual = rewritten_assertion(value, "SKILL.md", {}, profile)
        self.assertEqual(actual, "`mise run scan-secrets`: secret-shaped strings")

    def test_chained_rewrite_accepts_the_final_state(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "SKILL.md"
            target.write_text("final", encoding="utf-8")
            profile = {"text_rewrites": {"SKILL.md": [
                {"old": "initial", "new": "middle"},
                {"old": "middle", "new": "final"},
            ]}}
            apply_rewrites(root, profile)
            self.assertEqual(target.read_text(encoding="utf-8"), "final")

    def test_multi_command_script_needs_explicit_task_routes(self):
        tasks = {
            "catalog": {"run": "python3 scripts/fonts.py catalog"},
            "verify": {"run": "python3 scripts/fonts.py verify"},
        }
        self.assertNotIn("fonts.py", script_task_map(tasks))

    def test_uv_runner_collapses_into_the_owning_mise_task(self):
        owners = {"schema.py": "schema-tools"}
        command = "uv run --with 'PyYAML>=6,<7' python scripts/schema.py field color"
        self.assertEqual(rewrite_script_text(command, owners),
                         "mise run schema-tools field color")

    def test_unittest_discovery_collapses_to_test_task(self):
        command = ("PYTHONDONTWRITEBYTECODE=1 uv run --with PyYAML==6.0.3 "
                   "python -m unittest discover -s scripts/tests -p 'test_*.py'")
        self.assertEqual(rewrite_script_text(command, {}), "mise run test")

    def test_installed_skill_script_collapses_to_owner(self):
        owners = {"validate_brief.py": "validate-brief"}
        command = 'python3 "$SKILL_DIR/scripts/validate_brief.py" ./BRIEF.json'
        self.assertEqual(rewrite_script_text(command, owners),
                         "mise run validate-brief ./BRIEF.json")

    def test_repository_skill_script_collapses_to_owner(self):
        owners = {"tool_call_config.py": "tool-call-config"}
        command = "python3 skills/tool/scripts/tool_call_config.py apply spec.json"
        self.assertEqual(rewrite_script_text(command, owners),
                         "mise run tool-call-config apply spec.json")

    def test_duplicate_task_routes_collapse(self):
        text = "Use scripts/ and scripts/tests/."
        self.assertEqual(rewrite_script_text(text, {}), "Use `mise run test`.")

    def test_backticked_script_path_keeps_one_fence_pair(self):
        owners = {"scan.py": "scan"}
        self.assertEqual(rewrite_script_text("Run `scripts/scan.py`.", owners),
                         "Run `mise run scan`.")

    def test_backticked_script_command_keeps_arguments(self):
        owners = {"ledger.py": "ledger"}
        self.assertEqual(rewrite_script_text("Use `scripts/ledger.py init`.", owners),
                         "Use `mise run ledger init`.")

    def test_error_transcript_hides_internal_script_path(self):
        text = "python3: can't open file '/tmp/work/scripts/check.py': error"
        expected = "python3: can't open file '<skill-implementation>/check.py': error"
        self.assertEqual(rewrite_script_text(text, {}), expected)

    def test_profile_command_task_is_a_public_mise_owner(self):
        profile = {"main_task": "agentic-request", "primary_term": "font set",
                   "command_tasks": {"font-record": {
                       "description": "Read one saved font set",
                       "run": "python3 -c 'print(1)'"}}}
        output = normalize_mise("", profile)
        self.assertIn("[tasks.font-record]", output)
        self.assertIn("python3 -c 'print(1)'", output)

    def test_resource_gate_preserves_transcript_and_table_bytes(self):
        original = ("## Output\n\n```text\nassets/result.json\n```\n\n"
                    "| File | Meaning |\n| --- | --- |\n| assets/result.json | proof |\n")
        actual = rewrite_markdown(original, {}, {}, False)
        self.assertIn("Resource gate: run `mise run validate`", actual)
        self.assertIn("```text\nassets/result.json\n```", actual)
        self.assertIn("| assets/result.json | proof |", actual)
        self.assertNotIn("Use it through", actual)

    def test_optional_prepass_applies_only_available_routes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "SKILL.md"
            target.write_text("direct command", encoding="utf-8")
            profile = {"text_rewrites": {"SKILL.md": [
                {"old": "direct command", "new": "owned task"},
                {"old": "future generic text", "new": "final task"},
            ]}}
            apply_rewrites(root, profile, strict=False)
            self.assertEqual(target.read_text(encoding="utf-8"), "owned task")

    def test_section_rewrite_moves_detail_to_its_owner(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "SKILL.md"
            target.write_text("# Skill\n\n## Detail\n\nLong rule.\n\n## Next\n", encoding="utf-8")
            profile = {"section_rewrites": [{"path": "SKILL.md",
                "heading": "## Detail", "until": "## Next",
                "replacement": "## Detail\n\nLoad the rule through `mise run validate`."}]}
            apply_section_rewrites(root, profile)
            self.assertNotIn("Long rule", target.read_text())
            apply_section_rewrites(root, profile)


if __name__ == "__main__":
    unittest.main()
