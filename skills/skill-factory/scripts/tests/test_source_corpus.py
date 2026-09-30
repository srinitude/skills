"""Tests for the current source-shape corpus."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run
from test_adversarial_source_boundaries import write_marker

SKILL_DIR = Path(__file__).resolve().parents[2]
CLIENTS = {
    "aider", "chatgpt", "claude-code", "codex",
    "continue", "cursor", "gemini-cli", "hermes-agent", "openclaw",
    "opencode",
}


def test_full_corpus_markers_are_classified(self):
    corpus = SKILL_DIR / "assets" / "source-shape-corpus.json"
    data = json.loads(corpus.read_text(encoding="utf-8"))
    markers = {path for group in data["clients"] + data["package_formats"]
               for path in group["markers"]}
    with tempfile.TemporaryDirectory() as temp:
        source = Path(temp)
        for path in sorted(markers):
            write_marker(source, path)
        result = run("check_source_corpus.py", source)
        after = {p.relative_to(source).as_posix(): p.read_bytes()
                 for p in source.rglob("*") if p.is_file()}
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    report = json.loads(result.stdout)
    self.assertEqual(after, dict.fromkeys(markers, b"{}"))
    self.assertEqual(set(report["detected_clients"]), CLIENTS)
    self.assertEqual(report["detected_package_formats"], ["agent-plugins-v1"])
    self.assertEqual(report["missing_clients"], [])
    self.assertEqual(report["missing_package_formats"], [])
    self.assertEqual(report["unclassified"], [])
    self.assertEqual(report["symlinks"], [])


class TestSourceCorpus(unittest.TestCase):
    def test_bundled_corpus_is_valid(self):
        result = run("check_source_corpus.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(set(report["clients"]), CLIENTS)
        self.assertEqual(report["package_formats"], ["agent-plugins-v1"])
        self.assertEqual(report["status"], "PASS")

    test_full_corpus_markers_are_classified = test_full_corpus_markers_are_classified

    def test_unknown_adapter_shape_fails_closed(self):
        corpus = SKILL_DIR / "assets" / "source-shape-corpus.json"
        data = json.loads(corpus.read_text(encoding="utf-8"))
        self.assertEqual(data["unknown_shape"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
