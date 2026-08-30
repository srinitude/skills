"""Put full support next to each set action."""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = pathlib.Path(__file__).resolve().parents[2]
ROUTE_FILE = SKILL / "assets" / "context-routing.json"
WORKFLOW = SKILL / "assets" / "workflow.json"
CONTEXT_CASES = SKILL / "evals" / "context-cases.json"
SUPPORT_CLASSES = {"references", "scripts", "assets", "examples", "evals"}
CONTEXT_SUPPORT = {
    "references/context-routing.md",
    "scripts/check_context_routing.py",
    "assets/context-routing.json",
    "assets/context-bundle.schema.json",
    "examples/context-packets.md",
    "evals/context-cases.json",
}
RECORD_SCHEMAS = [
    "assets/model-record.schema.json",
    "assets/state-record.schema.json",
    "assets/review-record.schema.json",
]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class TestContextRouting(unittest.TestCase):
    def routes(self):
        self.assertTrue(ROUTE_FILE.is_file(), "missing assets/context-routing.json")
        return load(ROUTE_FILE)["routes"]

    def test_each_route_has_one_body_anchor(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        routes = self.routes()
        ids = [route["id"] for route in routes]
        self.assertEqual(len(ids), len(set(ids)))
        for route_id in ids:
            self.assertEqual(text.count(f"[{route_id}]"), 1, route_id)

    def test_each_workflow_action_has_all_five_support_classes(self):
        routes = {route.get("action"): route for route in self.routes()}
        actions = [row["action"] for row in load(WORKFLOW)["steps"]]
        for action in actions:
            self.assertIn(action, routes, action)
            self.assertEqual(set(routes[action]["support"]), SUPPORT_CLASSES,
                             action)

    def test_each_support_path_exists_and_names_its_contribution(self):
        for route in self.routes():
            self.assertTrue(route.get("load_when"), route.get("id"))
            self.assertTrue(route.get("produce"), route.get("id"))
            self.assertTrue(route.get("do_not_substitute"), route.get("id"))
            for rows in route.get("support", {}).values():
                self.assertTrue(rows, route.get("id"))
                for row in rows:
                    self.assertTrue((SKILL / row["path"]).is_file(), row["path"])
                    self.assertTrue(row.get("contribution"), row["path"])

    def test_scripts_never_own_design_judgment(self):
        forbidden = {"decision", "rank", "score", "chosen_direction"}
        for route in self.routes():
            self.assertEqual(route.get("judgment_owner"), "model")
            self.assertFalse(forbidden & set(route), route.get("id"))

    def test_body_names_each_context_support_owner(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for path in CONTEXT_SUPPORT:
            self.assertIn(path, text, path)

    def test_each_model_record_schema_requires_context_accounting(self):
        for path in RECORD_SCHEMAS:
            schema = load(SKILL / path)
            required = set(schema.get("required", []))
            self.assertIn("context_acknowledgements", required, path)
            self.assertIn("missing_context", required, path)

    def test_each_workflow_action_has_a_context_loss_case(self):
        actions = {row["action"] for row in load(WORKFLOW)["steps"]}
        tested = {row["action"] for row in load(CONTEXT_CASES)["cases"]}
        self.assertEqual(actions, tested)

    def test_eval_contract_names_context_cases_and_record_fixtures(self):
        text = (SKILL / "evals" / "contract.md").read_text(encoding="utf-8")
        for path in ["context-cases.json", "files/valid-context-record.json",
                     "files/missing-context-record.json"]:
            self.assertIn(path, text)

    def test_route_checker_rejects_a_missing_context_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / "skill"
            shutil.copytree(SKILL, copy)
            path = copy / "evals" / "context-cases.json"
            data = load(path)
            data["cases"].pop()
            path.write_text(json.dumps(data), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(copy / "scripts" /
                                     "check_context_routing.py"), str(copy)],
                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 1)
        self.assertIn("context eval", result.stdout)


if __name__ == "__main__":
    unittest.main()
