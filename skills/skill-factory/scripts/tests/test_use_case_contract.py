"""Behavior tests for the skill use-case specificity gate."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run

KINDS = ["skill_body", "references", "assets", "scripts", "tests",
         "mise_tasks", "examples", "evals", "policies", "schemas",
         "records"]
DIMENSIONS = ["actors", "objects", "actions", "states", "invariants",
              "variants", "interfaces", "authorities", "failures",
              "recoveries", "evidence", "time", "resources", "quality",
              "terminology", "exclusions"]


def role(kind):
    return {
        "ownership": "domain_specific",
        "role": f"Make {kind} serve release notes from git history.",
        "outcome": f"The {kind} advances the release notes result.",
        "motivation": "Keep change audience needs ahead of generic packaging.",
        "value": f"The {kind} turns git history into useful progress.",
        "failure_prevented": f"A {kind} that cannot improve release notes.",
        "proof": "A release notes case proves the git history behavior.",
    }


def motivations():
    return [
        {"constraint": "Use real git history.",
         "reason": "Release notes must reflect git history changes.",
         "failure_prevented": "Release notes with invented change claims."},
        {"constraint": "Name the release notes change audience.",
         "reason": "The change audience needs relevant release notes impact.",
         "failure_prevented": "Release notes without change audience value."},
    ]


def receipts():
    return [
        {"source": f"https://source{index}.example.com/release-notes",
         "source_class": "standard" if index % 2 else "first_party",
         "claim": "Release notes use git history for a change audience.",
         "disposition": "retained",
         "checked_at": "2026-09-02T04:00:00-04:00",
         "limitations": "This source does not define every release notes case.",
         "dimensions": DIMENSIONS[index::4]}
        for index in range(4)
    ]


def research_fields():
    return {
        "research_receipts": receipts(),
        "research_questions": {
            key: f"What does {key} mean for release notes from git history?"
            for key in DIMENSIONS},
        "disconfirmation": [
            {"question": "Could git history be insufficient for release notes?",
             "source": "https://counter.example.org/release-notes",
             "checked_at": "2026-09-02T04:00:00-04:00",
             "result": "Change audience context can require another live owner.",
             "disposition": "bounded"}],
    }


def contract(name="release-notes"):
    data = {
        "version": "1.0.0", "skill": name,
        "outcome": "Produce release notes from git history for a change audience.",
        "motivations": motivations(),
        "domain_terms": ["release notes", "git history", "change audience"],
        "domain_failures": ["release notes with invented change",
                            "release notes missing a change audience"],
        "domain_evidence": ["git history commit receipt",
                            "release notes reader-facing output"],
        "domain_dimensions": {
            key: [f"Release notes {key} grounded in git history."]
            for key in DIMENSIONS
        },
        "primitive_roles": {kind: role(kind) for kind in KINDS},
    }
    data.update(research_fields())
    return data


def write_skill(root, data):
    (root / "assets").mkdir()
    (root / "SKILL.md").write_text(
        "---\nname: release-notes\ndescription: Use when notes are needed.\n---\n",
        encoding="utf-8")
    path = root / "assets" / "use-case-contract.json"
    path.write_text(json.dumps(data), encoding="utf-8")


class TestUseCaseContract(unittest.TestCase):
    def test_help_documents_usage_and_exit_codes(self):
        result = run("check_use_case_contract.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("exit code", result.stdout.lower())

    def test_missing_contract_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            (root / "SKILL.md").write_text("---\nname: release-notes\n---\n")
            result = run("check_use_case_contract.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing", result.stdout.lower())

    def test_domain_specific_contract_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, contract())
            result = run("check_use_case_contract.py", root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_skill_identity_must_match_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, contract("generic-helper"))
            result = run("check_use_case_contract.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("skill must equal", result.stdout)

    def test_scaffold_text_fails(self):
        data = contract()
        data["outcome"] = "SCAFFOLD-PLACEHOLDER replace this outcome."
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, data)
            result = run("check_use_case_contract.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("scaffold placeholder", result.stdout.lower())

    def test_every_primitive_kind_needs_a_domain_role(self):
        data = contract()
        del data["primitive_roles"]["evals"]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, data)
            result = run("check_use_case_contract.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("primitive_roles.evals", result.stdout)

    def test_motivations_cannot_use_generic_language(self):
        data = contract()
        data["motivations"][0]["reason"] = "This is a good default."
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, data)
            result = run("check_use_case_contract.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("motivations.0.reason", result.stdout)

    def test_every_domain_dimension_is_required(self):
        data = contract()
        del data["domain_dimensions"]["states"]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, data)
            result = run("check_use_case_contract.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("domain_dimensions.states", result.stdout)

    def test_each_role_uses_package_domain_terms(self):
        data = contract()
        data["primitive_roles"]["scripts"]["role"] = "Parse input files."
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, data)
            result = run("check_use_case_contract.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("primitive_roles.scripts.role", result.stdout)

    def test_each_role_names_objective_progress(self):
        data = contract()
        data["primitive_roles"]["scripts"]["value"] = "Runs quickly."
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, data)
            result = run("check_use_case_contract.py", root)
        self.assertEqual(result.returncode, 1)
        self.assertIn("primitive_roles.scripts.value", result.stdout)

    def test_domain_label_cannot_decorate_generic_primitive(self):
        data = contract()
        data["primitive_roles"]["scripts"]["value"] = (
            "Release notes operation advances or proves its named package state.")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_skill(root, data)
            result = run("check_use_case_contract.py", root)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("generic scaffold language", result.stdout)


if __name__ == "__main__":
    unittest.main()
