"""Hostile mutations that must not receive a Figma skill PASS."""
import copy
import datetime
import pathlib
import sys
import unittest
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.factory_checks import decisions, load, research, use_case
from lib.factory_graph import graph
from new_run import make_record
from runtime_test_support import (
    comparison_proof, figma_audit_proof, governance_proof, property_proof,
    quality_evidence, render_context_proof,
)
from validate_run import validate


def complete_record():
    rules = load_contract()
    args = SimpleNamespace(run_id="run-1", mode="create", platform="web",
                           ui_scope="checkout")
    source = [{"id": "source-1", "type": "prd", "location": "/tmp/prd.md"}]
    record = make_record(args, rules, source)
    record["completion"] = "pass"
    record["capabilities"] = [{"role": "figma.visual.read", "disposition": "use"}]
    for stage in record["stages"]:
        stage.update(status="pass", proof=[f"proof:{stage['id']}"])
    record["lineage"] = [{"id": "component-1", "level": "atoms",
                          "status": "pass", "depends_on": [],
                          "proof": ["current lineage"]}]
    record["requirements"] = [{"id": "REQ-1", "request": "Map checkout",
        "owner": "component", "disposition": "use", "status": "pass",
        "evidence": ["current requirement"], "invalidated_by": []}]
    record["quality_evidence"] = quality_evidence()
    kinds = rules["component_property_kinds"]
    record["property_kind_dispositions"] = [{"kind": kind, "disposition": "use",
        "reason": "The contract needs it.", "evidence": ["current inventory"]}
        for kind in kinds]
    record["property_parity"] = property_proof(kinds)
    record["governance"] = governance_proof()
    record["comparison_inventory"], record["controlled_comparisons"] = comparison_proof()
    record["figma_app_audit"] = figma_audit_proof(rules)
    contexts = render_context_proof()
    record["render_context_inventory"], record["render_context_proof"] = contexts
    return record


def load_contract():
    return __import__("json").loads((ROOT / "assets/run-contract.json").read_text())


class AdversarialRunTests(unittest.TestCase):
    def test_completion_rejects_empty_or_pending_capability_proof(self):
        record = complete_record()
        record["capabilities"] = [{"role": "figma.visual.read",
                                   "disposition": "pending"}]
        self.assertTrue(any("capability proof" in item
                            for item in validate(record, load_contract())))

    def test_completion_requires_current_figma_application_audit(self):
        record = complete_record()
        record.pop("figma_app_audit")
        self.assertTrue(any("Figma app audit" in item
                            for item in validate(record, load_contract())))

    def test_claimed_item_kinds_cannot_hide_wrong_page_or_kind(self):
        record = complete_record()
        item = record["figma_app_audit"]["passes"][0]["items"][1]
        item["kind"] = "unknown"
        item["actual_page_id"] = "wrong-page"
        problems = validate(record, load_contract())
        self.assertTrue(any("item coverage" in item for item in problems))
        self.assertTrue(any("canonical page" in item for item in problems))

    def test_passed_stages_and_lineage_need_current_proof(self):
        record = complete_record()
        record["stages"][0]["proof"] = []
        record["lineage"][0]["proof"] = []
        problems = validate(record, load_contract())
        self.assertTrue(any("stage proof" in item for item in problems))
        self.assertTrue(any("lineage proof" in item for item in problems))

    def test_not_applicable_stage_needs_reason_and_evidence(self):
        record = complete_record()
        record["stages"][2] = {"id": "model-product", "status": "not_applicable"}
        self.assertTrue(any("not-applicable proof" in item
                            for item in validate(record, load_contract())))

    def test_lineage_cannot_depend_on_same_or_higher_layer(self):
        record = complete_record()
        record["lineage"] = [
            {"id": "atom", "level": "atoms", "status": "pass",
             "depends_on": ["screen"], "proof": ["current"]},
            {"id": "screen", "level": "screens", "status": "pass",
             "depends_on": [], "proof": ["current"]},
        ]
        self.assertTrue(any("lower layer" in item
                            for item in validate(record, load_contract())))

    def test_mapped_property_requires_typescript_and_parserless_mapping(self):
        record = complete_record()
        prop = record["property_parity"][0]["properties"][0]
        prop["code_evidence"] = "src/component.js"
        prop["mapping_evidence"] = "src/component.figma.tsx"
        problems = validate(record, load_contract())
        self.assertTrue(any("TypeScript evidence" in item for item in problems))
        self.assertTrue(any("parserless .figma.ts" in item for item in problems))

    def test_mapped_property_requires_api_and_render_receipts(self):
        record = complete_record()
        prop = record["property_parity"][0]["properties"][0]
        prop["react_prop"] = ""
        prop["render_evidence"] = []
        problems = validate(record, load_contract())
        self.assertTrue(any("API and render evidence" in item for item in problems))

    def test_quality_gates_need_direct_visual_evidence(self):
        record = complete_record()
        record["quality_evidence"]["design"]["gates"][0]["evidence"] = []
        record["quality_evidence"]["design"]["whole_view_evidence"] = []
        problems = validate(record, load_contract())
        self.assertTrue(any("gate evidence" in item for item in problems))
        self.assertTrue(any("visual contexts" in item for item in problems))

    def test_figma_audit_needs_inventory_and_cleanliness_readback(self):
        record = complete_record()
        audit = record["figma_app_audit"]["passes"][0]
        audit["item_count"] = 999
        audit["whole_canvas_after"] = []
        problems = validate(record, load_contract())
        self.assertTrue(any("inventory count" in item for item in problems))
        self.assertTrue(any("cleanliness evidence" in item for item in problems))

    def test_mobile_contexts_need_both_orientations(self):
        record = complete_record()
        inventory = record["render_context_inventory"]
        inventory[0].update(form_factor="mobile", orientation="portrait")
        self.assertTrue(any("portrait and landscape" in item
                            for item in validate(record, load_contract())))

    def test_executed_mutation_needs_target_and_matching_permission(self):
        record = complete_record()
        record["mutations"] = [{"effect": "repository_write", "status": "executed",
            "authorization_id": "AUTH-1", "readback": "current"}]
        problems = validate(record, load_contract())
        self.assertTrue(any("target is required" in item for item in problems))
        self.assertTrue(any("matching permission" in item for item in problems))

    def test_requirement_and_governance_owners_cannot_be_blank_or_reused(self):
        record = complete_record()
        record["requirements"][0]["request"] = ""
        record["governance"][1]["path"] = record["governance"][0]["path"]
        problems = validate(record, load_contract())
        self.assertTrue(any("request and owner" in item for item in problems))
        self.assertTrue(any("unique owner paths" in item for item in problems))

    def test_screen_stage_needs_exact_render_context_coverage(self):
        record = complete_record()
        record["render_context_proof"] = []
        self.assertTrue(any("render context coverage" in item
                            for item in validate(record, load_contract())))


class AdversarialFactoryTests(unittest.TestCase):
    def test_future_research_receipt_is_not_current(self):
        data = copy.deepcopy(load(ROOT)[0])
        future = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
        data["research_receipts"][0]["checked_at"] = future.isoformat()
        self.assertTrue(any("future" in item for item in research(data)))

    def test_unknown_task_link_is_reported_without_crashing(self):
        values = list(load(ROOT))
        tasks = copy.deepcopy(values[-1])
        tasks["ci"]["depends"].append("missing-task")
        values[-1] = tasks
        self.assertTrue(any("unknown link" in item for item in graph(*values)))

    def test_primitive_policy_cannot_copy_another_owner(self):
        data = copy.deepcopy(load(ROOT)[0])
        data["primitive_roles"]["references"] = copy.deepcopy(
            data["primitive_roles"]["assets"])
        self.assertTrue(any("primitive.references" in item for item in use_case(data)))

    def test_choice_records_cannot_repeat_generic_claims(self):
        values = list(load(ROOT))
        records = copy.deepcopy(values[2])
        records["records"][1]["outcome"] = records["records"][0]["outcome"]
        values[2] = records
        self.assertTrue(any("repeat" in item for item in decisions(*values)))


if __name__ == "__main__":
    unittest.main()
