"""Local owned-MCP discovery and safe state proof."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
SERVER = SKILL / "scripts" / "fixture_server.py"


def transact(root, requests):
    payload = "".join(json.dumps(item) + "\n" for item in requests)
    return subprocess.run(
        [sys.executable, str(SERVER), "--root", str(root)], input=payload,
        capture_output=True, text=True, timeout=30)


class TestOwnedMcpFixture(unittest.TestCase):
    def test_lists_two_exact_tools_and_reads_back_safe_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            requests = [
                {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                 "params": {"name": "sandbox.write-note",
                            "arguments": {"key": "proof", "text": "saved"}}},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                 "params": {"name": "sandbox.read-note",
                            "arguments": {"key": "proof"}}},
            ]
            result = transact(root, requests)
            replies = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(result.returncode, 0, result.stderr)
        names = [tool["name"] for tool in replies[0]["result"]["tools"]]
        self.assertEqual(names, ["sandbox.write-note", "sandbox.read-note"])
        self.assertEqual(replies[1]["result"]["content"][0]["text"], "proof")
        self.assertEqual(replies[2]["result"]["content"][0]["text"], "saved")

    def test_rejects_escaping_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = transact(Path(tmp), [{
                "jsonrpc": "2.0", "id": 1, "method": "tools/call",
                "params": {"name": "sandbox.write-note",
                           "arguments": {"key": "../escape", "text": "no"}},
            }])
            reply = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(reply["error"]["code"], -32602)


if __name__ == "__main__":
    unittest.main()
