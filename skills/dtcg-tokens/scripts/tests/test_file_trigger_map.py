"""Prove that every shipped file has one real activation or consumption route."""
import json
import pathlib
import subprocess
import sys
import unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
POLICY_PATH = SKILL_DIR / "assets" / "file-trigger-policy.json"
AUDITOR = SKILL_DIR / "scripts" / "audit_file_triggers.py"


def persistent_files():
    return {
        path.relative_to(SKILL_DIR).as_posix()
        for path in SKILL_DIR.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }


class FileTriggerMapTests(unittest.TestCase):
    def load_policy(self):
        self.assertTrue(POLICY_PATH.is_file(), "assets/file-trigger-policy.json must exist")
        return json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    def test_generated_cache_files_are_not_shipped(self):
        generated = [
            path.relative_to(SKILL_DIR).as_posix()
            for path in SKILL_DIR.rglob("*")
            if path.is_file() and ("__pycache__" in path.parts or path.suffix == ".pyc")
        ]
        self.assertEqual(generated, [])

    def test_policy_names_only_bounded_discovery_routes(self):
        data = self.load_policy()
        self.assertEqual(data["version"], "1.0.0")
        self.assertEqual(set(data["roots"]), {"SKILL.md", "mise.toml", ".github/workflows/ci.yml"})
        self.assertNotIn("**/*", data["discovery"])
        for pattern, record in data["discovery"].items():
            self.assertTrue(pattern)
            self.assertTrue(record["trigger"])
            self.assertTrue(record["consumer"])

    def test_auditor_reads_current_bytes_and_passes(self):
        self.assertTrue(AUDITOR.is_file(), "scripts/audit_file_triggers.py must exist")
        result = subprocess.run(
            [sys.executable, str(AUDITOR), str(SKILL_DIR)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["files_read"], len(persistent_files()))
        self.assertEqual(report["unrouted"], [])
        self.assertEqual(report["missing_consumers"], [])
        self.assertEqual({entry["path"] for entry in report["routes"]}, persistent_files())
        for entry in report["routes"]:
            self.assertTrue(entry["trigger"], entry["path"])
            self.assertTrue(entry["consumers"] or entry["mode"] in {"activate", "configure"}, entry["path"])


if __name__ == "__main__":
    unittest.main()
