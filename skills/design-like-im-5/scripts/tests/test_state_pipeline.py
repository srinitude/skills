"""Open state and rich model review contracts."""
import json, pathlib, subprocess, sys, tempfile, unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = SKILL_DIR / "scripts" / "run_pipeline.py"
CHECKLIST = SKILL_DIR / "scripts" / "review_checklist.py"
INTAKE = SKILL_DIR / "evals" / "files" / "valid-intake.json"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True, timeout=120)


def set_next(run_dir, action):
    path = pathlib.Path(run_dir) / "run.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["next"] = action
    path.write_text(json.dumps(data), encoding="utf-8")


def full_checklist():
    result = subprocess.run([sys.executable, str(CHECKLIST)],
                            capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return json.loads(result.stdout)


def model_reviews(checklist):
    reviews = {}
    for lens, items in checklist["lenses"].items():
        reviews[lens] = [{
            "id": item["id"], "scene": "A detailed evidence-bound scene.",
            "observation": "The named render shows the state.",
            "evidence": ["render:1"], "decision": "PASS",
            "reason": "The observation supports the decision.",
            "alternatives": ["Keep the current response."],
            "uncertainty": "Direct use is not yet observed."
        } for item in items]
    return reviews


def negative_reviews(checklist):
    reviews = {}
    for group, items in checklist["negative_checks"].items():
        reviews[group] = [{
            "id": item["id"], "scene": "A detailed evidence-bound scene.",
            "observation": "The named render shows no named harm.",
            "evidence": ["render:1"], "decision": "PASS",
            "reason": "The observation supports the decision.",
            "alternatives": ["Keep the current response."],
            "uncertainty": "Direct use is not yet observed."
        } for item in items]
    return reviews


def exploration():
    options = []
    for index, direction in enumerate([
            "known pattern", "product-shaped form", "true reverse",
            "experimental edge"], start=1):
        options.append({
            "id": f"option-{index}", "direction": direction,
            "scene": "A person completes the task in the named state.",
            "hypothesis": "This response may fit the current goal.",
            "product_fit": "It uses the stated product meaning.",
            "evidence": ["render:1"], "tradeoffs": ["Needs a use test."],
            "veto_check": "No open veto was found.",
            "test": "Observe one full task.",
            "novelty": "This differs in structure and response."
        })
    return {"options": options,
            "chosen_direction": {"source_option_ids": ["option-1"],
                                 "reason": "It best fits current proof."}}


def state_record(reviews, bad_reviews):
    return {
        "action": "state_judgment", "decision": "PASS",
        "open_world": True, "exhaustive": False,
        "state_items": [{
            "id": "account-ready", "scope": "setup flow",
            "context": {"task": "create account"},
            "causes": ["valid form submission"],
            "transitions": ["editing to account-ready"],
            "model_reviews": reviews,
            "negative_reviews": bad_reviews,
            "best_response": {"decision": "show next task"},
            "alternatives": ["show account home"],
            "evidence": ["render:1"],
            "uncertainty": "Return use is not observed."
        }],
        "unknowns": [], "evidence": ["render:1"],
        "reason": "The state is supported.", "counterevidence": [],
        "uncertainty": "Return use is not observed.", "affected": [],
        **exploration(),
    }


class TestStatePipeline(unittest.TestCase):
    def test_start_keeps_the_product_state_set_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run("start", "--intake", INTAKE, "--run-dir", tmp)
            root = pathlib.Path(tmp)
            states = json.loads((root / "state-matrix.json").read_text())
            renders = json.loads((root / "render-plan.json").read_text())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(states["state_set"], "OPEN_CONTEXT_DERIVED")
        self.assertFalse(states["exhaustive"])
        self.assertNotIn("states", states)
        self.assertEqual(renders["state_source"], "state-matrix.json#items")

    def test_state_packet_uses_the_open_state_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            set_next(tmp, "state_judgment")
            result = run("packet", "--run-dir", tmp,
                         "--action", "state_judgment")
            saved = pathlib.Path(tmp) / "packets" / "state_judgment.json"
            data = json.loads(saved.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(data["output_schema"], "assets/state-record.schema.json")
        for name in ["context", "transition", "eye", "brain", "touch"]:
            self.assertIn(name, data["required_evidence"])

    def test_state_record_blocks_missing_state_and_reviews(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            set_next(tmp, "state_judgment")
            run("packet", "--run-dir", tmp, "--action", "state_judgment")
            path = pathlib.Path(tmp) / "state-result.json"
            path.write_text(json.dumps({"action": "state_judgment",
                                        "decision": "PASS", "evidence": ["x"],
                                        "reason": "x", "counterevidence": [],
                                        "uncertainty": "x", "affected": []}))
            result = run("record", "--run-dir", tmp, "--result", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("open state set", result.stderr)
        self.assertIn("state item", result.stderr)

    def test_state_record_requires_a_scene_for_every_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            set_next(tmp, "state_judgment")
            run("packet", "--run-dir", tmp, "--action", "state_judgment")
            root = pathlib.Path(tmp)
            checklist = full_checklist()
            reviews = model_reviews(checklist)
            reviews["eye"][0].pop("scene")
            path = root / "state-result.json"
            path.write_text(json.dumps(state_record(
                reviews, negative_reviews(checklist))), encoding="utf-8")
            result = run("record", "--run-dir", tmp, "--result", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("eye-first scene", result.stderr)

    def test_state_record_requires_every_negative_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            set_next(tmp, "state_judgment")
            run("packet", "--run-dir", tmp, "--action", "state_judgment")
            root = pathlib.Path(tmp)
            checklist = full_checklist()
            bad_reviews = negative_reviews(checklist)
            missing = bad_reviews["bad_design"].pop(0)["id"]
            path = root / "state-result.json"
            path.write_text(json.dumps(state_record(
                model_reviews(checklist), bad_reviews)), encoding="utf-8")
            result = run("record", "--run-dir", tmp, "--result", path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("bad_design review checklist", result.stderr)
        self.assertIn(f"{missing} model review", result.stderr)

    def test_record_blocks_a_changed_check_meaning(self):
        with tempfile.TemporaryDirectory() as tmp:
            run("start", "--intake", INTAKE, "--run-dir", tmp)
            set_next(tmp, "state_judgment")
            run("packet", "--run-dir", tmp, "--action", "state_judgment")
            root = pathlib.Path(tmp)
            checklist_path = root / "review-checklist.json"
            index = json.loads(checklist_path.read_text())
            index["source_command"] = "python3 scripts/style_score.py"
            checklist_path.write_text(json.dumps(index), encoding="utf-8")
            checklist = full_checklist()
            result_path = root / "state-result.json"
            result_path.write_text(json.dumps(state_record(
                model_reviews(checklist), negative_reviews(checklist))),
                encoding="utf-8")
            result = run("record", "--run-dir", tmp, "--result", result_path)
        self.assertEqual(result.returncode, 1)
        self.assertIn("canonical review checklist", result.stderr)


if __name__ == "__main__":
    unittest.main()
