"""Tests for the current source-shape corpus."""
import json
import unittest
from pathlib import Path

from cli import run

SKILL_DIR = Path(__file__).resolve().parents[2]
CLIENTS = {
    "aider", "chatgpt", "claude-code", "codex",
    "continue", "cursor", "gemini-cli", "hermes-agent", "openclaw",
    "opencode",
}


class TestSourceCorpus(unittest.TestCase):
    def test_bundled_corpus_is_valid(self):
        result = run("check_source_corpus.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(set(report["clients"]), CLIENTS)
        self.assertEqual(report["package_formats"], ["agent-plugins-v1"])
        self.assertEqual(report["status"], "PASS")

    def test_live_corpus_markers_are_classified(self):
        source = Path("/tmp/srinitude-skills.Dymf5V")
        if not source.is_dir():
            self.skipTest("current source clone is not present")
        result = run("check_source_corpus.py", source)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["unclassified"], [])
        self.assertEqual(set(report["clients"]), CLIENTS)
        self.assertEqual(report["package_formats"], ["agent-plugins-v1"])

    def test_unknown_adapter_shape_fails_closed(self):
        corpus = SKILL_DIR / "assets" / "source-shape-corpus.json"
        data = json.loads(corpus.read_text(encoding="utf-8"))
        self.assertEqual(data["unknown_shape"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
