"""Apply workflow tests through the public command."""
import hashlib
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


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_lineage(target):
    evals = target / "evals"
    evals.mkdir()
    (evals / "cases.json").write_text(
        json.dumps({"groups": [{"cases": [{"id": "EX-001"}]}]}), encoding="utf-8")
    (evals / "source-lineage.json").write_text(json.dumps({
        "schema": "source-lineage/v1", "public_version": "0.1.0",
        "source_case_ids": ["EX-001"], "sources": [], "source_files": [],
        "public_files": [], "native_manifest_sha256": "",
    }), encoding="utf-8")


def setup(root):
    skills = root / "skills"
    target = skills / "existing-skill"
    target.mkdir(parents=True)
    body = "---\nname: existing-skill\ndescription: 'Use when testing apply.'\n---\n\n# Existing\n\n## Run\n\nKeep sibling_tool behavior unchanged.\n"
    (target / "SKILL.md").write_text(body, encoding="utf-8")
    (target / "unrelated.txt").write_text("keep me\n", encoding="utf-8")
    write_lineage(target)
    tool = root / "tool.json"
    tool.write_text(json.dumps({
        "schema": "tool-call-config/tool-descriptor/v1", "origin_class": "native",
        "callable_name": "exact_tool", "provider_or_owner": "fixture",
        "runtime_or_server": "fixture", "namespace": "fixture", "version": "1",
        "discovery_route": "fixture", "input_schema": {"type": "object"},
        "output_schema": {"type": "object"},
        "capabilities": {"read_only": True, "state_changing": False},
        "sources": [{"locator": "fixture", "status": "verified"}],
    }), encoding="utf-8")
    behavior = root / "behavior.json"
    behavior.write_text(json.dumps({"rules": [{
        "original": "Validate arguments before exact_tool.", "timing": "before",
        "action": "validate arguments", "strength": "required",
    }]}), encoding="utf-8")
    return skills, target, tool, behavior


def plan(path, target, tool_hash, behavior_hash, fail=False):
    command = [sys.executable, "-c", "raise SystemExit(1)"] if fail else []
    value = {
        "schema": "tool-call-config/integration-plan/v1",
        "tool_identity_hash": tool_hash, "behavior_hash": behavior_hash,
        "expected_hashes": {"SKILL.md": digest(target / "SKILL.md")},
        "declared_files": ["SKILL.md", "references/exact-tool.md",
                           "evals/source-lineage.json"],
        "operations": [
            {"kind": "insert_before", "path": "SKILL.md", "anchor": "## Run",
             "marker": "exact-tool-v1", "content": "## Exact tool configuration\n\nRead references/exact-tool.md before every exact_tool call.\n\n"},
            {"kind": "add", "path": "references/exact-tool.md",
             "content": "# exact_tool\n\nValidate arguments before exact_tool.\n"},
        ],
        "validation_commands": [command] if command else [],
        "lineage": {"path": "evals/source-lineage.json",
                    "case_files": ["evals/cases.json"],
                    "public_version": "0.1.1"},
        "dispositions": [{"rule_id": "B-fixture", "status": "instruction-only"}],
    }
    path.write_text(json.dumps(value), encoding="utf-8")


def command(skills, tool, behavior, plan_path):
    return ("apply", f"@{tool}", "--target", "existing-skill", "--skills-root",
            skills, "--behavior", f"@{behavior}", "--integration", f"@{plan_path}")


class TestApply(unittest.TestCase):
    def prepare(self, root, fail=False):
        skills, target, tool, behavior = setup(root)
        probe = run("generate", f"@{tool}", "--behavior", f"@{behavior}",
                    "--output", root / "probe")
        report = json.loads(probe.stdout)
        plan_path = root / "plan.json"
        plan(plan_path, target, report["tool_identity_hash"],
             report["behavior_hash"], fail)
        return skills, target, tool, behavior, plan_path

    def test_apply_preserves_unrelated_behavior_and_second_run_is_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills, target, tool, behavior, plan_path = self.prepare(root)
            before = (target / "unrelated.txt").read_bytes()
            first = run(*command(skills, tool, behavior, plan_path))
            second = run(*command(skills, tool, behavior, plan_path))
            text = (target / "SKILL.md").read_text(encoding="utf-8")
            lineage = json.loads(
                (target / "evals" / "source-lineage.json").read_text())
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(json.loads(first.stdout)["status"], "applied")
        self.assertEqual(json.loads(second.stdout)["status"], "no-op")
        self.assertEqual(text.count("Exact tool configuration"), 1)
        self.assertIn("sibling_tool behavior unchanged", text)
        self.assertEqual(before, b"keep me\n")
        self.assertEqual(lineage["public_version"], "0.1.1")
        self.assertEqual(lineage["source_case_ids"], ["EX-001"])
        self.assertIn("SKILL.md", {row["path"] for row in lineage["source_files"]})

    def test_stale_plan_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills, target, tool, behavior, plan_path = self.prepare(root)
            (target / "SKILL.md").write_text("changed concurrently\n", encoding="utf-8")
            result = run(*command(skills, tool, behavior, plan_path))
        self.assertEqual(result.returncode, 1)
        self.assertIn("stale", result.stderr.lower())

    def test_failed_validation_rolls_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills, target, tool, behavior, plan_path = self.prepare(root, fail=True)
            before = (target / "SKILL.md").read_bytes()
            result = run(*command(skills, tool, behavior, plan_path))
            after = (target / "SKILL.md").read_bytes()
        self.assertEqual(result.returncode, 1)
        self.assertEqual(before, after)
        self.assertFalse((target / "references" / "exact-tool.md").exists())
        self.assertIn("rolled back", result.stderr.lower())

    def test_symlinked_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills, target, tool, behavior, plan_path = self.prepare(root)
            alias = skills / "alias"
            alias.symlink_to(target, target_is_directory=True)
            args = list(command(skills, tool, behavior, plan_path))
            args[args.index("existing-skill")] = "alias"
            result = run(*args)
        self.assertEqual(result.returncode, 2)
        self.assertIn("symlink", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
