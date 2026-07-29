import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "validate_verdict.py"
VALID = "# Human action verdict\n\n## Exact behavior\n\n## Verdict\n\nINSUFFICIENT EVIDENCE\n\n## Evidence ledger\n\n## Reference class and transport\n\n## Mechanisms\n\n## Evidence and scope limits\n\n## What would change the verdict\n\n## Next ethical test\n\n## Sources\n\nhttps://example.org/source\n\n## Research log"
UNVALIDATED = VALID.replace("INSUFFICIENT EVIDENCE", "UNVALIDATED HYPOTHESIS").replace("https://example.org/source", "No live sources because research was unavailable.")
MISSING = VALID.replace("## Sources\n\nhttps://example.org/source\n\n", "")


def run_validator(source):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "verdict.md"
        path.write_text(source, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--input", str(path)],
            capture_output=True,
            text=True,
        )


class ValidDocumentTests(unittest.TestCase):
    def test_valid_document_passes(self):
        result = run_validator(VALID)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "PASS")

    def test_unvalidated_document_needs_no_url(self):
        result = run_validator(UNVALIDATED)
        self.assertEqual(result.returncode, 0, result.stderr)


class InvalidDocumentTests(unittest.TestCase):
    def test_missing_heading_fails(self):
        result = run_validator(MISSING)
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing heading", result.stdout)

    def test_bad_usage_exits_two(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
