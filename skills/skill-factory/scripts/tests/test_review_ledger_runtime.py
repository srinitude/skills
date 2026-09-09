"""Actual native ledger workflow cases; no model or domain acceptance claim."""
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class TestLedgerRuntime(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.ledger = self.folder / "ledger.json"
        self.request = self.folder / "request.json"
        rules = [{"id": name, "text": text} for name, text in
                 [("read", "Read current evidence."), ("write", "Preserve authorized bytes."), ("review", "Review the actual change.")]]
        source = "\n".join(row["text"] for row in rules).encode()
        definition = {"family": "meaning", "meaning": "Provides a stated motive.",
                      "transitivity": "not implied", "review_state": "reviewed"}
        edge = {"id": "reason", "type": "motivates", "from": ["source:read", "source:review"],
                "to": "source:write", "condition": "Only within the authorized change.",
                "meaning": "The two source duties jointly motivate preserving the reviewed change.",
                "basis": ["source:read", "source:write", "source:review"], "review_state": "candidate",
                "roles": ["evidence", "judgment"], "extension": {"preserve": "λ\r\n"}}
        self.data = {"source": {"sha256": hashlib.sha256(source).hexdigest()}, "source_records": rules,
                     "semantic_model": {"relationship_types": {"motivates": definition}, "relationships": [edge],
                                        "facets": {"meaning": "Keep exact context."}, "entry_reviews": {}}}
        self.ledger.write_text(json.dumps(self.data))

    def invoke(self, public=False, **changes):
        request = {"action": "trace", "ledger": str(self.ledger),
                   "ledger_sha256": hashlib.sha256(self.ledger.read_bytes()).hexdigest(),
                   "selector": "source:read", "direction": "out", "relation_type": "motivates", "depth": 1}
        request.update(changes)
        self.request.write_text(json.dumps(request))
        command = (["mise", "run", "--force", "--task-cache", "off", "ledger", "--", str(self.request)]
                   if public else ["node", str(ROOT / "scripts/run_review_ledger.ts"), str(self.request)])
        return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)

    def result(self, process):
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        output = json.loads(process.stdout)
        self.assertEqual(output["status"], "success")
        self.assertTrue(all(step["status"] == "success" for step in output["steps"].values()))
        return output["result"]

    def test_real_workflow_preserves_whole_body_and_conditional_hyperedge(self):
        result = self.result(self.invoke())
        self.assertEqual(result["body"]["text"].encode(), (ROOT / "SKILL.md").read_bytes())
        self.assertEqual(result["body"]["sha256"], hashlib.sha256((ROOT / "SKILL.md").read_bytes()).hexdigest())
        view = json.loads(result["view_text"])
        self.assertEqual(view["edges"], self.data["semantic_model"]["relationships"])
        self.assertEqual(view["nodes"], ["source:read", "source:write"])
        self.assertEqual(result["execution_acceptance"], "pending")
        self.assertEqual(result["coverage"], "asserted relationships and direct records only")

    def test_public_entry_emits_one_json_result(self):
        self.result(self.invoke(public=True))

    def test_direction_and_zero_depth_keep_their_actual_boundaries(self):
        self.assertEqual(json.loads(self.result(self.invoke(depth=0))["view_text"])["edges"], [])
        self.assertEqual(json.loads(self.result(self.invoke(direction="in"))["view_text"])["edges"], [])
        incoming = json.loads(self.result(self.invoke(selector="source:write", direction="in"))["view_text"])
        self.assertEqual(incoming["nodes"], ["source:read", "source:review", "source:write"])

    def test_stale_input_fails_before_view_and_valid_input_recovers(self):
        raw = self.ledger.read_bytes()
        failure = self.invoke(ledger_sha256="0" * 64)
        self.assertEqual(failure.returncode, 1, failure.stdout + failure.stderr)
        report = json.loads(failure.stdout)
        self.assertNotEqual(report["steps"].get("build-asserted-relationship-view", {}).get("status"), "success")
        self.assertEqual(self.ledger.read_bytes(), raw)
        self.result(self.invoke())

    def test_duplicate_nonfinite_missing_subject_and_unknown_type_reject(self):
        raw = self.ledger.read_bytes()
        for invalid in [b'{"source":{},"source":{}}', b'{"value":NaN}']:
            self.ledger.write_bytes(invalid)
            self.assertEqual(self.invoke().returncode, 1)
        self.ledger.write_bytes(raw)
        for change in [{"selector": "source:absent"}, {"relation_type": "absent"}, {"depth": -1}]:
            self.assertEqual(self.invoke(**change).returncode, 1)
        self.result(self.invoke())


if __name__ == "__main__":
    unittest.main()
