"""Audience is explicit, independent of scope, preserved, and read consistently."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from publication_fixtures import standardize
from test_standardize_registry_skill import profile, write_target
from test_use_case_contract import contract, write_skill


class TestAudience(unittest.TestCase):
    def test_created_scope_audience_cross_product_has_one_owner_and_early_key(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            for scope in ["user", "project"]:
                for audience in ["human", "agent"]:
                    name = f"notes-{scope}-{audience}"
                    result = run("scaffold_skill.py", "--name", name, "--scope", scope,
                                 "--audience", audience, "--description", "Use when release notes need review.", "--dest", base)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    data = json.loads((base / name / "assets/use-case-contract.json").read_text())
                    self.assertEqual(data.get("audience", {}).get("primary"), audience)
                    body = (base / name / "SKILL.md").read_text()
                    self.assertLess(body.index(f"Primary audience: {audience}."), body.index("## Ordered workflow"))
                    self.assertIn("Mechanical evidence", body)
                    self.assertIn("Human evidence", body)
                    self.assertEqual(json.loads(result.stdout)["audience"], audience)

    def test_missing_choice_prevents_new_output(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            result = run("scaffold_skill.py", "--name", "notes", "--scope", "user",
                         "--description", "Use when release notes need review.", "--dest", base)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(base.iterdir()), [])

    def test_enum_types_legacy_and_body_consistency(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve() / "release-notes"
            root.mkdir()
            data = contract()
            data.pop("audience", None)
            write_skill(root, data)
            path = root / "assets/use-case-contract.json"
            self.assertNotEqual(run("check_use_case_contract.py", root).returncode, 0)
            self.assertEqual(run("check_use_case_contract.py", root, "--inspect-legacy").returncode, 0)
            for audience in [None, {"primary": True}, {"primary": ["human"]}, {"primary": "both"}, {"primary": "human"}]:
                data["audience"] = audience
                path.write_text(json.dumps(data))
                result = run("check_use_case_contract.py", root)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertNotIn("Traceback", result.stderr)
            body = (root / "SKILL.md").read_text() + "\n## Outcome\n\nPrimary audience: human.\n"
            (root / "SKILL.md").write_text(body)
            self.assertEqual(run("check_use_case_contract.py", root).returncode, 0)
            path.write_text(json.dumps(data).replace('"primary": "human"', '"primary": "human", "primary": "agent"'))
            self.assertNotEqual(run("check_use_case_contract.py", root).returncode, 0)

    def test_standardization_preserves_an_existing_valid_audience(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            root = base / "clock-anchor"
            write_target(root)
            (root / "assets").mkdir()
            (root / "assets/use-case-contract.json").write_text(json.dumps({"audience": {"primary": "human"}}))
            data = profile()
            data.pop("audience", None)
            source = base / "profile.json"
            source.write_text(json.dumps(data))
            result = standardize(root, "--profile", source, "--scope", "user", "--apply")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            current = json.loads((root / "assets/use-case-contract.json").read_text())
            self.assertEqual(current.get("audience"), {"primary": "human"})
            self.assertIn("Primary audience: human.", (root / "SKILL.md").read_text())

    def test_explicit_audience_choice_is_reflected_without_a_scope_change(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            root = base / "clock-anchor"
            write_target(root)
            (root / "assets").mkdir()
            (root / "assets/use-case-contract.json").write_text(json.dumps({"audience": {"primary": "human"}}))
            source = base / "profile.json"
            source.write_text(json.dumps(profile()))
            result = standardize(root, "--profile", source, "--scope", "user",
                         "--audience", "agent", "--apply")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            current = json.loads((root / "assets/use-case-contract.json").read_text())
            self.assertEqual(current["audience"]["primary"], "agent")
            self.assertIn("Primary audience: agent.", (root / "SKILL.md").read_text())

    def test_target_legacy_inspection_does_not_accept_missing_audience(self):
        from variant_fixtures import package
        with tempfile.TemporaryDirectory() as temp:
            root = package(Path(temp).resolve() / "legacy-inventory", "user")
            path = root / "assets/use-case-contract.json"
            data = json.loads(path.read_text())
            data.pop("audience")
            path.write_text(json.dumps(data))
            strict = run("check_target.py", "validate", root)
            self.assertNotEqual(strict.returncode, 0)
            self.assertIn("audience.primary is required", strict.stdout)
            inspected = run("check_target.py", "validate", root, "--inspect-legacy")
            self.assertEqual(inspected.returncode, 0, inspected.stdout + inspected.stderr)
