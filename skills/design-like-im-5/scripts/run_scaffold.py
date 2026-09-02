#!/usr/bin/env python3
"""Build stable run scaffolds and model packet contracts."""
import argparse
import json

from review_checklist import REVIEW_INDEX

REVIEW_ACTIONS = {"state_judgment", "visual_review"}
CREATIVE_ACTIONS = {"state_judgment", "atom_judgment", "part_design",
                    "screen_design", "motion_judgment"}
JUDGMENT_CONTEXT = [
    {"path": "run.json", "use": "Use the frozen goal, people, tasks, rights, proof, and rules."},
    {"path": "source-queue.json", "use": "Use source facts, locations, gaps, and rights."},
    {"path": "retrieval-manifest.json", "use": "Use current source bytes and dates."},
    {"path": "state-matrix.json", "use": "Use found states, context, causes, change, and unknowns."},
    {"path": "review-checklist.json", "use": "Use every eye, brain, touch, objective failure, bad design, bad output, and bad practice prompt."},
    {"path": "render-plan.json", "use": "Use each needed state, view, mode, and motion path."},
    {"path": "viewport-matrix.json", "use": "Use each needed size, crop, zoom, and space."},
    {"path": "dependency-manifest.json", "use": "Use proved low parts and affected high parts."},
    {"path": "rebuild-queue.json", "use": "Use stale links and work that must be rebuilt."},
]
EXPLORATION_CONTRACT = {
    "option_owner": "model", "choice_owner": "model",
    "script_role": "Require the option fields and veto checks. Never rank or choose.",
    "minimum_options": 4, "maximum_options": None,
    "may_add_directions": True, "may_combine_directions": True,
    "may_split_directions": True, "constraints_are_vetoes": True,
    "required_directions": ["known pattern", "product-shaped form",
                            "true reverse", "experimental edge"],
    "exploration_axes": ["state model", "task structure", "sequence",
                         "disclosure", "content", "interaction", "visual form",
                         "motion", "sound", "touch and haptics", "access path",
                         "platform fit", "service and human effects"],
    "method": ["Make unlike options before one choice.",
               "A required direction is a starting point, not a box.",
               "Add, split, reverse, or combine directions when the product calls for it.",
               "Give each option a concrete scene, proof, tradeoff, veto check, and test.",
               "Keep a bold option alive until evidence or a veto rejects it.",
               "Choose with stated reasons. The script does not choose."],
    "required_option_fields": ["id", "direction", "scene", "hypothesis",
                               "product_fit", "evidence", "tradeoffs",
                               "veto_check", "test", "novelty"],
    "controlled_comparison": {
        "classification": "controlled_visual_comparison",
        "changed_factor_count": 1,
        "required_links": ["exploration_option_ids", "experiment.id",
                           "experiment.hypothesis", "experiment.null_hypothesis",
                           "experiment.measure", "experiment.falsifier",
                           "experiment.frozen_before_view"],
        "held_constant": ["specimen", "content", "state", "viewport",
                          "input_path", "all_non_tested_tokens"],
        "vision_owner": "model", "not_live_user_ab_test": True,
    },
}


def packet_schema(action):
    if action == "state_judgment":
        return "assets/state-record.schema.json"
    if action == "visual_review":
        return "assets/review-record.schema.json"
    return "assets/model-record.schema.json"


def required_evidence(action):
    needed = ["source", "location", "observation"]
    if action == "state_judgment":
        needed += ["context", "transition"]
    if action in REVIEW_ACTIONS:
        needed += ["eye", "brain", "touch", "human sweep",
                   "objective failure", "bad design", "bad output",
                   "bad practice"]
    return needed + ["reason"]


def exploration_fields(action):
    if action not in CREATIVE_ACTIONS:
        return {}
    return {"judgment_context": JUDGMENT_CONTEXT,
            "exploration_contract": EXPLORATION_CONTRACT}


def make_packet(action, run_id, data, rules, item_id=None):
    review = action in REVIEW_ACTIONS
    return {
        "version": "1.0.0", "run_id": run_id, "action": action,
        "item_id": item_id,
        "goal": ("Find and judge context-derived product states."
                 if action == "state_judgment" else
                 "Make one evidence-backed design judgment."),
        "inputs": data, "source_locations": [],
        "allowed_decisions": ["PASS", "REVISE", "BLOCKED"],
        "forbidden_claims": ["unseen pixels", "missing sources", "causal impact"],
        "required_evidence": required_evidence(action),
        "output_schema": packet_schema(action),
        **({"review_checklist": "review-checklist.json",
           "review_checklist_command": "python3 scripts/review_checklist.py",
           "human_sweep_command": "python3 scripts/human_capability_sweep.py",
           "review_owner": "model"} if review else {}),
        **exploration_fields(action),
        "required_rules": rules,
        "reason_codes": ["CLEAR", "NEEDS_PROOF", "VETO", "STALE",
                         "OBJECTIVE_FAILURE", "HARM_CHECK", "CHECK_MEANING"],
        "vetoes": ["safety", "access", "understanding", "agency"],
        "pass_rule": "PASS needs all fields and no open veto.",
    }


def scaffold_files(run_id, data):
    views = ["wide", "narrow", "whole", "close"]
    dimensions = ["user_goal", "task", "data", "system", "environment",
                  "device", "input", "access", "time", "risk", "content",
                  "social_setting", "prior_action"]
    prompts = ["no content", "work in progress", "partial result", "failure",
               "repair", "offline", "permission", "interruption", "success"]
    tools = ["files", "commands", "web", "browser", "render", "capture",
             "motion", "vision"]
    return {
        "capabilities.json": {"items": [{"id": x, "state": "UNKNOWN"} for x in tools]},
        "source-queue.json": {"items": [], "permissions": data["source_permissions"]},
        "retrieval-manifest.json": {"items": [], "content_hashes": []},
        "render-plan.json": {"items": [], "view_prompts": views, "prompts_are_exhaustive": False, "state_source": "state-matrix.json#items"},
        "viewport-matrix.json": {"view_prompts": views, "prompts_are_exhaustive": False, "items": []},
        "state-matrix.json": {"state_set": "OPEN_CONTEXT_DERIVED", "exhaustive": False, "items": [], "discovery_dimensions": dimensions, "coverage_prompts": prompts, "required_lenses": ["eye", "brain", "touch", "objective failure", "bad design", "bad output", "bad practice", "access", "agency"], "rule": "Add, split, merge, or retire items when evidence changes."},
        "review-checklist.json": REVIEW_INDEX,
        "dependency-manifest.json": {"dtcg_run": {"status": "BLOCKED"}, "parts": []},
        "dtcg-route.json": {"skill": "dtcg-tokens", "state": "NEEDS_DISCOVERY", "needs": ["tokens", "evidence", "proof", "visual review"]},
        "rebuild-queue.json": {"items": [], "reason_codes": ["STALE_DEP", "LAYER_SKIP"]},
        "run-log.json": {"events": [{"kind": "START", "run_id": run_id}]},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="example")
    parser.add_argument("--source-permission", action="append", default=[])
    args = parser.parse_args(argv)
    data = {"source_permissions": args.source_permission}
    print(json.dumps(scaffold_files(args.run_id, data), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
