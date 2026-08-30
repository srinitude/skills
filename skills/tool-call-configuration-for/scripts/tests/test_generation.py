"""Public generation behavior for tool-call-configuration-for."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
CLI = SKILL / "scripts" / "tool_call_config.py"
ORIGINS = ["established-mcp", "owned-mcp", "native", "custom"]


def run(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *map(str, args)],
        capture_output=True, text=True, timeout=180)


def descriptor(origin="native", name="runtime.echo", state=False):
    return {
        "schema": "tool-call-config/tool-descriptor/v1",
        "origin_class": origin,
        "callable_name": name,
        "provider_or_owner": "fixture-owner",
        "runtime_or_server": "fixture-runtime",
        "namespace": "fixture",
        "version": "1.0.0",
        "discovery_route": "fixture registry",
        "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}},
        "output_schema": {"type": "object", "properties": {"text": {"type": "string"}}},
        "capabilities": {
            "read_only": not state,
            "state_changing": state,
            "approval_required": state,
            "idempotent": not state,
            "supports_progress": False,
            "supports_cancellation": False,
            "supports_readback": state,
            "safe_retry_conditions": ["execution is proved absent"],
            "known_failures": ["invalid input"],
        },
        "sources": [{"locator": "fixture", "status": "verified"}],
    }


def behavior(action="Report the validated result after every call."):
    return {"schema": "tool-call-config/behavior/v1", "rules": [{
        "original": action, "timing": "after", "trigger": "every call",
        "strength": "required", "action": action, "target": "tool result",
        "enforcement": "instruction-only", "success_evidence": "result is reported",
        "failure_branch": "stop and report", "precedence": 10,
    }]}


def write(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


class TestGrammar(unittest.TestCase):
    def test_help_lists_only_public_commands(self):
        result = run("help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for command in ["help", "generate", "apply"]:
            self.assertIn(command, result.stdout)

    def test_missing_behavior_is_usage_error(self):
        result = run("generate", "runtime.echo")
        self.assertEqual(result.returncode, 2)
        self.assertIn("behavior", result.stderr.lower())

    def test_plain_tool_and_behavior_aliases_generate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.json"
            write(registry, {"tools": [descriptor()]})
            result = run("runtime.echo", "--behavior", "Report every result.",
                         "--registry", f"@{registry}", "--output", root / "out")
        self.assertEqual(result.returncode, 0, result.stderr)


class TestOriginsAndIdentity(unittest.TestCase):
    def test_each_supported_origin_generates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            behavior_path = root / "behavior.json"
            write(behavior_path, behavior())
            for origin in ORIGINS:
                tool = root / f"{origin}.json"
                write(tool, descriptor(origin, f"{origin}.status"))
                result = run("generate", f"@{tool}", "--behavior",
                             f"@{behavior_path}", "--output", root / origin)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_server_or_collection_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "server.json"
            write(path, {"server": "fixture", "tools": [descriptor(), descriptor(name="runtime.two")]})
            result = run("generate", f"@{path}", "--behavior", "Report results.",
                         "--output", Path(tmp) / "out")
        self.assertEqual(result.returncode, 2)
        self.assertIn("exactly one", result.stderr.lower())

    def test_ambiguous_registry_name_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.json"
            write(registry, {"tools": [descriptor(name="status"),
                                        descriptor("custom", "status")]})
            result = run("generate", "status", "--registry", f"@{registry}",
                         "--behavior", "Report results.", "--output", root / "out")
        self.assertEqual(result.returncode, 2)
        self.assertIn("2 tools", result.stderr)

    def test_unavailable_sources_block_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tool = root / "tool.json"
            value = descriptor()
            value["sources"] = [{"locator": "fixture", "status": "unavailable"}]
            write(tool, value)
            result = run("generate", f"@{tool}", "--behavior", "Report results.",
                         "--output", root / "out")
        self.assertEqual(result.returncode, 1)
        self.assertIn("verified source", result.stderr.lower())

    def test_cross_origin_names_do_not_collide(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            names = []
            for origin in ["native", "custom"]:
                tool = root / f"{origin}.json"
                write(tool, descriptor(origin, "status"))
                result = run("generate", f"@{tool}", "--behavior", "Report results.",
                             "--output", root / origin)
                names.append(json.loads(result.stdout)["generated_name"])
        self.assertEqual(len(set(names)), 2)


class TestMaterialOutput(unittest.TestCase):
    def generate_text(self, root, state, action, label):
        tool = root / f"tool-{label}.json"
        rules = root / f"behavior-{label}.json"
        output = root / f"output-{label}"
        write(tool, descriptor(name=f"fixture.{label}", state=state))
        write(rules, behavior(action))
        result = run("generate", f"@{tool}", "--behavior", f"@{rules}", "--output", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        path = Path(json.loads(result.stdout)["skill_path"]) / "SKILL.md"
        return path.read_text(encoding="utf-8")

    def test_read_only_and_state_changing_guidance_differs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            read_text = self.generate_text(root, False, "Summarize each result.", "read")
            write_text = self.generate_text(root, True, "Read back each saved value.", "write")
        self.assertNotEqual(read_text, write_text)
        self.assertNotIn("independent readback", read_text.lower())
        self.assertIn("independent readback", write_text.lower())
        self.assertIn("approval", write_text.lower())

    def test_different_behaviors_change_same_tool_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = self.generate_text(root, False, "Redact emails from results.", "first")
            second = self.generate_text(root, False, "Preserve emails in results.", "second")
        self.assertNotEqual(first, second)
        self.assertIn("Redact emails", first)
        self.assertIn("Preserve emails", second)

    def test_generated_package_has_registry_evidence_and_current_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tool = root / "tool.json"
            rules = root / "behavior.json"
            write(tool, descriptor("owned-mcp", "sandbox.read-note"))
            write(rules, behavior("Validate and report each returned note."))
            result = run("generate", f"@{tool}", "--behavior", f"@{rules}",
                         "--output", root / "out")
            package = Path(json.loads(result.stdout)["skill_path"])
            evidence = Path(json.loads(result.stdout)["evidence_dir"])
            lineage = json.loads(
                (package / "evals" / "source-lineage.json").read_text())
            required = {"manifest.json", "cases.json", "trigger-cases.json",
                        "contract.md", "rubric.md", "speed-budgets.json"}
            actual = {path.name for path in (package / "evals").iterdir()}
            matrix = json.loads((evidence / "rule-to-contract.json").read_text())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(required <= actual)
        self.assertEqual(lineage["public_version"], "0.1.0")
        self.assertIn("SKILL.md", {row["path"] for row in lineage["source_files"]})
        self.assertEqual(len(matrix["rules"]), 1)
        self.assertEqual(matrix["rules"][0]["disposition"], "instruction-only")

    def test_generated_frontmatter_resolves_formatter_stable_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tool = root / "tool.json"
            rules = root / "behavior.json"
            write(tool, descriptor(name="fixture.formatted"))
            write(rules, behavior())
            result = run("generate", f"@{tool}", "--behavior", f"@{rules}",
                         "--output", root / "out")
            report = json.loads(result.stdout)
            source = (Path(report["skill_path"]) / "SKILL.md").read_text()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"name: {report['generated_name']}\n", source)
        self.assertNotIn("@@NAME@@", source)
        self.assertNotIn("{ { NAME } }", source)


if __name__ == "__main__":
    unittest.main()
