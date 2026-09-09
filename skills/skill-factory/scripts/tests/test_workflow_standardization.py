"""Actual domain preparation, persistent review pause and guarded promotion.

The positive evidence covers a disposable mechanical source only. These tests
are not human approval, complete output acceptance or whole-factory acceptance.
"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR
from publication_fixtures import evidence
from skill_package import inventory, tree_digest
from test_standardization_inputs import prepare


def invoke(action, base, source, profile, candidate, *extra):
    command = ["node", str(SKILL_DIR / "scripts/workflow.ts"), action,
               "--state-dir", str(base / "state"), "--run-id", "standardization-test",
               "--source", str(source), "--profile", str(profile),
               "--candidate", str(candidate), "--scope", "user", "--audience", "agent"]
    return subprocess.run([*command, *map(str, extra)], capture_output=True,
                          text=True, cwd=SKILL_DIR, timeout=60)


def review_flags(base, candidate, report):
    root = base / "evidence"
    root.mkdir()
    return evidence(root, candidate, {"route": "standardize-target",
        "target": report["target"], "inputs": report["consumer_inputs"]})


class TestStandardizationWorkflow(unittest.TestCase):
    def test_real_preparation_suspends_and_new_process_promotes_only_bound_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            source, profile, candidate = prepare(base)
            before = inventory(source)
            started = invoke("start", base, source, profile, candidate)
            self.assertEqual(started.returncode, 3, started.stdout + started.stderr)
            report = json.loads(started.stdout)
            self.assertEqual(report["domain_status"], "pending")
            self.assertEqual(inventory(source), before)
            self.assertTrue((candidate / "assets/use-case-contract.json").is_file())
            flags = review_flags(base, candidate, report)
            missing = invoke("resume", base, source, profile, candidate)
            self.assertNotEqual(missing.returncode, 0)
            self.assertEqual(inventory(source), before)
            resumed = invoke("resume", base, source, profile, candidate, *flags)
            self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
            self.assertEqual(json.loads(resumed.stdout)["domain_status"], "accepted")
            self.assertEqual(inventory(source), inventory(candidate))
            repeated = invoke("resume", base, source, profile, candidate, *flags)
            self.assertNotEqual(repeated.returncode, 0)

    def test_changed_candidate_rejects_without_changing_original(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            source, profile, candidate = prepare(base)
            before = inventory(source)
            started = invoke("start", base, source, profile, candidate)
            self.assertEqual(started.returncode, 3, started.stdout + started.stderr)
            flags = review_flags(base, candidate, json.loads(started.stdout))
            body = (candidate / "SKILL.md").read_bytes()
            (candidate / "SKILL.md").write_bytes(body + b"\n")
            rejected = invoke("resume", base, source, profile, candidate, *flags)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(inventory(source), before)
            (candidate / "SKILL.md").write_bytes(body)
            recovered = invoke("resume", base, source, profile, candidate, *flags)
            self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
            self.assertEqual(inventory(source), inventory(candidate))

    def test_stale_evidence_keeps_the_pause_recoverable(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            source, profile, candidate = prepare(base)
            before = inventory(source)
            started = invoke("start", base, source, profile, candidate)
            self.assertEqual(started.returncode, 3, started.stdout + started.stderr)
            flags = review_flags(base, candidate, json.loads(started.stdout))
            artifact = base / "evidence/evidence.json"
            content = artifact.read_bytes()
            artifact.write_bytes(content + b" ")
            rejected = invoke("resume", base, source, profile, candidate, *flags)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(inventory(source), before)
            artifact.write_bytes(content)
            recovered = invoke("resume", base, source, profile, candidate, *flags)
            self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
            self.assertEqual(inventory(source), inventory(candidate))

    def test_rejection_is_terminal_and_preserves_original(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            source, profile, candidate = prepare(base)
            before = tree_digest(inventory(source))
            started = invoke("start", base, source, profile, candidate)
            self.assertEqual(started.returncode, 3, started.stdout + started.stderr)
            rejected = invoke("reject", base, source, profile, candidate)
            self.assertEqual(rejected.returncode, 1, rejected.stdout + rejected.stderr)
            self.assertEqual(json.loads(rejected.stdout)["domain_status"], "rejected")
            self.assertEqual(tree_digest(inventory(source)), before)
            repeated = invoke("resume", base, source, profile, candidate)
            self.assertNotEqual(repeated.returncode, 0)


if __name__ == "__main__":
    unittest.main()
