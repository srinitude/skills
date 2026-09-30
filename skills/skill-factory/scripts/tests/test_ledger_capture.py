"""Real read boundaries for large ledgers; no semantic acceptance claim."""
import hashlib
import json
import subprocess
import unittest
from test_review_ledger_runtime import (
    ROOT, _TestLedgerRuntime_setUp, _TestLedgerRuntime_invoke,
    _TestLedgerRuntime_result,
)


def append_padding(path):
    with path.open("ab") as stream:
        for _ in range(513):
            stream.write(b" " * 1024 * 1024)


class TestLedgerCapture(unittest.TestCase):
    setUp = _TestLedgerRuntime_setUp
    invoke = _TestLedgerRuntime_invoke
    result = _TestLedgerRuntime_result

    def test_large_capture_and_invalid_utf8_recovery(self):
        original = self.ledger.read_bytes()
        self.ledger.write_bytes(b"\xff")
        self.assertEqual(self.invoke().returncode, 1)
        self.ledger.write_bytes(original)
        append_padding(self.ledger)
        result = self.result(self.invoke())
        self.assertEqual(result["ledger"]["bytes"], self.ledger.stat().st_size)
        self.assertEqual(json.loads(result["view_text"])["edges"],
                         self.data["semantic_model"]["relationships"])


def test_view_rechecks_live_bytes_and_preserves_inline_capture():
    case = TestLedgerCapture()
    case.setUp()
    try:
        original = case.ledger.read_bytes()
        request = {"action": "trace", "selector": "source:read", "depth": 0,
                   "ledger": str(case.ledger),
                   "ledger_sha256": hashlib.sha256(original).hexdigest()}
        command = ["python3", str(ROOT / "scripts/review_ledger.py"), "view"]
        def invoke(payload):
            return subprocess.run(command, input=json.dumps(payload), text=True,
                                  capture_output=True, timeout=30)
        case.ledger.write_bytes(original + b" ")
        failed = invoke({"request": request})
        assert failed.returncode == 1 and "ledger changed" in failed.stderr
        case.ledger.write_bytes(original)
        assert invoke({"request": request}).returncode == 0
        assert invoke({"request": request, "ledger_text": original.decode()}).returncode == 0
        assert invoke({"request": request, "ledger_text": "{}"}).returncode == 1
    finally:
        case.doCleanups()


def load_tests(loader, tests, pattern):
    return unittest.TestSuite([
        *loader.loadTestsFromTestCase(TestLedgerCapture),
        unittest.FunctionTestCase(test_view_rechecks_live_bytes_and_preserves_inline_capture),
    ])
