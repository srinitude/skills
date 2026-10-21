"""Behavior tests for domain-specific skill primitive lifecycle ownership."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR, run


def payloads():
    names = ["primitive-lifecycle.json", "use-case-contract.json"]
    return [json.loads((SKILL_DIR / "assets" / name).read_text())
            for name in names]


def write_case(root, lifecycle, contract, mise):
    assets = root / "assets"
    assets.mkdir()
    (assets / "primitive-lifecycle.json").write_text(
        json.dumps(lifecycle), encoding="utf-8")
    (assets / "use-case-contract.json").write_text(
        json.dumps(contract), encoding="utf-8")
    (root / "mise.toml").write_text(mise, encoding="utf-8")


def _TestPrimitiveLifecycle_check(self, edit=None, mise=None):
    lifecycle, contract = payloads()
    if edit:
        edit(lifecycle, contract)
    source = mise or (SKILL_DIR / "mise.toml").read_text()
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "skill-factory"
        root.mkdir()
        write_case(root, lifecycle, contract, source)
        return run("check_primitive_lifecycle.py", root)

def _TestPrimitiveLifecycle_test_factory_lifecycle_passes(self):
    result = self.check()
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

def _TestPrimitiveLifecycle_test_every_primitive_role_needs_a_lifecycle(self):
    def edit(lifecycle, _):
        lifecycle["primitives"].pop("assets")
    result = self.check(edit)
    self.assertEqual(result.returncode, 1)
    self.assertIn("must match primitive roles", result.stdout)

def _TestPrimitiveLifecycle_test_every_domain_aspect_needs_a_lifecycle(self):
    def edit(lifecycle, _):
        lifecycle["aspects"].pop("quality")
    result = self.check(edit)
    self.assertEqual(result.returncode, 1)
    self.assertIn("must match domain aspects", result.stdout)

def _TestPrimitiveLifecycle_test_every_aspect_phase_needs_an_owner(self):
    def edit(lifecycle, _):
        lifecycle["profiles"]["agent-skill-aspect"].pop("discover")
    result = self.check(edit)
    self.assertEqual(result.returncode, 1)
    self.assertIn("must cover every lifecycle phase", result.stdout)

def _TestPrimitiveLifecycle_test_every_phase_needs_an_owner(self):
    def edit(lifecycle, _):
        lifecycle["profiles"]["agent-skill-primitive"].pop("retire")
    result = self.check(edit)
    self.assertEqual(result.returncode, 1)
    self.assertIn("must cover every lifecycle phase", result.stdout)

def _TestPrimitiveLifecycle_test_phase_owner_must_be_a_real_mise_task(self):
    def edit(lifecycle, _):
        lifecycle["profiles"]["agent-skill-primitive"]["update"] = "fake"
    result = self.check(edit)
    self.assertEqual(result.returncode, 1)
    self.assertIn("unknown Mise task", result.stdout)

def _TestPrimitiveLifecycle_test_role_and_task_must_be_domain_specific(self):
    def edit(lifecycle, contract):
        contract["primitive_roles"]["assets"]["motivation"] = "Useful."
    result = self.check(edit)
    self.assertEqual(result.returncode, 1)
    self.assertIn("domain term", result.stdout)

def _TestPrimitiveLifecycle_test_malformed_profile_fails_without_traceback(self):
    def edit(lifecycle, _):
        lifecycle["profiles"]["agent-skill-aspect"] = []
    result = self.check(edit)
    self.assertEqual(result.returncode, 1)
    self.assertIn("must be an object", result.stdout)
    self.assertNotIn("Traceback", result.stderr)

def _TestPrimitiveLifecycle_test_domain_term_must_not_match_inside_an_unrelated_word(self):
    def edit(lifecycle, contract):
        lifecycle["skill"] = "git"
        contract["skill"] = "git"
        contract["domain_terms"] = ["git"]
        contract["primitive_roles"]["assets"]["motivation"] = (
            "Digital output remains available.")
    result = self.check(edit)
    self.assertEqual(result.returncode, 1)
    self.assertIn("primitive assets.motivation", result.stdout)


class TestPrimitiveLifecycle(unittest.TestCase):
    check = _TestPrimitiveLifecycle_check
    test_factory_lifecycle_passes = _TestPrimitiveLifecycle_test_factory_lifecycle_passes
    test_every_primitive_role_needs_a_lifecycle = _TestPrimitiveLifecycle_test_every_primitive_role_needs_a_lifecycle
    test_every_domain_aspect_needs_a_lifecycle = _TestPrimitiveLifecycle_test_every_domain_aspect_needs_a_lifecycle
    test_every_aspect_phase_needs_an_owner = _TestPrimitiveLifecycle_test_every_aspect_phase_needs_an_owner
    test_every_phase_needs_an_owner = _TestPrimitiveLifecycle_test_every_phase_needs_an_owner
    test_phase_owner_must_be_a_real_mise_task = _TestPrimitiveLifecycle_test_phase_owner_must_be_a_real_mise_task
    test_role_and_task_must_be_domain_specific = _TestPrimitiveLifecycle_test_role_and_task_must_be_domain_specific
    test_malformed_profile_fails_without_traceback = _TestPrimitiveLifecycle_test_malformed_profile_fails_without_traceback
    test_domain_term_must_not_match_inside_an_unrelated_word = _TestPrimitiveLifecycle_test_domain_term_must_not_match_inside_an_unrelated_word


if __name__ == "__main__":
    unittest.main()
