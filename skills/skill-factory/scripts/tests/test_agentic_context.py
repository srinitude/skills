"""Exercise required context transport, not semantic or human acceptance."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

from test_agentic_request import CONTRACT, ROOT, digest, invoke_stdin, request


class TestInitialContext(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.ledger = self.root / "ledger.json"
        self.matrix = self.root / "matrix.md"
        self.ledger.write_bytes(b'{"rule":"Preserve each supplied UTF-8 byte sequence."}\r\n')
        self.matrix.write_bytes("Transport trial: caf\u00e9, before and after.\r\n".encode())
        self.contract = self.root / "use-case-contract.json"
        self.data = json.loads(CONTRACT.read_text())
        self.data["initial_context"] = [
            {"id": "matrix", "role": "resource", "path": "matrix.md",
             "sha256": digest(self.matrix), "depends_on": ["ledger"]},
            {"id": "ledger", "role": "ledger", "path": "ledger.json",
             "sha256": digest(self.ledger), "depends_on": []},
        ]
        self.payload = request(ROOT / "SKILL.md", ROOT / "SKILL.md")
        self.payload["context"] = [
            {"id": item["id"], "path": str(self.root / item["path"]),
             "sha256": item["sha256"]} for item in self.data["initial_context"]]

    def invoke(self, code="import json,sys; print(json.dumps(json.load(sys.stdin)['context']))"):
        self.contract.write_text(json.dumps(self.data), encoding="utf-8")
        self.payload["use_case"].update(path=str(self.contract), sha256=digest(self.contract))
        return invoke_stdin(json.dumps(self.payload), code)

    def assert_blocked(self, result):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("context", result.stderr.lower())
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_full_resources_reach_runner_in_dependency_order(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        context = json.loads(result.stdout)
        self.assertEqual([item["id"] for item in context], ["ledger", "matrix"])
        self.assertEqual([item["text"] for item in context],
                         [self.ledger.read_bytes().decode(), self.matrix.read_bytes().decode()])
        self.assertEqual([item["sha256"] for item in context],
                         [digest(self.ledger), digest(self.matrix)])

    def test_missing_declaration_blocks_before_runner(self):
        self.data.pop("initial_context")
        self.assert_blocked(self.invoke("print('RUNNER_STARTED')"))

    def test_missing_duplicate_and_extra_inputs_block_before_runner(self):
        good = self.payload["context"]
        for value in [None, {}, [], good[:1], good + [good[0]],
                      good + [{"id": "extra", "path": "unknown", "sha256": "0" * 64}]]:
            with self.subTest(value=value):
                self.payload["context"] = value
                self.assert_blocked(self.invoke("print('RUNNER_STARTED')"))

    def test_stale_and_wrong_resource_bindings_block_then_recover(self):
        self.matrix.write_text("changed")
        self.assert_blocked(self.invoke("print('RUNNER_STARTED')"))
        current = digest(self.matrix)
        self.data["initial_context"][0]["sha256"] = current
        self.payload["context"][0]["sha256"] = current
        self.assertEqual(self.invoke().returncode, 0)
        copy = self.root / "different.md"
        copy.write_bytes(self.matrix.read_bytes())
        self.payload["context"][0]["path"] = str(copy)
        self.assert_blocked(self.invoke("print('RUNNER_STARTED')"))

    def test_invalid_reading_graph_blocks_before_runner(self):
        original = json.dumps(self.data["initial_context"])
        for field, value in [("depends_on", ["missing"]), ("depends_on", "ledger"),
                             ("depends_on", ["matrix"]), ("depends_on", ["ledger", "ledger"]),
                             ("id", "ledger"), ("role", "unknown")]:
            with self.subTest(field=field, value=value):
                self.data["initial_context"] = json.loads(original)
                self.data["initial_context"][0][field] = value
                self.assert_blocked(self.invoke("print('RUNNER_STARTED')"))
        self.data["initial_context"] = json.loads(original)
        self.data["initial_context"][1]["depends_on"] = ["matrix"]
        self.assert_blocked(self.invoke("print('RUNNER_STARTED')"))

    def test_direct_dispatch_cannot_bypass_required_context(self):
        self.invoke()
        code = ("import json,sys; sys.path.insert(0, " + repr(str(ROOT / "scripts")) + "); "
                "from run_agentic_request import dispatch; "
                "dispatch([sys.executable,'-c',\"print('RUNNER_STARTED')\"],json.load(sys.stdin))")
        complete = self.payload.pop("context")
        for expected in [1, 0]:
            result = subprocess.run([sys.executable, "-c", code],
                                    input=json.dumps(self.payload), capture_output=True,
                                    text=True, check=False)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            self.assertEqual(result.stdout.strip(), "" if expected else "RUNNER_STARTED")
            self.payload["context"] = complete

    def test_ledger_and_nonempty_utf8_contents_are_required(self):
        self.data["initial_context"][1]["role"] = "resource"
        self.assert_blocked(self.invoke("print('RUNNER_STARTED')"))
        self.data["initial_context"][1]["role"] = "ledger"
        for content in [b"", b" \n", b"\xff"]:
            with self.subTest(content=content):
                self.matrix.write_bytes(content)
                current = digest(self.matrix)
                self.data["initial_context"][0]["sha256"] = current
                self.payload["context"][0]["sha256"] = current
                self.assert_blocked(self.invoke("print('RUNNER_STARTED')"))


    def test_invocation_binding_captures_selected_ledger_and_keeps_package_pins(self):
        self.data["initial_context"][1] = {
            "id": "ledger", "role": "ledger", "binding": "invocation", "depends_on": []}
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        captured = json.loads(result.stdout)
        self.assertEqual(captured[0]["text"], self.ledger.read_bytes().decode())
        self.assertEqual(captured[0]["binding"], "invocation")
        self.assertEqual(captured[1]["binding"], "package")
        self.ledger.write_text('{"rule":"Review this changed invocation source."}')
        self.assert_blocked(self.invoke("print('RUNNER_STARTED')"))
        self.payload["context"][1]["sha256"] = digest(self.ledger)
        recovered = self.invoke()
        self.assertEqual(recovered.returncode, 0, recovered.stderr)
        self.assertEqual(json.loads(recovered.stdout)[0]["text"], self.ledger.read_text())
        self.matrix.write_text("The pinned package matrix has changed.")
        self.payload["context"][0]["sha256"] = digest(self.matrix)
        self.assert_blocked(self.invoke("print('RUNNER_STARTED')"))

    def test_only_contract_can_select_invocation_binding(self):
        original = json.dumps(self.data["initial_context"])
        for binding in ["unknown", None, [], {}]:
            with self.subTest(binding=binding):
                self.data["initial_context"] = json.loads(original)
                self.data["initial_context"][1]["binding"] = binding
                self.assert_blocked(self.invoke("print('RUNNER_STARTED')"))
        self.data["initial_context"] = json.loads(original)
        self.data["initial_context"][1]["binding"] = "invocation"
        self.assert_blocked(self.invoke("print('RUNNER_STARTED')"))
        self.data["initial_context"] = json.loads(original)
        self.payload["context"][1]["binding"] = "invocation"
        self.assert_blocked(self.invoke("print('RUNNER_STARTED')"))

if __name__ == "__main__":
    unittest.main()
