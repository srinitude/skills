"""Attack standalone DTCG policy checks with malformed real packages."""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "check_token_policy.py"
POLICY_FILES = [
    "use-case-contract.json",
    "primitive-lifecycle.json",
    "decision-records.json",
    "mise-primitives-catalog.json",
    "mise-primitives.json",
]
TEXT_FIELDS = ["outcome", "motivation", "value", "proof", "applicability"]
DECISION_FIELDS = [
    "outcome", "motivation", "why_this_path", "expected_effect", "proof",
    "falsifier", "failure_branch",
]


def copy_policy_package(destination):
    shutil.copy2(ROOT / "mise.toml", destination / "mise.toml")
    assets = destination / "assets"
    assets.mkdir()
    for name in POLICY_FILES:
        shutil.copy2(ROOT / "assets" / name, assets / name)


def read_json(root, name):
    return json.loads((root / "assets" / name).read_text(encoding="utf-8"))


def write_json(root, name, data):
    (root / "assets" / name).write_text(
        json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_policy(mode, root):
    return subprocess.run(
        [sys.executable, str(SCRIPT), mode, str(root)],
        capture_output=True, text=True, timeout=30,
    )


class TokenPolicyFailClosedTests(unittest.TestCase):
    def run_attack(self, mode, mutate):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            copy_policy_package(root)
            mutate(root)
            return run_policy(mode, root)

    def test_circular_mise_graph_is_rejected(self):
        def mutate(root):
            text = (root / "mise.toml").read_text(encoding="utf-8")
            text = text.replace(
                'depends = ["acceptance", "lineage"]',
                'depends = ["acceptance", "lineage", "ci"]', 1)
            (root / "mise.toml").write_text(text, encoding="utf-8")

        result = self.run_attack("task-graph", mutate)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("cycle", result.stdout.lower())

    def test_domain_label_cannot_hide_generic_task_record(self):
        def mutate(root):
            data = read_json(root, "use-case-contract.json")
            record = data["task_graph"]["tasks"]["ci"]
            for field in TEXT_FIELDS:
                record[field] = "DTCG token operation advances or proves its named package state."
            write_json(root, "use-case-contract.json", data)

        result = self.run_attack("task-graph", mutate)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("generic", result.stdout.lower())

    def test_domain_label_cannot_hide_generic_decision(self):
        def mutate(root):
            data = read_json(root, "decision-records.json")
            record = data["records"][0]
            for field in DECISION_FIELDS:
                record[field] = "DTCG token operation produces objective progress or a bounded failure."
            write_json(root, "decision-records.json", data)

        result = self.run_attack("decisions", mutate)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("generic", result.stdout.lower())

    def test_research_receipts_require_real_provenance_fields(self):
        def mutate(root):
            data = read_json(root, "use-case-contract.json")
            dimensions = list(data["research_questions"])
            data["research_receipts"] = [{"dimensions": dimensions}] * 4
            data["disconfirmation"] = ["DTCG token"]
            write_json(root, "use-case-contract.json", data)

        result = self.run_attack("domain-research", mutate)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("receipt", result.stdout.lower())

    def test_multiple_dependency_paths_are_rejected(self):
        def mutate(root):
            text = (root / "mise.toml").read_text(encoding="utf-8")
            text = text.replace(
                'depends = ["acceptance", "lineage"]',
                'depends = ["acceptance", "lineage", "test"]', 1)
            (root / "mise.toml").write_text(text, encoding="utf-8")

        result = self.run_attack("task-graph", mutate)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("multiple dependency paths", result.stdout.lower())

    def test_nested_mise_in_command_array_is_rejected(self):
        def mutate(root):
            text = (root / "mise.toml").read_text(encoding="utf-8")
            text = text.replace(
                'run = "python3 scripts/check_lineage.py ."',
                'run = ["python3 scripts/check_lineage.py .", "mise run validate"]', 1)
            (root / "mise.toml").write_text(text, encoding="utf-8")

        result = self.run_attack("task-graph", mutate)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("nests mise", result.stdout.lower())

    def test_task_without_description_is_rejected(self):
        def mutate(root):
            text = (root / "mise.toml").read_text(encoding="utf-8")
            text = text.replace(
                'description = "Validate current DTCG token source-lineage hashes and release version"\n',
                "", 1)
            (root / "mise.toml").write_text(text, encoding="utf-8")

        result = self.run_attack("task-graph", mutate)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("description", result.stdout.lower())

    def test_duplicate_decision_id_and_empty_inputs_are_rejected(self):
        def mutate(root):
            data = read_json(root, "decision-records.json")
            data["records"][1]["id"] = data["records"][0]["id"]
            data["records"][1]["inputs"] = []
            write_json(root, "decision-records.json", data)

        result = self.run_attack("decisions", mutate)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("decision", result.stdout.lower())

    def test_duplicate_terms_and_empty_dimensions_are_rejected(self):
        def mutate(root):
            data = read_json(root, "use-case-contract.json")
            data["domain_terms"] = ["DTCG token"] * 4
            data["domain_dimensions"]["actors"] = []
            write_json(root, "use-case-contract.json", data)

        result = self.run_attack("use-case", mutate)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("domain", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
