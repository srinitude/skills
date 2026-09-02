"""Build current passing proof records for runtime behavior tests."""


def quality_evidence():
    ids = [
        "truth", "access", "task", "perception", "familiarity",
        "standards", "uniqueness", "craft", "resilience",
    ]
    return {
        "token": {"status": "pass", "freshness": "current",
                  "scope": "token_and_proof_only", "evidence": ["token:proof"]},
        "design": {"status": "pass", "diagnosis": "PASS",
                   "freshness": "current", "checkpoint": "integrated",
                   "vision_owner": "same invoking strong vision-capable executor",
                   "whole_view_evidence": ["vision:whole"],
                   "detail_evidence": ["vision:detail"],
                   "responsive_evidence": ["vision:responsive"],
                   "input_path_evidence": ["vision:input"],
                   "gates": [{"id": item, "status": "pass",
                              "evidence": [f"vision:{item}"]} for item in ids]},
    }


def property_proof(kinds):
    return [{
        "component_id": "component-1", "figma_node": "1:2",
        "code_export": "Component", "properties": [{
            "name": kind.lower(), "kind": kind, "disposition": "mapped",
            "justification": "The product contract needs this control.",
            "figma_evidence": "figma:1:2", "code_evidence": "src/component.tsx",
            "mapping_evidence": "src/component.figma.ts", "status": "pass",
            "comparison_id": "item-2", "figma_property": kind.lower(),
            "react_prop": kind.lower(), "api_evidence": ["typecheck:pass"],
            "render_evidence": [f"render:{kind.lower()}"],
        } for kind in kinds],
    }]


def governance_proof():
    return [{
        "scope": scope, "path": f"src/{scope}/AGENTS.md",
        "parent_path": "AGENTS.md", "parent_required": True,
        "design_system_source_of_truth": True,
        "generated_owner": "generator" if scope == "generator" else "direct",
        "status": "pass",
    } for scope in ["component", "mapping", "generator"]]


def figma_audit_proof(rules):
    gate = rules["figma_app_pass_gate"]
    items = []
    for kind in gate["required_item_kinds"]:
        item_id = "page-1" if kind == "page" else f"{kind}-1"
        ancestry = ["page-1"] if kind == "page" else ["page-1", item_id]
        items.append({"id": item_id, "kind": kind, "decision": "pass",
            "freshness": "current", "vision_evidence": [f"vision:{item_id}"],
            "source_receipts": gate["required_sources"],
            "canonical_page_id": "page-1", "actual_page_id": "page-1",
            "ancestry": ancestry, "readback": f"figma:{item_id}"})
    return {"in_scope": True, "passes": [{"id": "pass-1", "status": "pass",
        "freshness": "current", "skills": gate["required_skills"],
        "skills_fresh_before_first_decision": True,
        "source_receipts": gate["required_sources"],
        "item_kinds": gate["required_item_kinds"], "items": items,
        "computer_control_capability": gate["computer_control_capability"],
        "vision_owner": gate["vision_owner"], "item_count": len(items),
        "inventory_digest": "sha256:current-inventory",
        "whole_canvas_before": ["vision:canvas-before"],
        "whole_canvas_after": ["vision:canvas-after"],
        "active_area_before": ["vision:area-before"],
        "active_area_after": ["vision:area-after"],
        "cleanliness_receipt": ["vision:clean"]}]}


def render_context_proof():
    inventory = [{"id": "checkout-empty-desktop", "screen": "checkout",
        "product_state": "empty", "form_factor": "desktop",
        "viewport": "1440x900", "orientation": "not_applicable",
        "input_path": "keyboard"}]
    proof = [{"id": "checkout-empty-desktop", "status": "pass",
        "figma_evidence": "figma:screen", "code_evidence": "src/screen.tsx",
        "mapping_evidence": "src/screen.figma.ts",
        "vision_evidence": ["vision:screen"]}]
    return inventory, proof


def comparison_proof():
    levels = [
        "dtcg-tokens", "atoms", "molecules", "organisms",
        "design-composition-templates", "screens", "flows",
    ]
    items = [{"id": f"item-{index}", "level": level}
             for index, level in enumerate(levels, 1)]
    entries = [comparison_entry(item, index, items) for index, item in enumerate(items)]
    return items, {"classification": "controlled_visual_comparison",
                   "not_live_user_ab_test": True, "entries": entries}


def comparison_entry(item, index, items):
    return {
        **item, "experiment_id": f"experiment:{item['id']}",
        "exploration_source_ids": [f"candidate:{item['id']}"],
        "changed_factor": "owned-role", "one_factor_only": True,
        "change_scale": "material_direction",
        "material_effect": "Changes hierarchy, task effort, meaning, or behavior at whole-view scale.",
        "micro_optimization": False,
        "threshold_exception": None,
        "fixed_conditions": ["specimen", "content", "state", "viewport",
                             "input_path", "all_non_tested_tokens"],
        "a_evidence": f"figma:{item['id']}:a",
        "b_evidence": f"figma:{item['id']}:b",
        "vision": {"status": "pass", "freshness": "current",
                   "evidence": [f"vision:{item['id']}"]},
        "status": "pass", "experiment_status": "run",
        "decision_lock": {
            "status": "accepted_locked",
            "canonical_creation_after_experiment": True,
            "decision_owner": "direct_current_vision",
            "lower_owner_locks": [] if index == 0 else [items[index - 1]["id"]],
        },
    }
