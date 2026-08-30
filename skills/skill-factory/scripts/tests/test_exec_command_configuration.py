"""Contract tests for the exact exec_command configuration."""
import pathlib
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[2]


class TestExecCommandConfiguration(unittest.TestCase):
    def test_route_precedes_first_command_and_is_exactly_scoped(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        route = "## What configuration applies to `exec_command`?"
        self.assertEqual(text.count(route), 1)
        self.assertLess(text.index(route), text.index("python3 scripts/doctor.py"))
        self.assertIn("applies only to `exec_command`", text)
        self.assertIn("does not change sibling tools", text)

    def test_reference_retains_all_rules_and_enforcement_limit(self):
        path = SKILL / "references" / "exec-command-configuration.md"
        text = path.read_text(encoding="utf-8")
        ids = ["B-66624905d73b", "B-c9cb3a4918f7", "B-e4e528347ac4",
               "B-c46083cf74ac", "B-c500fb1baa36", "B-84fcb4b4eb05",
               "B-1c388240357e", "B-97c2d87f44b7"]
        self.assertTrue(all(rule_id in text for rule_id in ids))
        self.assertIn("instruction-only", text)
        self.assertIn("rg --files", text)
        self.assertIn("max_output_tokens", text)
        self.assertIn("session_id", text)
        self.assertIn("destructive target", text)


if __name__ == "__main__":
    unittest.main()
