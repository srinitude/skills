"""Scope acceptance, preservation, and fail-before-write contracts."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_scaffold_skill import scaffold


def _TestScopeCreation_test_both_scopes_survive_generated_self_validation(self):
    for scope in ["user", "project"]:
        with tempfile.TemporaryDirectory() as temp:
            result = scaffold(temp, "demo-skill", "Use when testing scope.",
                              "--scope", scope)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            root = Path(temp) / "demo-skill"
            self.assertIn(f'scope: "{scope}"', (root / "SKILL.md").read_text())
            result = run(root / "scripts/validate_skill.py", root, "--accept")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            text = (root / "mise.toml").read_text()
            self.assertIn("validate_skill.py . --accept", text)
            file = root / "SKILL.md"
            file.write_text(file.read_text().replace(f'  scope: "{scope}"\n', ""))
            self.assertEqual(run(root / "scripts/validate_skill.py", root, "--accept").returncode, 1)

def _TestScopeCreation_test_missing_scope_does_not_create_any_files(self):
    with tempfile.TemporaryDirectory() as temp:
        result = run("scaffold_skill.py", "--name", "demo-skill",
                     "--description", "Use when testing scope.", "--dest", temp)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(list(Path(temp).iterdir()), [])


class TestScopeCreation(unittest.TestCase):
    test_both_scopes_survive_generated_self_validation = _TestScopeCreation_test_both_scopes_survive_generated_self_validation
    test_missing_scope_does_not_create_any_files = _TestScopeCreation_test_missing_scope_does_not_create_any_files


def _TestScopeValidation_test_legacy_inspection_and_output_acceptance_are_distinct(self):
    with tempfile.TemporaryDirectory() as temp:
        scaffold(temp, "demo-skill", "Use when testing scope.", "--scope", "user")
        root = Path(temp) / "demo-skill"
        file = root / "SKILL.md"
        file.write_text(file.read_text().replace('  scope: "user"\n', ""))
        before = file.read_bytes()
        self.assertEqual(run("validate_skill.py", root).returncode, 0)
        result = run("validate_skill.py", root, "--accept")
        self.assertEqual(result.returncode, 1)
        self.assertIn("metadata.scope", result.stdout)
        self.assertEqual(file.read_bytes(), before)

def _TestScopeValidation_test_invalid_and_duplicate_scope_always_fail(self):
    for value in ['"global"', 'null', 'true', '7', '[user]', '{value: user}',
                  '"user"\n  scope: "project"']:
        with tempfile.TemporaryDirectory() as temp:
            scaffold(temp, "demo-skill", "Use when testing scope.", "--scope", "user")
            root = Path(temp) / "demo-skill"
            file = root / "SKILL.md"
            file.write_text(file.read_text().replace('scope: "user"', f"scope: {value}"))
            self.assertEqual(run("validate_skill.py", root).returncode, 1, value)


class TestScopeValidation(unittest.TestCase):
    test_legacy_inspection_and_output_acceptance_are_distinct = _TestScopeValidation_test_legacy_inspection_and_output_acceptance_are_distinct
    test_invalid_and_duplicate_scope_always_fail = _TestScopeValidation_test_invalid_and_duplicate_scope_always_fail


def _TestScopeResolution_test_relative_skill_root_reads_scope_without_location_inference(self):
    with tempfile.TemporaryDirectory() as temp:
        scaffold(temp, "demo-skill", "Use when testing scope.", "--scope", "project")
        root = Path(temp) / "demo-skill"
        before = (root / "SKILL.md").read_bytes()
        result = run("resolve_scope.py", "--skill", ".", cwd=root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["scope"], "project")
        self.assertEqual((root / "SKILL.md").read_bytes(), before)

def _TestScopeResolution_test_preserve_existing_and_honor_explicit_change_without_writes(self):
    with tempfile.TemporaryDirectory() as temp:
        scaffold(temp, "demo-skill", "Use when testing scope.", "--scope", "project")
        root = Path(temp) / "demo-skill"
        before = (root / "SKILL.md").read_bytes()
        for flags, scope in [([], "project"), (["--scope", "user"], "user")]:
            result = run("resolve_scope.py", "--skill", root, *flags)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["scope"], scope)
        self.assertEqual((root / "SKILL.md").read_bytes(), before)

def _TestScopeResolution_test_missing_or_conflicting_evidence_asks_one_question(self):
    for evidence in [[], [{"scope": "user", "source": "request", "intended_use": "Across projects"},
                          {"scope": "project", "source": "requirements", "intended_use": "Only this project"}]]:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "evidence.json"
            path.write_text(json.dumps(evidence))
            result = run("resolve_scope.py", "--evidence", path)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["status"], "NEEDS_CLARIFICATION")
            self.assertEqual(data["question"].count("?"), 1)
            self.assertEqual(data["writes"], 0)

def _TestScopeResolution_test_unambiguous_authoritative_intended_use_can_resolve_legacy(self):
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp) / "evidence.json"
        path.write_text(json.dumps([{"scope": "user", "source": "user request",
                                     "intended_use": "Available across my projects"}]))
        result = run("resolve_scope.py", "--evidence", path)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["scope"], "user")


class TestScopeResolution(unittest.TestCase):
    test_relative_skill_root_reads_scope_without_location_inference = _TestScopeResolution_test_relative_skill_root_reads_scope_without_location_inference
    test_preserve_existing_and_honor_explicit_change_without_writes = _TestScopeResolution_test_preserve_existing_and_honor_explicit_change_without_writes
    test_missing_or_conflicting_evidence_asks_one_question = _TestScopeResolution_test_missing_or_conflicting_evidence_asks_one_question
    test_unambiguous_authoritative_intended_use_can_resolve_legacy = _TestScopeResolution_test_unambiguous_authoritative_intended_use_can_resolve_legacy
