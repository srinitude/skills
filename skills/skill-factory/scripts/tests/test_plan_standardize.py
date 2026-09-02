"""Tests for the read-only skill standardization planner."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run


class TestPlanStandardizeCli(unittest.TestCase):
    def test_help_documents_usage_and_exit_codes(self):
        result = run("plan_standardize.py", "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage", result.stdout.lower())
        self.assertIn("exit code", result.stdout.lower())

    def test_missing_target_is_usage_error(self):
        result = run("plan_standardize.py")
        self.assertEqual(result.returncode, 2)

    def test_non_skill_fails_without_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            result = run("plan_standardize.py", temp)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(list(Path(temp).iterdir()), [])


class TestPlanStandardizeReport(unittest.TestCase):
    def test_runtime_cache_files_are_excluded_from_baseline(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "SKILL.md").write_text("---\nname: demo\n---\n",
                                            encoding="utf-8")
            cache = root / "scripts" / "__pycache__"
            cache.mkdir(parents=True)
            (cache / "check.cpython-311.pyc").write_bytes(b"runtime cache")
            result = run("plan_standardize.py", root)
        report = json.loads(result.stdout)
        paths = [item["path"] for item in report["files"]]
        self.assertFalse(any("__pycache__" in path for path in paths))

    def test_report_freezes_files_and_missing_standard_owners(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "SKILL.md").write_text("---\nname: demo\n---\n", encoding="utf-8")
            (root / "domain.txt").write_text("preserve me\n", encoding="utf-8")
            result = run("plan_standardize.py", root)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["target"], str(root.resolve()))
        self.assertIn("domain.txt", [item["path"] for item in report["files"]])
        self.assertIn("mise.toml", report["missing_required"])
        self.assertIn("assets/use-case-contract.json",
                      report["missing_required"])
        self.assertIn("assets/decision-records.json",
                      report["missing_required"])
        self.assertIn("assets/invocation-receipt-template.json",
                      report["missing_required"])
        self.assertIn("SKILL.md", report["present_required"])
        self.assertTrue(report["baseline_digest"].startswith("sha256:"))
        self.assertEqual(report["writes"], 0)

    def test_report_maps_host_specific_paths_to_portable_owners(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "SKILL.md").write_text("---\nname: demo\n---\n", encoding="utf-8")
            (root / "CLAUDE.md").write_text("rules\n", encoding="utf-8")
            (root / ".codex").mkdir()
            (root / ".codex" / "skills.txt").write_text("rules\n", encoding="utf-8")
            (root / "GEMINI.md").write_text("rules\n", encoding="utf-8")
            (root / ".cursor").mkdir()
            (root / ".cursor" / "rules.txt").write_text("rules\n", encoding="utf-8")
            result = run("plan_standardize.py", root)
        self.assertEqual(result.returncode, 1, result.stdout)
        report = json.loads(result.stdout)
        mappings = {item["source"]: item["destination"]
                    for item in report["portable_path_map"]}
        self.assertEqual(mappings["CLAUDE.md"], "AGENTS.md")
        self.assertEqual(mappings[".codex/skills.txt"], ".agents/skills.txt")
        self.assertEqual(mappings["GEMINI.md"], "AGENTS.md")
        self.assertEqual(mappings[".cursor/rules.txt"], ".agents/rules.txt")
        self.assertEqual(report["unknown_shape_policy"], "BLOCKED")
        self.assertEqual(len(report["path_collisions"]), 1)

    def test_unknown_host_owner_fails_closed_in_plan(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "SKILL.md").write_text("---\nname: demo\n---\n", encoding="utf-8")
            (root / ".future-agent").mkdir()
            path = root / ".future-agent" / "skills.txt"
            path.write_text("rules\n", encoding="utf-8")
            result = run("plan_standardize.py", root)
        report = json.loads(result.stdout)
        self.assertEqual(report["unclassified_host_paths"],
                         [".future-agent/skills.txt"])

    def test_symlinked_skill_root_fails_before_inventory(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "demo"
            root.mkdir()
            (root / "SKILL.md").write_text("---\nname: demo\n---\n",
                                            encoding="utf-8")
            linked = base / "linked-demo"
            linked.symlink_to(root, target_is_directory=True)
            result = run("plan_standardize.py", linked)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("symlink", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
