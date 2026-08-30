"""Behavior input preservation and failure behavior."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
CLI = SKILL / "scripts" / "tool_call_config.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *map(str, args)],
        capture_output=True, text=True, timeout=180)


def tool(path):
    value = {
        "schema": "tool-call-config/tool-descriptor/v1",
        "origin_class": "custom", "callable_name": "fixture.lookup",
        "provider_or_owner": "fixture", "runtime_or_server": "fixture",
        "namespace": "fixture", "version": None, "discovery_route": "file",
        "input_schema": {"type": "object"}, "output_schema": {"type": "object"},
        "capabilities": {"read_only": True, "state_changing": False},
        "sources": [{"locator": "fixture", "status": "verified"}],
    }
    path.write_text(json.dumps(value), encoding="utf-8")


class TestBehaviorInputs(unittest.TestCase):
    def generate(self, root, suffix, text):
        tool_path = root / "tool.json"
        behavior = root / f"behavior.{suffix}"
        output = root / f"out-{suffix}"
        tool(tool_path)
        behavior.write_text(text, encoding="utf-8")
        result = run("generate", f"@{tool_path}", "--behavior",
                     f"@{behavior}", "--output", output)
        return result, output

    def test_markdown_yaml_and_json_are_preserved(self):
        sources = {
            "md": "- Before every call, validate the query.\n- After success, report the row count.\n",
            "yaml": "rules:\n  - original: Validate the query before every call.\n    timing: before\n",
            "json": json.dumps({"rules": [{"original": "Validate the query.",
                                              "timing": "before"}]}),
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for suffix, source in sources.items():
                result, _ = self.generate(root, suffix, source)
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                profile = Path(report["evidence_dir"]) / "behavior-profile.json"
                data = json.loads(profile.read_text(encoding="utf-8"))
                self.assertIn("validate the query", data["source_text"].lower())
                self.assertTrue(data["rules"])
                self.assertTrue(data["rules"][0]["id"].startswith("B-"))

    def test_empty_behavior_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, _ = self.generate(Path(tmp), "md", "  \n")
        self.assertEqual(result.returncode, 2)
        self.assertIn("empty", result.stderr.lower())

    def test_malformed_json_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            result, _ = self.generate(Path(tmp), "json", "{bad")
        self.assertEqual(result.returncode, 2)
        self.assertIn("json", result.stderr.lower())

    def test_structured_conflict_stops(self):
        value = {"rules": [
            {"original": "Require logging.", "action": "log call", "strength": "required"},
            {"original": "Prohibit logging.", "action": "log call", "strength": "prohibited"},
        ]}
        with tempfile.TemporaryDirectory() as tmp:
            result, _ = self.generate(Path(tmp), "json", json.dumps(value))
        self.assertEqual(result.returncode, 1)
        self.assertIn("conflict", result.stderr.lower())

    def test_rule_ids_are_stable_across_reruns(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first, _ = self.generate(root, "md", "- Validate the query.\n")
            second, _ = self.generate(root, "md", "- Validate the query.\n")
            one = json.loads((Path(json.loads(first.stdout)["evidence_dir"]) /
                              "behavior-profile.json").read_text())
            two = json.loads((Path(json.loads(second.stdout)["evidence_dir"]) /
                              "behavior-profile.json").read_text())
        self.assertEqual(one["rules"][0]["id"], two["rules"][0]["id"])


if __name__ == "__main__":
    unittest.main()
