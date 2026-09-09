"""Exercise reviewed bytes at the actual variant publication consumer."""
import json
import tempfile
import unittest
from pathlib import Path

from test_skill_variant import plan
from variant_fixtures import package, project, review
from variant_accept import publish


class TestReviewedCandidate(unittest.TestCase):
    def test_changed_candidate_cannot_be_published_after_review(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            source = package(base / "source/demo-skill", "user")
            candidate = package(base / "candidate/atlas-inventory", "project")
            atlas = project(base / "atlas")
            destination = base / "accepted"
            destination.mkdir()
            result = plan(source, destination, "project", candidate.name,
                          "--project", atlas, "--project-id", "repo:atlas")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads(result.stdout)
            evidence = review(source, candidate, [(atlas, "Python src")])
            (candidate / "assets/changed-after-review.txt").write_text("Unreviewed content.\n")
            with self.assertRaisesRegex(ValueError, "reviewed candidate"):
                publish(data, candidate, evidence, destination / candidate.name, None)
            self.assertEqual(list(destination.iterdir()), [])
