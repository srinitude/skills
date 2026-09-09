"""Public preparation preserves supplied evidence and the full case inventory."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

from cli import run, SCRIPTS
sys.path.insert(0, str(SCRIPTS))
from skill_package import inventory
from test_standardize_registry_skill import profile, write_target


def prepare(base, data=None):
    root = base / "clock-anchor"
    write_target(root)
    path = base / "profile.json"
    path.write_text(json.dumps(data if data is not None else profile()))
    target = base / "prepared" / root.name
    return root, path, target


def invoke(root, path, target):
    return run("standardize_registry_skill.py", root, "--profile", path,
               "--scope", "user", "--prepare", target)


class TestStandardizationInputs(unittest.TestCase):
    def test_all_cases_keep_ids_conditions_and_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            root, path, target = prepare(Path(temp))
            (root / "evals").mkdir()
            cases = [{"id": f"CASE-{i}", "prompt": f"Read clock input {i}.",
                      "expected_output": "An offset-aware timestamp.",
                      "assertions": ["Reject a missing offset."],
                      "condition": {"format": "RFC3339", "index": i}}
                     for i in range(12)]
            queries = [{"id": f"TRIGGER-{i}", "prompt": f"Read time query {i}.",
                        "should_trigger": i % 2 == 0} for i in range(14)]
            (root / "evals/cases.json").write_text(json.dumps({"cases": cases}))
            (root / "evals/trigger-cases.json").write_text(json.dumps({"cases": queries}))
            before = inventory(root)
            result = invoke(root, path, target)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            actual = json.loads((target / "evals/evals.json").read_text())["evals"]
            self.assertEqual(actual, cases)
            triggers = json.loads((target / "evals/trigger-queries.json").read_text())
            self.assertEqual(triggers, [{**q, "query": q["prompt"]} for q in queries])
            checked = run("check_evals.py", target)
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertEqual(inventory(root), before)

    def test_missing_cases_and_research_stay_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            root, path, target = prepare(Path(temp))
            result = invoke(root, path, target)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads((target / "evals/evals.json").read_text())["evals"], [])
            self.assertEqual(json.loads((target / "evals/trigger-queries.json").read_text()), [])
            data = json.loads((target / "assets/use-case-contract.json").read_text())
            self.assertEqual(data["research_receipts"], [])
            self.assertEqual(data["disconfirmation"], [])
            self.assertEqual(data["research_sources"], profile()["sources"])
            for checker in ["check_domain_research.py", "check_evals.py"]:
                rejected = run(checker, target)
                self.assertNotEqual(rejected.returncode, 0, rejected.stdout)

    def test_existing_research_is_preserved_without_refresh_or_expansion(self):
        with tempfile.TemporaryDirectory() as temp:
            root, path, target = prepare(Path(temp))
            (root / "assets").mkdir()
            receipt = {**profile()["sources"][0], "checked_at": "2020-01-01T00:00:00Z",
                       "dimensions": ["time"], "disposition": "bounded",
                       "reviewer": "Historical fixture, not a current research claim."}
            previous = {"research_receipts": [receipt], "disconfirmation": []}
            (root / "assets/use-case-contract.json").write_text(json.dumps(previous))
            result = invoke(root, path, target)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            data = json.loads((target / "assets/use-case-contract.json").read_text())
            self.assertEqual(data["research_receipts"], [receipt])
            self.assertEqual(data["disconfirmation"], [])
            rejected = run("check_domain_research.py", target)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("not current", rejected.stdout)

    def test_profile_rejects_malformed_input_without_writes_or_traceback(self):
        bad = ["[]", "null", '{"profiles":[]}', '{"skill":"x","skill":"clock-anchor"}',
               json.dumps({**profile(), "script_tasks": {"inspect": None}}),
               json.dumps({**profile(), "unknown": float("nan")})]
        for raw in bad:
            with self.subTest(raw=raw[:80]), tempfile.TemporaryDirectory() as temp:
                root, path, target = prepare(Path(temp))
                path.write_text(raw)
                before = inventory(root)
                result = invoke(root, path, target)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(target.exists())
                self.assertEqual(inventory(root), before)


if __name__ == "__main__":
    unittest.main()
