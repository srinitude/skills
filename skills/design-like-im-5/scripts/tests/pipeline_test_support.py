"""Share run tools for small tests."""
import json
import pathlib
import subprocess
import sys

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = SKILL_DIR / "scripts" / "run_pipeline.py"
SELECT = SKILL_DIR / "scripts" / "select_rules.py"
LINEAGE = SKILL_DIR / "scripts" / "check_lineage.py"
CHECKLIST = SKILL_DIR / "scripts" / "review_checklist.py"
INTAKE = SKILL_DIR / "evals" / "files" / "valid-intake.json"


def run(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True, timeout=120)


def set_next(run_dir, action):
    path = pathlib.Path(run_dir) / "run.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["next"] = action
    path.write_text(json.dumps(data), encoding="utf-8")


def review_groups(checklist, key):
    return {group: [{
        "id": item["id"], "scene": "A named test scene.",
        "observation": "The test has the named proof.",
        "evidence": ["fixture:runner-only"], "decision": "PASS",
        "reason": "This answer tests record fields only.",
        "alternatives": ["Get live product proof."],
        "uncertainty": "This says no product is good.",
    } for item in items] for group, items in checklist[key].items()}


def exploration_fields():
    directions = ["known", "product-shaped", "reverse", "experimental"]
    options = [{
        "id": f"option-{index}", "direction": direction,
        "scene": "A named test scene.",
        "hypothesis": "This path tests run fields.",
        "product_fit": "This test does not grade product fit.",
        "evidence": ["fixture:runner-only"],
        "tradeoffs": ["Needs live product proof."],
        "veto_check": "All run veto fields are set.",
        "test": "Use live product proof here.",
        "novelty": "The four forms are not alike.",
    } for index, direction in enumerate(directions, 1)]
    return {"options": options, "chosen_direction": {
        "source_option_ids": ["option-1"],
        "reason": "This pick tests record fields only."}}


def decision_lock():
    return {
        "status": "accepted_locked",
        "canonical_creation_after_experiment": True,
        "decision_owner": "direct_current_vision",
        "lower_owner_locks": ["fixture:lower-owner-lock"],
    }


def comparison_fields(action):
    layers = {
        "state_judgment": "states", "atom_judgment": "atoms",
        "part_design": "molecules", "screen_design": "screens",
        "motion_judgment": "transitions",
    }
    return {"controlled_comparisons": [{
        "target_id": f"{action}-item", "layer": layers[action],
        "exploration_option_ids": ["option-1"],
        "experiment": {
            "id": f"experiment:{action}",
            "hypothesis": "The one change will clarify the product job.",
            "null_hypothesis": "The one change will not clarify the product job.",
            "measure": "Current eye, brain, and touch review.",
            "falsifier": "The change harms use, access, or product fit.",
            "frozen_before_view": True,
            "status": "run",
        },
        "changed_factor": "owned-role", "one_factor_only": True,
        "fixed_conditions": ["specimen", "content", "state", "viewport",
                             "input_path", "all_non_tested_tokens"],
        "a_evidence": f"render:{action}:a", "b_evidence": f"render:{action}:b",
        "vision": {"status": "PASS", "freshness": "current",
                   "evidence": [f"vision:{action}"]},
        "decision": "A", "reason": "The retained form clarifies the product job.",
        "decision_lock": decision_lock(),
    }]}


def base_record(packet):
    return {
        "action": packet["action"], "decision": "PASS",
        "evidence": ["fixture:runner-only"],
        "reason": "This record tests run order only.",
        "counterevidence": ["This says no product is good."],
        "uncertainty": "Live product proof is not in this test.",
        "affected": [],
        "context_acknowledgements": packet["context_bundle"]["required_paths"],
        "missing_context": [],
    }


def quality_gate(checkpoint):
    ids = [
        "truth", "access", "task", "perception", "familiarity",
        "standards", "uniqueness", "craft", "resilience",
    ]
    return {"checkpoint": checkpoint, "status": "PASS", "diagnosis": "PASS",
            "gates": [{"id": item, "status": "PASS",
                       "evidence": ["fixture:runner-only"]} for item in ids]}


def state_fields(checklist):
    return {"open_world": True, "exhaustive": False, "state_items": [{
        "id": "fixture-state", "scope": "run rules",
        "context": {"task": "run test"}, "causes": ["test input"],
        "transitions": ["start to test state"],
        "model_reviews": review_groups(checklist, "lenses"),
        "negative_reviews": review_groups(checklist, "negative_checks"),
        "best_response": {"decision": "test reply"},
        "alternatives": ["Use live product proof."],
        "evidence": ["fixture:runner-only"],
        "uncertainty": "This says no state is good.",
    }]}


def passing_record(packet, checklist):
    record = base_record(packet)
    if packet.get("exploration_contract"):
        record.update(exploration_fields())
        record.update(comparison_fields(packet["action"]))
    if packet["action"] == "state_judgment":
        record.update(state_fields(checklist))
        record["quality_gate"] = quality_gate("direction")
    if packet["action"] == "visual_review":
        record["quality_gate"] = quality_gate("integrated")
        record["model_reviews"] = review_groups(checklist, "lenses")
        record["negative_reviews"] = review_groups(
            checklist, "negative_checks")
    return record
