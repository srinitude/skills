import copy
import json
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.integrated_validation import check_figma_app_audit, check_property_parity
from validate_run import validate


FIXED = [
    "specimen", "content", "state", "viewport", "input_path",
    "all_non_tested_tokens",
]
LEVELS = [
    "dtcg-tokens", "atoms", "molecules", "organisms",
    "design-composition-templates", "screens", "flows",
]


def contract():
    return json.loads((ROOT / "assets" / "run-contract.json").read_text())


def decision_lock(index, items):
    lower = [] if index == 0 else [items[index - 1]["id"]]
    return {
        "status": "accepted_locked",
        "canonical_creation_after_experiment": True,
        "decision_owner": "direct_current_vision",
        "lower_owner_locks": lower,
    }


def comparison_entries(items):
    entries = []
    for index, item in enumerate(items):
        entry = {
        **item,
        "experiment_id": f"experiment:{item['id']}",
        "exploration_source_ids": [f"candidate:{item['id']}"],
        "changed_factor": "owned-role",
        "one_factor_only": True,
        "change_scale": "material_direction",
        "material_effect": "Changes hierarchy, task effort, meaning, or behavior at whole-view scale.",
        "micro_optimization": False,
        "threshold_exception": None,
        "fixed_conditions": FIXED,
        "a_evidence": f"figma:{item['id']}:a",
        "b_evidence": f"figma:{item['id']}:b",
        "vision": {
            "status": "pass", "freshness": "current",
            "evidence": [f"vision:{item['id']}"],
        },
        "status": "pass",
        "experiment_status": "run",
        "decision_lock": decision_lock(index, items),
        }
        entries.append(entry)
    return entries


def valid_record():
    rules = contract()
    items = [{"id": f"item-{index}", "level": level}
             for index, level in enumerate(LEVELS, 1)]
    return {
        "mode": "create", "hierarchy": rules["hierarchy"],
        "template_kinds": rules["template_kinds"],
        "sources": [{"type": "figma_file", "location": "figma:file"}],
        "stages": [{"id": name, "status": "planned"}
                   for name in rules["stage_order"]],
        "capabilities": [], "mutations": [], "lineage": [],
        "comparison_inventory": items, "controlled_comparisons": {
            "classification": "controlled_visual_comparison",
            "not_live_user_ab_test": True,
            "entries": comparison_entries(items),
        },
        "completion": "planned",
    }


class ComparisonCoverageTests(unittest.TestCase):
    def test_complete_current_inventory_passes(self):
        self.assertEqual(validate(valid_record(), contract()), [])

    def test_missing_item_pair_blocks_the_run(self):
        record = valid_record()
        record["controlled_comparisons"]["entries"].pop()
        self.assertIn(
            "controlled comparison inventory coverage mismatch",
            validate(record, contract()),
        )

    def test_stale_pair_blocks_the_run(self):
        record = copy.deepcopy(valid_record())
        record["controlled_comparisons"]["entries"][0]["vision"]["freshness"] = "stale"
        errors = validate(record, contract())
        self.assertTrue(any("current vision" in item for item in errors))

    def test_missing_experiment_link_blocks_the_run(self):
        record = valid_record()
        record["controlled_comparisons"]["entries"][0].pop("experiment_id")
        errors = validate(record, contract())
        self.assertTrue(any("experiment link" in item for item in errors))

    def test_micro_optimization_without_threshold_evidence_blocks_the_run(self):
        record = valid_record()
        item = record["controlled_comparisons"]["entries"][0]
        item["change_scale"] = "micro_optimization"
        item["micro_optimization"] = True
        errors = validate(record, contract())
        self.assertTrue(any("material change" in error for error in errors))

    def test_unrun_experiment_or_missing_layer_lock_blocks_acceptance(self):
        record = valid_record()
        record["controlled_comparisons"]["entries"][0]["experiment_status"] = "registered"
        errors = validate(record, contract())
        self.assertTrue(any("run before canonical creation" in item for item in errors))
        record = valid_record()
        record["controlled_comparisons"]["entries"][1].pop("decision_lock")
        errors = validate(record, contract())
        self.assertTrue(any("accepted layer lock" in item for item in errors))

    def test_component_properties_need_every_kind_and_a_pair_link(self):
        kinds = contract()["component_property_kinds"]
        record = {"controlled_comparisons": {"entries": [{"id": "atom-1"}]},
                  "property_parity": [{
                      "component_id": "button", "figma_node": "1:2",
                      "code_export": "Button", "properties": [{
                          "name": kind, "kind": kind, "status": "pass",
                          "disposition": "not_applicable", "justification": "Not needed.",
                          "figma_evidence": "figma:1:2",
                      } for kind in kinds[:-1]],
                  }]}
        problems = []
        check_property_parity(record, contract(), problems)
        self.assertTrue(any("canonical kind" in item for item in problems))
        self.assertTrue(any("comparison link" in item for item in problems))

    def test_figma_app_pass_needs_four_skills_and_all_source_receipts(self):
        record = {"figma_app_audit": {"in_scope": True, "passes": [{
            "id": "pass-1", "skills": ["computer-use"],
            "skills_fresh_before_first_decision": False,
            "source_receipts": ["current direct vision"],
            "item_kinds": ["page"], "items": [{"id": "page-1"}],
        }]}}
        problems = []
        check_figma_app_audit(record, contract(), problems)
        self.assertTrue(any("four-skill" in item for item in problems))
        self.assertTrue(any("source receipt" in item for item in problems))
        self.assertTrue(any("item kinds" in item for item in problems))


if __name__ == "__main__":
    unittest.main()
