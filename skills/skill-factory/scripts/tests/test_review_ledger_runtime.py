"""Actual native ledger workflow cases; no model or domain acceptance claim."""
import hashlib, json, subprocess, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def _TestLedgerRuntime_setUp(self):
    self.temporary = tempfile.TemporaryDirectory()
    self.addCleanup(self.temporary.cleanup)
    self.folder = Path(self.temporary.name)
    self.ledger, self.request = self.folder / "ledger.json", self.folder / "request.json"
    rules = [{'id': name, 'text': text} for name, text in [('read', 'Read current evidence.'), ('write', 'Preserve authorized bytes.'), ('review', 'Review the actual change.')]]
    source = "\n".join(row["text"] for row in rules).encode()
    definition = {'family': 'meaning', 'meaning': 'Provides a stated motive.', 'transitivity': 'not implied', 'review_state': 'reviewed'}
    edge = {"id": "reason", "type": "motivates", "from": ["source:read", "source:review"],
            "to": "source:write", "condition": "Only within the authorized change.",
            "meaning": "The two source duties jointly motivate preserving the reviewed change.",
            "basis": ["source:read", "source:write", "source:review"], "review_state": "candidate",
            "roles": ["evidence", "judgment"], "extension": {"preserve": "λ\r\n"}}
    self.data = {"source": {"sha256": hashlib.sha256(source).hexdigest()}, "source_records": rules,
                 "semantic_model": {"relationship_types": {"motivates": definition}, "relationships": [edge],
                                    "facets": {"meaning": "Keep exact context."}, "entry_reviews": {}}}
    self.ledger.write_text(json.dumps(self.data))

def _TestLedgerRuntime_invoke(self, public=False, refresh=False, **changes):
    if refresh: self.ledger.write_text(json.dumps(self.data))
    action = changes.get("action", "trace")
    request = {'action': action, 'ledger': str(self.ledger), 'ledger_sha256': hashlib.sha256(self.ledger.read_bytes()).hexdigest()}
    if action in {"show", "relations", "trace"}: request["selector"] = "source:read"
    if action in {"relations", "trace"}: request.update(direction="out", relation_type="motivates")
    if action == "trace": request["depth"] = 1
    request.update(changes)
    self.request.write_text(json.dumps(request))
    command = (["mise", "run", "--force", "--task-cache", "off", "ledger", "--", str(self.request)]
               if public else ["node", str(ROOT / "scripts/run_review_ledger.ts"), str(self.request)])
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)

def _TestLedgerRuntime_result(self, process):
    self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
    output = json.loads(process.stdout)
    self.assertEqual([output["status"], *[step["status"] for step in output["steps"].values()]], ["success"] * (1 + len(output["steps"])))
    return output["result"]

def _TestLedgerRuntime_captured_source(self):
    text = "\n".join(row["text"] for row in self.data["source_records"])
    raw, start = text.encode(), 0
    source = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "lines": 3}
    self.data.update(source=source, packet_documents=[{"name": "rules.txt", "text": text, **source}])
    for number, (row, line) in enumerate(zip(self.data["source_records"], raw.splitlines(keepends=True)), 1):
        row.update(source_sha256=source['sha256'], quote=line.decode(), byte_start=start, byte_end_exclusive=start + len(line), line_start=number, line_end=number)
        start += len(line)
    self.ledger.write_text(json.dumps(self.data))

def _TestLedgerRuntime_test_real_workflow_preserves_whole_body_and_conditional_hyperedge(self):
    result = self.result(self.invoke())
    self.assertEqual(result["body"]["text"].encode(), (ROOT / "SKILL.md").read_bytes())
    self.assertEqual(result["body"]["sha256"], hashlib.sha256((ROOT / "SKILL.md").read_bytes()).hexdigest())
    view = json.loads(result["view_text"])
    self.assertEqual((view["edges"], view["nodes"]), (self.data["semantic_model"]["relationships"], ["source:read", "source:write"]))
    self.assertEqual((result["execution_acceptance"], result["coverage"]), ("pending", "recorded context, relationships and source checks only"))

def _TestLedgerRuntime_test_public_entry_emits_one_json_result(self):
    self.result(self.invoke(public=True))

def _TestLedgerRuntime_test_direction_and_zero_depth_keep_their_actual_boundaries(self):
    self.assertEqual(json.loads(self.result(self.invoke(depth=0))["view_text"])["edges"], [])
    self.assertEqual(json.loads(self.result(self.invoke(direction="in"))["view_text"])["edges"], [])
    incoming = json.loads(self.result(self.invoke(selector="source:write", direction="in"))["view_text"])
    self.assertEqual(incoming["nodes"], ["source:read", "source:review", "source:write"])

def _TestLedgerRuntime_test_stale_input_fails_before_view_and_valid_input_recovers(self):
    raw = self.ledger.read_bytes()
    failure = self.invoke(ledger_sha256="0" * 64)
    self.assertEqual(failure.returncode, 1, failure.stdout + failure.stderr)
    report = json.loads(failure.stdout)
    self.assertNotEqual(report["steps"].get("build-asserted-relationship-view", {}).get("status"), "success")
    self.assertEqual(self.ledger.read_bytes(), raw)
    self.result(self.invoke())

def _TestLedgerRuntime_test_duplicate_nonfinite_missing_subject_and_unknown_type_reject(self):
    raw = self.ledger.read_bytes()
    for invalid in [b'{"source":{},"source":{}}', b'{"value":NaN}']:
        self.ledger.write_bytes(invalid)
        self.assertEqual(self.invoke().returncode, 1)
    self.ledger.write_bytes(raw)
    for change in [{"selector": "source:absent"}, {"relation_type": "absent"}, {"depth": -1}]:
        self.assertEqual(self.invoke(**change).returncode, 1)
    self.result(self.invoke())

def _TestLedgerRuntime_test_detail_keeps_inherited_meaning_parent_context_and_original_edges(self):
    self.data["source_records"][0]["clauses"] = [{"id": "read-part", "quote": "current evidence"}]
    self.data["semantic_model"]["entry_reviews"] = { "source:review": {"inherits": [], "facets": {"meaning": "Review actual evidence."}, "state": "partial"},
        "source:read": {"inherits": ["source:review"], "facets": {}, "state": "pending"}}
    view = json.loads(self.result(self.invoke(refresh=True, action="show", selector="clause:read-part"))["view_text"])
    self.assertEqual(view["entry"], self.data["source_records"][0]["clauses"][0])
    self.assertEqual(view["context"]["effective_facets"], {"meaning": "Review actual evidence."})
    self.assertEqual(view["context"]["subjects"], ["source:review", "source:read", "clause:read-part"])
    self.assertEqual(view["context"]["relationships"], self.data["semantic_model"]["relationships"])
    self.assertEqual(view["context"]["reviews"]["source:read"]["state"], "pending")

def _TestLedgerRuntime_test_inheritance_conflicts_and_cycles_reject_before_valid_recovery(self):
    reviews = {"source:review": {"facets": {"meaning": "Review."}}, "source:write": {"facets": {"meaning": "Preserve."}},
               "source:read": {"inherits": ["source:review", "source:write"], "facets": {}}}
    self.data["semantic_model"]["entry_reviews"] = reviews
    self.assertEqual(self.invoke(refresh=True, action="show").returncode, 1)
    reviews["source:read"]["facets"]["meaning"] = "Review the preservation decision."
    view = json.loads(self.result(self.invoke(refresh=True, action="show"))["view_text"])
    self.assertEqual(view["context"]["effective_facets"], reviews["source:read"]["facets"])
    reviews["source:review"]["inherits"] = ["source:read"]
    self.assertEqual(self.invoke(refresh=True, action="show").returncode, 1)
    del reviews["source:review"]["inherits"]
    self.result(self.invoke(refresh=True, action="show"))

def _TestLedgerRuntime_test_file_detail_keeps_history_and_does_not_relabel_it_current(self):
    baseline = {"path": "removed.py", "sha256": "1" * 64, "note": "Original owner."}
    historic = {"sha256": "2" * 64, "note": "Earlier observation."}
    self.data["functional_file_map"] = [baseline]
    self.data["semantic_model"]["review_changes"] = [{"previous": {"package_snapshot": {"files": {"removed.py": historic}}}}]
    self.data["package_snapshot"] = {"files": {"current.py": {"sha256": "3" * 64}}}
    entry = json.loads(self.result(self.invoke(refresh=True, action="show", selector="file:removed.py"))["view_text"])["entry"]
    self.assertEqual((entry["recorded_package_state"], entry["baseline"]), ("missing", baseline))
    self.assertIsNone(entry["current"])
    self.assertEqual(entry["history"], [{"review_change": 0, "record": historic}])
    self.data["functional_file_map"].append(dict(baseline))
    self.assertEqual(self.invoke(refresh=True, action="show", selector="file:removed.py").returncode, 1)
    self.data["functional_file_map"].pop()
    self.result(self.invoke(refresh=True, action="show", selector="file:removed.py"))

def _TestLedgerRuntime_test_source_context_orders_group_prerequisites_before_consumers(self):
    self.data["source_records"][0]["owner_group"] = "consumer"
    self.data['source_owner_groups'] = [{'id': 'consumer', 'reading_prerequisites': ['provider']}, {'id': 'provider', 'reading_prerequisites': []}]
    view = json.loads(self.result(self.invoke(refresh=True, action="show"))["view_text"])
    order = view["context"]["subjects"]
    self.assertIn("group:provider", order)
    self.assertLess(order.index("group:provider"), order.index("group:consumer"))
    self.assertLess(order.index("group:consumer"), order.index("source:read"))

def _TestLedgerRuntime_test_capture_check_rejects_changed_source_text_and_recovers(self):
    self.captured_source()
    view = json.loads(self.result(self.invoke(action="check-capture"))["view_text"])
    self.assertEqual((view["documents"], view["source_records"]), (1, 3))
    self.assertEqual(view["scope"], "captured bytes and locators only")
    valid = self.ledger.read_bytes()
    self.data["source_records"][0]["quote"] += "Changed"
    self.ledger.write_text(json.dumps(self.data))
    invalid = self.ledger.read_bytes()
    self.assertEqual(self.invoke(action="check-capture").returncode, 1)
    self.assertEqual(self.ledger.read_bytes(), invalid)
    self.ledger.write_bytes(valid)
    self.result(self.invoke(action="check-capture"))

def _TestLedgerRuntime_live_source_bindings(self):
    self.captured_source()
    source = self.data["source"]
    inventory = {'source_sha256': source['sha256'], 'source_bytes': source['bytes'], 'source_lines': source['lines'], 'records': self.data['source_records']}
    text = json.dumps(inventory)
    self.data['packet_documents'].append({'name': 'coverage.json', 'text': text, 'sha256': hashlib.sha256(text.encode()).hexdigest(), 'bytes': len(text.encode()), 'lines': 1})
    expected = []
    for document in self.data["packet_documents"]:
        path = self.folder / document["name"]
        path.write_bytes(document["text"].encode())
        expected.append({"name": document["name"], "path": str(path), "sha256": document["sha256"]})
    original = self.folder / "original.txt"
    original.write_bytes(self.data["packet_documents"][0]["text"].encode())
    self.ledger.write_text(json.dumps(self.data))
    return {'expected_documents': expected, 'inventory_document': 'coverage.json', 'original_source': {'path': str(original), 'sha256': source['sha256']}}

def _TestLedgerRuntime_test_live_source_binding_blocks_inventory_rewrite_and_recovers(self):
    bindings = self.live_source_bindings()
    view = json.loads(self.result(self.invoke(action="check-sources", **bindings))["view_text"])
    self.assertEqual(view["scope"], "supplied live bindings and frozen source inventory only")
    self.assertEqual((self.invoke(action="check-sources").returncode, self.invoke(action="check-capture", **bindings).returncode), (1, 1))
    valid = self.ledger.read_bytes()
    self.data["source_records"][0]["id"] = "different"
    self.ledger.write_text(json.dumps(self.data))
    bad = self.ledger.read_bytes()
    self.assertEqual(self.invoke(action="check-sources", **bindings).returncode, 1)
    self.assertEqual(self.ledger.read_bytes(), bad)
    self.ledger.write_bytes(valid)
    self.result(self.invoke(action="check-sources", **bindings))

class TestLedgerRuntime(unittest.TestCase):
    setUp = _TestLedgerRuntime_setUp
    invoke = _TestLedgerRuntime_invoke
    result = _TestLedgerRuntime_result
    test_real_workflow_preserves_whole_body_and_conditional_hyperedge = _TestLedgerRuntime_test_real_workflow_preserves_whole_body_and_conditional_hyperedge
    test_public_entry_emits_one_json_result = _TestLedgerRuntime_test_public_entry_emits_one_json_result
    test_direction_and_zero_depth_keep_their_actual_boundaries = _TestLedgerRuntime_test_direction_and_zero_depth_keep_their_actual_boundaries
    test_stale_input_fails_before_view_and_valid_input_recovers = _TestLedgerRuntime_test_stale_input_fails_before_view_and_valid_input_recovers
    test_duplicate_nonfinite_missing_subject_and_unknown_type_reject = _TestLedgerRuntime_test_duplicate_nonfinite_missing_subject_and_unknown_type_reject
    test_detail_keeps_inherited_meaning_parent_context_and_original_edges = _TestLedgerRuntime_test_detail_keeps_inherited_meaning_parent_context_and_original_edges
    test_inheritance_conflicts_and_cycles_reject_before_valid_recovery = _TestLedgerRuntime_test_inheritance_conflicts_and_cycles_reject_before_valid_recovery
    test_file_detail_keeps_history_and_does_not_relabel_it_current = _TestLedgerRuntime_test_file_detail_keeps_history_and_does_not_relabel_it_current
    test_source_context_orders_group_prerequisites_before_consumers = _TestLedgerRuntime_test_source_context_orders_group_prerequisites_before_consumers
    captured_source = _TestLedgerRuntime_captured_source
    test_capture_check_rejects_changed_source_text_and_recovers = _TestLedgerRuntime_test_capture_check_rejects_changed_source_text_and_recovers
    live_source_bindings = _TestLedgerRuntime_live_source_bindings
    test_live_source_binding_blocks_inventory_rewrite_and_recovers = _TestLedgerRuntime_test_live_source_binding_blocks_inventory_rewrite_and_recovers

if __name__ == "__main__": unittest.main()
