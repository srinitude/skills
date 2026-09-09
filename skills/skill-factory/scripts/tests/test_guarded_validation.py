"""Keep selected checks separate from bound target acceptance."""
import tempfile
import unittest
from pathlib import Path

from cli import run
from publication_fixtures import evidence
from variant_fixtures import package


class TestGuardedValidation(unittest.TestCase):
    def test_selected_checks_cannot_borrow_stale_or_other_route_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            root = package(base / "file-inventory", "user")
            result = run("check_target.py", "validate", root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("evidence acceptance: pending", result.stdout)
            expected = {"route": "validate-target", "target": str(root), "inputs": {"mode": "validate"}}
            flags = evidence(base, root, expected)
            result = run("check_target.py", "eval", root, *flags)
            self.assertNotEqual(result.returncode, 0)
            artifact = base / "evidence.json"
            original = artifact.read_bytes()
            artifact.write_bytes(original + b" ")
            result = run("check_target.py", "validate", root, *flags)
            self.assertNotEqual(result.returncode, 0)
            artifact.write_bytes(original)
            result = run("check_target.py", "validate", root, *flags)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("host-bound claims", result.stdout)


if __name__ == "__main__":
    unittest.main()
