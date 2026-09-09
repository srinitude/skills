"""Independent malformed, stale, and forbidden artifact attempts at acceptance."""
import tempfile
import unittest
from pathlib import Path

from acceptance_fixtures import invoke, setup, write_json
from test_acceptance_bindings import digest


class TestEvidenceRejections(unittest.TestCase):
    def test_ambiguous_json_cannot_become_accepted_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            root, context, receipt, context_sha, receipt_sha = setup(base)
            artifact = base / "evidence/row-2.json"
            original = artifact.read_bytes()
            for suffix in [b', "ambiguous": NaN}', b', "state": "passed"}']:
                raw = original.rstrip()[:-1] + suffix
                artifact.write_bytes(raw)
                receipt["acceptance"]["claims"]["ROW-2"]["sha256"] = digest(raw)
                current = write_json(base / "receipt.json", receipt)
                result = invoke(base, context_sha, current)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertNotIn("Traceback", result.stderr)

    def test_expired_and_malformed_validity_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            root, context, receipt, context_sha, receipt_sha = setup(base)
            for value, expected in [({"not_before": 0, "expires_at": 1}, "expired"),
                                    ({"not_before": True, "expires_at": 9999999999}, "invalid acceptance validity")]:
                context["validity"] = value
                altered = write_json(base / "context.json", context)
                result = invoke(base, altered, receipt_sha)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stdout)

    def test_artifact_cannot_escape_host_root_even_with_matching_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            root, context, receipt, context_sha, receipt_sha = setup(base)
            artifact = base / "evidence/row-2.json"
            (base / "outside.json").write_bytes(artifact.read_bytes())
            claim = receipt["acceptance"]["claims"]["ROW-2"]
            claim["path"] = "../outside.json"
            altered = write_json(base / "receipt.json", receipt)
            result = invoke(base, context_sha, altered)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("host-approved root", result.stdout)
