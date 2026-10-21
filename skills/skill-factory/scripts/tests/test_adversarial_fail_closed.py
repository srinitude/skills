"""Adversarial tests for destructive and false-positive factory paths."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_task_graph_policy import task_text, write_skill as write_graph_skill
from test_use_case_contract import contract, write_skill


def write_marker(root, relative, text="{}"):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class TestScaffoldSafety(unittest.TestCase):
    def test_force_cannot_erase_an_existing_target(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "demo-skill"
            target.mkdir()
            marker = target / "user-work.txt"
            marker.write_text("preserve", encoding="utf-8")
            result = run("scaffold_skill.py", "--name", "demo-skill",
                         "--description", "Use when a demo is needed.",
                         "--dest", temp, "--scope", "user", "--force")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")

    def test_description_cannot_inject_frontmatter_lines(self):
        with tempfile.TemporaryDirectory() as temp:
            result = run("scaffold_skill.py", "--name", "demo-skill",
                         "--description", "Use when needed.\nmetadata: broken",
                         "--dest", temp, "--scope", "user")
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertFalse((Path(temp) / "demo-skill").exists())


def _TestPlanFailClosed_make_skill(self, root):
    write_marker(root, "SKILL.md", "---\nname: demo\n---\n")

def _TestPlanFailClosed_test_unknown_host_owner_returns_failure(self):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        self.make_skill(root)
        write_marker(root, ".future-agent/skill.txt", "rules")
        result = run("plan_standardize.py", root)
    self.assertEqual(result.returncode, 1, result.stdout)

def _TestPlanFailClosed_test_destination_collision_returns_failure(self):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        self.make_skill(root)
        write_marker(root, "CLAUDE.md", "one")
        write_marker(root, "CODEX.md", "two")
        result = run("plan_standardize.py", root)
    self.assertEqual(result.returncode, 1, result.stdout)

def _TestPlanFailClosed_test_symlink_is_reported_without_following_it(self):
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        root = base / "demo"
        root.mkdir()
        self.make_skill(root)
        secret = base / "secret.txt"
        secret.write_text("private", encoding="utf-8")
        (root / "linked.txt").symlink_to(secret)
        result = run("plan_standardize.py", root)
        report = json.loads(result.stdout)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertEqual(report["symlinks"], ["linked.txt"])
    self.assertNotIn("linked.txt", [item["path"] for item in report["files"]])


class TestPlanFailClosed(unittest.TestCase):
    make_skill = _TestPlanFailClosed_make_skill
    test_unknown_host_owner_returns_failure = _TestPlanFailClosed_test_unknown_host_owner_returns_failure
    test_destination_collision_returns_failure = _TestPlanFailClosed_test_destination_collision_returns_failure
    test_symlink_is_reported_without_following_it = _TestPlanFailClosed_test_symlink_is_reported_without_following_it


class TestSourceShapeClassification(unittest.TestCase):
    def test_one_recognized_client_pack_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_marker(root, ".cursor-plugin/plugin.json")
            result = run("check_source_corpus.py", root)
            report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(report["detected_clients"], ["cursor"])
        self.assertEqual(report["detected_package_formats"], [])

    def test_package_format_is_not_reported_as_a_client(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_marker(root, "plugin.json")
            write_marker(root, "mcp.json")
            result = run("check_source_corpus.py", root)
            report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(report["detected_clients"], [])
        self.assertEqual(report["detected_package_formats"], ["agent-plugins-v1"])

    def test_unrecognized_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_marker(root, "unknown.tool")
            result = run("check_source_corpus.py", root)
        self.assertEqual(result.returncode, 1, result.stdout)


def _TestSemanticFalsePositives_check_research(self, data):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "release-notes"
        root.mkdir()
        write_skill(root, data)
        return run("check_domain_research.py", root)

def _TestSemanticFalsePositives_check_use_case(self, data):
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp) / "release-notes"
        root.mkdir()
        write_skill(root, data)
        return run("check_use_case_contract.py", root)

def _TestSemanticFalsePositives_test_stale_research_receipt_fails_currentness(self):
    data = contract()
    data["research_receipts"][0]["checked_at"] = "2020-01-01T00:00:00+00:00"
    result = self.check_research(data)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertIn("current", result.stdout)

def _TestSemanticFalsePositives_test_future_research_receipt_fails_currentness(self):
    data = contract()
    data["disconfirmation"][0]["checked_at"] = "2099-01-01T00:00:00+00:00"
    result = self.check_research(data)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertIn("future", result.stdout)

def _TestSemanticFalsePositives_test_malformed_dimensions_fail_without_traceback(self):
    data = contract()
    data["research_receipts"][0]["dimensions"] = [{}]
    result = self.check_research(data)
    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
    self.assertNotIn("Traceback", result.stderr)
    self.assertIn("domain research:", result.stdout)

def _TestSemanticFalsePositives_test_one_letter_domain_terms_fail(self):
    data = contract()
    data["domain_terms"] = ["a", "e", "i"]
    result = self.check_use_case(data)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertIn("specific phrase", result.stdout)

def _TestSemanticFalsePositives_test_domain_terms_match_words_not_substrings(self):
    data = contract()
    data["domain_terms"] = ["git", "aud", "not"]
    data["outcome"] = "A digital audience notices change."
    result = self.check_use_case(data)
    self.assertEqual(result.returncode, 1, result.stdout)
    self.assertIn("outcome", result.stdout)


class TestSemanticFalsePositives(unittest.TestCase):
    check_research = _TestSemanticFalsePositives_check_research
    check_use_case = _TestSemanticFalsePositives_check_use_case
    test_stale_research_receipt_fails_currentness = _TestSemanticFalsePositives_test_stale_research_receipt_fails_currentness
    test_future_research_receipt_fails_currentness = _TestSemanticFalsePositives_test_future_research_receipt_fails_currentness
    test_malformed_dimensions_fail_without_traceback = _TestSemanticFalsePositives_test_malformed_dimensions_fail_without_traceback
    test_one_letter_domain_terms_fail = _TestSemanticFalsePositives_test_one_letter_domain_terms_fail
    test_domain_terms_match_words_not_substrings = _TestSemanticFalsePositives_test_domain_terms_match_words_not_substrings


class TestMarkdownBoundary(unittest.TestCase):
    def test_markdown_over_200_lines_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "reference.md"
            path.write_text("\n".join(f"# H{index}" for index in range(201)), encoding="utf-8")
            result = run("lint_writing.py", path)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("201 lines", result.stdout)


class TestTaskGraphBypass(unittest.TestCase):
    def test_nested_mise_in_a_command_array_fails(self):
        graph = task_text().replace(
            'run = "python3 scripts/tests.py"',
            'run = ["python3 scripts/tests.py", "mise run info"]')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "release-notes"
            root.mkdir()
            write_graph_skill(root, graph)
            result = run("check_task_graph.py", root)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("must not invoke Mise", result.stdout)


if __name__ == "__main__":
    unittest.main()
