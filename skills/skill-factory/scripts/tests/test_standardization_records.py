"""Public preparation retains authored records, IDs, conditions and uncertainty."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from cli import run, SKILL_DIR
from skill_package import inventory
from test_standardization_inputs import prepare


def invoke(root, profile, target):
    return subprocess.run(["mise", "run", "standardize-target", "--", str(root),
        "--profile", str(profile), "--scope", "user", "--prepare", str(target)],
        cwd=SKILL_DIR, capture_output=True, text=True, timeout=90)


def record(root, name, data):
    path = root / "assets" / name
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")
    return path


class TestStandardizationRecords(unittest.TestCase):
    def test_authored_domain_and_dependency_records_survive_preparation(self):
        with tempfile.TemporaryDirectory() as temp:
            root, profile, target = prepare(Path(temp).resolve())
            domain = {"version": "1.0.0", "skill": root.name,
                "outcome": "Read the clock anchor once and reject an unresolved timezone offset.",
                "domain_terms": ["clock anchor", "timezone offset", "relative date"],
                "motivations": [{"id": "M-4", "condition": "zone unknown", "reason": "Ask once."}],
                "domain_dimensions": {"authorities": ["The caller selects the timezone."],
                    "local-extension": ["Keep this study's declared context."]},
                "human_matrix": {"record": "MATRIX-7", "state": "pending", "conflicts": ["C-2"]},
                "task_graph": {"custom": {"consumer": "anchor", "requires": ["D-9"]},
                    "tasks": {"anchor": {"id": "T-2", "proof": "Actual timestamp readback."}},
                    "public_operations": [{"task": "anchor", "condition": "zone selected"}]}}
            record(root, "use-case-contract.json", domain)
            before = inventory(root)
            result = invoke(root, profile, target)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            actual = json.loads((target / "assets/use-case-contract.json").read_text())
            for key in ["version", "outcome", "domain_terms", "motivations", "human_matrix"]:
                self.assertEqual(actual[key], domain[key], key)
            for key, value in domain["domain_dimensions"].items():
                self.assertEqual(actual["domain_dimensions"][key], value)
            for key in ["custom", "public_operations"]:
                self.assertEqual(actual["task_graph"][key], domain["task_graph"][key])
            self.assertEqual(actual["task_graph"]["tasks"]["anchor"]["id"], "T-2")
            self.assertEqual(actual["task_graph"]["tasks"]["anchor"]["proof"], "Actual timestamp readback.")
            self.assertIn("human-matrix", actual["task_graph"]["tasks"])
            self.assertEqual(inventory(root), before)

    def test_existing_policy_assets_keep_their_full_records(self):
        with tempfile.TemporaryDirectory() as temp:
            root, profile, target = prepare(Path(temp).resolve())
            assets = {}
            for name in ["primitive-lifecycle.json", "decision-records.json",
                         "invocation-receipt-template.json", "mise-primitives.json"]:
                path = record(root, name, {"version": "1.0.0", "skill": root.name,
                    "records": [{"id": name + "/R-2", "state": "conflicting",
                                 "condition": "Caller has not resolved the timezone."}],
                    "unknown": {"preserve": True}})
                assets[name] = path.read_bytes()
            before = inventory(root)
            result = invoke(root, profile, target)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for name, content in assets.items():
                self.assertEqual((target / "assets" / name).read_bytes(), content, name)
            self.assertEqual(inventory(root), before)

    def test_explicit_record_rewrite_survives_and_keeps_unrelated_decisions(self):
        with tempfile.TemporaryDirectory() as temp:
            root, profile, target = prepare(Path(temp).resolve())
            record(root, "decision-records.json", {"version": "1.0.0", "skill": root.name,
                "records": [{"id": "D-1", "condition": "Offset unknown; ask caller."},
                            {"id": "D-2", "state": "pending", "requires": ["H-4"]}]})
            data = json.loads(profile.read_text())
            data["text_rewrites"]["assets/decision-records.json"] = [
                {"old": "Offset unknown; ask caller.", "new": "Offset unknown; request the caller's IANA zone."}]
            profile.write_text(json.dumps(data))
            before = inventory(root)
            result = invoke(root, profile, target)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            actual = json.loads((target / "assets/decision-records.json").read_text())
            self.assertEqual(actual["records"][0], {"id": "D-1",
                "condition": "Offset unknown; request the caller's IANA zone."})
            self.assertEqual(actual["records"][1], {"id": "D-2", "state": "pending", "requires": ["H-4"]})
            self.assertEqual(inventory(root), before)

    def test_invalid_existing_domain_record_rejects_and_recovers(self):
        with tempfile.TemporaryDirectory() as temp:
            root, profile, target = prepare(Path(temp).resolve())
            path = record(root, "use-case-contract.json", [])
            before = inventory(root)
            rejected = invoke(root, profile, target)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertNotIn("Traceback", rejected.stderr)
            self.assertFalse(target.exists())
            self.assertEqual(inventory(root), before)
            path.write_text('{}\n')
            recovered = invoke(root, profile, target)
            self.assertEqual(recovered.returncode, 0, recovered.stdout + recovered.stderr)
            checked = run("check_domain_research.py", target)
            self.assertNotEqual(checked.returncode, 0)


if __name__ == "__main__":
    unittest.main()
