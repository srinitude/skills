"""Rich review checklist contracts."""
import json, pathlib, subprocess, sys, tempfile, unittest

SKILL_DIR = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = SKILL_DIR / "scripts" / "run_pipeline.py"
CHECKLIST = SKILL_DIR / "scripts" / "review_checklist.py"
INTAKE = SKILL_DIR / "evals" / "files" / "valid-intake.json"


def start(path):
    return subprocess.run([sys.executable, str(SCRIPT), "start", "--intake",
                           str(INTAKE), "--run-dir", path],
                          capture_output=True, text=True, timeout=120)


def load_index(path):
    target = pathlib.Path(path) / "review-checklist.json"
    return json.loads(target.read_text(encoding="utf-8"))


def load_checklist():
    result = subprocess.run([sys.executable, str(CHECKLIST)],
                            capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise RuntimeError(result.stderr)
    return json.loads(result.stdout)


def assert_rich(case, items):
    ids = [item["id"] for item in items]
    case.assertGreaterEqual(len(ids), 10)
    case.assertEqual(len(ids), len(set(ids)))
    for item in items:
        case.assertGreaterEqual(len(item["scene_prompt"]), 100)
        case.assertGreaterEqual(len(item["probes"]), 3)
        case.assertGreaterEqual(len(item["evidence_needs"]), 2)
        case.assertGreaterEqual(len(item["failure_signals"]), 2)
        meaning = item["semantic_contract"]
        case.assertEqual(meaning["one_question"], item["prompt"])
        case.assertEqual(meaning["probe_order"], "probes")
        case.assertEqual(meaning["evidence_boundary"], "evidence_needs")
        case.assertEqual(meaning["failure_meaning"], "failure_signals")
        case.assertEqual(meaning["decision_rules"], "decision_rules")
        case.assertEqual(meaning["forbidden_reinterpretations"],
                         "forbidden_reinterpretations")


class TestReviewContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        result = start(self.temp.name)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.index = load_index(self.temp.name)
        self.checklist = load_checklist()

    def tearDown(self):
        self.temp.cleanup()

    def test_checklist_is_deterministic_and_has_fixed_owners(self):
        second = load_checklist()
        self.assertEqual(self.checklist, second)
        self.assertEqual(self.checklist["owner"], "script")
        self.assertEqual(self.checklist["review_owner"], "model")
        self.assertIn("scene", self.checklist["required_answer_fields"])
        self.assertGreaterEqual(len(self.checklist["scene_prompt_template"]), 400)

    def test_run_index_is_small_and_points_to_the_full_checklist(self):
        raw = json.dumps(self.index, sort_keys=True, separators=(",", ":"))
        self.assertLess(len(raw), 10000)
        self.assertEqual(self.index["source_command"],
                         "python3 scripts/review_checklist.py")
        self.assertEqual(self.index["invariants"], self.checklist["invariants"])
        self.assertEqual(self.index["negative_invariants"],
                         self.checklist["negative_invariants"])
        self.assertEqual(self.index["item_count"], 70)

    def test_all_positive_and_negative_items_are_rich(self):
        for lens, items in self.checklist["lenses"].items():
            self.assertEqual(self.checklist["invariants"][lens],
                             [item["id"] for item in items])
            assert_rich(self, items)
        for group, items in self.checklist["negative_checks"].items():
            self.assertEqual(self.checklist["negative_invariants"][group],
                             [item["id"] for item in items])
            assert_rich(self, items)

    def test_objective_and_semantic_rules_are_fixed(self):
        decisions = {"PASS", "REVISE", "BLOCKED", "NOT_APPLICABLE"}
        self.assertEqual(set(self.checklist["decision_rules"]), decisions)
        objective = self.checklist["negative_checks"]["objective_failure"]
        ids = [item["id"] for item in objective]
        self.assertIn("objective-text-overlap", ids)
        self.assertIn("objective-image-overlap", ids)
        self.assertIn("not a fixed taste rule",
                      self.checklist["negative_invariant_rule"])

    def test_human_sweep_is_open_and_applies_to_every_check(self):
        sweep = self.checklist["human_capability_sweep"]
        self.assertEqual((sweep["open_world"], sweep["exhaustive"]),
                         (True, False))
        for items in sweep["lenses"].values():
            ids = [item["id"] for item in items]
            self.assertGreaterEqual(len(ids), 25)
            self.assertEqual(len(ids), len(set(ids)))
        groups = [self.checklist["lenses"], self.checklist["negative_checks"]]
        for items in [items for group in groups for items in group.values()]:
            for item in items:
                self.assertEqual(item["human_lenses"],
                                 ["eye", "brain", "touch"])
                self.assertEqual(item["apply_human_sweep"], "ALL")


if __name__ == "__main__":
    unittest.main()
