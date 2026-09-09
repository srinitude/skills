"""Create a reviewed package through new, keeping seed creation unaccepted."""
import tempfile
import unittest
import json
from pathlib import Path

from cli import run
from publication_fixtures import evidence
from skill_package import inventory, tree_digest
from skill_scope import read_fields
from variant_fixtures import package


class TestGuardedCreation(unittest.TestCase):
    def test_a_seed_cannot_claim_acceptance_or_installation(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            target = base / "seed"
            args = ["--name", "seed", "--description", "Use when source counts are needed.",
                    "--scope", "user", "--audience", "agent", "--dest", base]
            placement = base / "placement.json"
            placement.write_text(json.dumps({"kind": "installation", "scope": "user",
                "destination": str(target), "scope_root": str(base), "visible_roots": [str(base)],
                "reference": "https://agentskills.io/client-implementation/adding-skills-support"}))
            for extra in [["--placement-receipt", placement], ["--context-sha256", "0" * 64]]:
                result = run("scaffold_skill.py", *args, *extra)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("candidate", result.stdout)
                self.assertFalse(target.exists())

    def test_reviewed_creation_rejects_stale_evidence_and_preserves_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            candidate = package(base / "candidate" / "source-count", "user")
            destination = base / "accepted"
            destination.mkdir()
            description = read_fields(candidate)["description"]
            args = ["--name", candidate.name, "--description", description, "--scope", "user",
                    "--audience", "agent", "--dest", destination, "--candidate", candidate]
            result = run("scaffold_skill.py", *args)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((destination / candidate.name).exists())
            expected = {"route": "new", "target": str(destination / candidate.name),
                        "inputs": {"candidate": tree_digest(inventory(candidate)), "scope": "user",
                                   "audience": "agent", "description": description, "placement": "authoring"}}
            flags = evidence(base, candidate, expected)
            artifact = base / "evidence.json"
            original = artifact.read_bytes()
            artifact.write_bytes(original + b" ")
            result = run("scaffold_skill.py", *args, *flags)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
            self.assertFalse((destination / candidate.name).exists())
            artifact.write_bytes(original)
            before = inventory(candidate)
            result = run("scaffold_skill.py", *args, *flags)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(inventory(candidate), before)
            self.assertEqual(inventory(destination / candidate.name), before)


if __name__ == "__main__":
    unittest.main()
