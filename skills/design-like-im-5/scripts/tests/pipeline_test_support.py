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
    if packet["action"] == "state_judgment":
        record.update(state_fields(checklist))
    if packet["action"] == "visual_review":
        record["model_reviews"] = review_groups(checklist, "lenses")
        record["negative_reviews"] = review_groups(
            checklist, "negative_checks")
    return record
