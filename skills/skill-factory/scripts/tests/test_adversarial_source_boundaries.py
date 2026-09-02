"""Adversarial tests for independent source classification."""
import json
import tempfile
import unittest
from pathlib import Path

from cli import run


def write_marker(root, relative):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}", encoding="utf-8")


class TestUnknownHostShapes(unittest.TestCase):
    def test_known_client_does_not_hide_unknown_host_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_marker(root, ".cursor-plugin/plugin.json")
            write_marker(root, ".future-agent/skill.txt")
            result = run("check_source_corpus.py", root)
            report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(report["detected_clients"], ["cursor"])
        self.assertEqual(report["unclassified"], [".future-agent/skill.txt"])

    def test_external_marker_symlink_cannot_classify_source(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "source"
            root.mkdir()
            external = base / "external.json"
            external.write_text("{}", encoding="utf-8")
            marker = root / ".cursor-plugin/plugin.json"
            marker.parent.mkdir()
            marker.symlink_to(external)
            result = run("check_source_corpus.py", root)
            report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(report["detected_clients"], [])
        self.assertEqual(report["symlinks"], [".cursor-plugin/plugin.json"])

    def test_symlinked_repository_root_fails_before_classification(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "source"
            root.mkdir()
            write_marker(root, ".cursor-plugin/plugin.json")
            linked = base / "linked-source"
            linked.symlink_to(root, target_is_directory=True)
            result = run("check_source_corpus.py", linked)
            report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("symlink", " ".join(report["problems"]).lower())


if __name__ == "__main__":
    unittest.main()
