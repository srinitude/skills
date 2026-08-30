"""With-skill and without-skill fixture trace comparison."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
SCRIPT = SKILL / "scripts" / "trace_fixture.py"
TOOL = SKILL / "evals" / "fixtures" / "established-mcp-read.json"
BEHAVIOR = SKILL / "evals" / "fixtures" / "behavior-report.json"


def trace(condition):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), f"@{TOOL}", "--behavior",
         f"@{BEHAVIOR}", "--condition", condition],
        capture_output=True, text=True, timeout=30)
    return result, json.loads(result.stdout)


class TestTraceFixture(unittest.TestCase):
    def test_with_skill_trace_contains_every_rule_and_without_does_not(self):
        with_result, with_trace = trace("with-skill")
        without_result, without_trace = trace("without-skill")
        self.assertEqual(with_result.returncode, 0, with_result.stderr)
        self.assertEqual(without_result.returncode, 0, without_result.stderr)
        with_events = [event["event"] for event in with_trace["events"]]
        without_events = [event["event"] for event in without_trace["events"]]
        self.assertIn("skill-load", with_events)
        self.assertNotIn("skill-load", without_events)
        rule_events = [event for event in with_trace["events"]
                       if event["event"] == "behavior-rule"]
        self.assertEqual(len(rule_events), 2)
        self.assertFalse(any(event["event"] == "behavior-rule"
                             for event in without_trace["events"]))
        self.assertEqual(with_trace["claim_limit"], "fixture-only")


if __name__ == "__main__":
    unittest.main()
