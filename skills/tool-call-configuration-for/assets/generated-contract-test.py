"""Contract tests for a generated tool-specific skill."""
import json
import pathlib
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[2]


class TestGeneratedContract(unittest.TestCase):
    def test_identity_and_profiles_exist(self):
        identity = SKILL / "assets" / "tool-identity.json"
        self.assertTrue(identity.is_file())
        self.assertTrue(json.loads(identity.read_text())["callable_name"])
        self.assertTrue((SKILL / "references" / "tool-contract.md").is_file())
        self.assertTrue((SKILL / "references" / "behavior-profile.md").is_file())

    def test_body_states_enforcement_limit(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("does not prove that a host intercepts calls", text)
        self.assertIn("instruction-only", text)


if __name__ == "__main__":
    unittest.main()
