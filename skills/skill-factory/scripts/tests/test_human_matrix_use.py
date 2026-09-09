"""Require bound matrix use at actual policy consumers, including skipped dependencies."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from cli import SKILL_DIR, run
from human_matrix_fixtures import case, save
from skill_package import inventory, tree_digest
from test_human_catalogs import resources

TASKS = ["domain-research-policy", "use-case-policy", "decision-policy", "evals"]


def invoke(task, arguments=(), root=SKILL_DIR):
    return subprocess.run(["mise", "run", "--force", "--task-cache", "off", task,
                           "--", *map(str, arguments)], cwd=root,
                          env={**os.environ, "NO_COLOR": "1"}, text=True, capture_output=True, timeout=120)


def context(base, target=SKILL_DIR):
    document = case(base)
    uses = {}
    for task in TASKS:
        record = {"task": task, "subject_sha256": tree_digest(inventory(target)),
                  "interactions": ["practice-and-create"], "framing": ["brief"],
                  "challenge": ["counterevidence"], "criteria": ["criterion"], "assessment": ["assessment"]}
        name = task + ".json"
        digest = save(base / name, {"use": record})
        document["records"][task] = {"path": name, "sha256": digest, "pointer": ["use"]}
        uses[task] = task
    facts = {"counterevidence": "The fixture supplies no participant observation or semantic acceptance.",
             "criterion": "Resolve the supplied repeated activity without changing its identity.",
             "assessment": "Only consumer binding and record resolution are exercised by this test."}
    digest = save(base / "assessment.json", facts)
    for name in facts:
        document["records"][name] = {"path": "assessment.json", "sha256": digest, "pointer": [name]}
    matrix_digest = save(base / "matrix.json", document)
    resource_digest = save(base / "resources.json", resources())
    value = {"version": 1, "resources": {"path": "resources.json", "sha256": resource_digest},
             "matrix": {"path": "matrix.json", "sha256": matrix_digest}, "uses": uses}
    path = base / "human context.json"
    return path, save(path, value)


class TestHumanMatrixUse(unittest.TestCase):
    def test_each_public_consumer_and_direct_checker_rejects_missing_matrix(self):
        for task in TASKS:
            with self.subTest(task=task):
                result = invoke(task)
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("human", (result.stdout + result.stderr).lower())
        for script in ["check_domain_research.py", "check_use_case_contract.py", "check_decision_records.py", "check_evals.py"]:
            result = run(script, SKILL_DIR)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("human matrix use requires", result.stdout)

    def test_real_matrix_use_is_bound_to_the_consumer_and_actual_subject(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            path, digest = context(base)
            for task in TASKS:
                result = invoke(task, ["--human-context", path, "--human-context-sha256", digest])
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('"task": "' + task + '"', result.stdout)
            result = invoke("domain-research-policy", ["--human-context", path, "--human-context-sha256", digest])
            line = next(line for line in result.stdout.splitlines() if line.startswith('{"human_matrix_use"'))
            use = json.loads(line)["human_matrix_use"]
            self.assertEqual(use["task"], "domain-research-policy")
            self.assertEqual(use["subject_sha256"], tree_digest(inventory(SKILL_DIR)))
            self.assertEqual(use["acceptance"], "pending")
            self.assertIn("no participant", use["challenge"][0])
            value = json.loads((base / "domain-research-policy.json").read_text())
            value["use"]["subject_sha256"] = "0" * 64
            record_digest = save(base / "domain-research-policy.json", value)
            document = json.loads((base / "matrix.json").read_text())
            document["records"]["domain-research-policy"]["sha256"] = record_digest
            updated = json.loads(path.read_text())
            updated["matrix"]["sha256"] = save(base / "matrix.json", document)
            changed = invoke("domain-research-policy", ["--human-context", path,
                                                       "--human-context-sha256", save(path, updated)])
            self.assertNotEqual(changed.returncode, 0)
            self.assertIn("subject", changed.stdout + changed.stderr)

    def test_changed_records_and_wrong_consumer_reject_then_recover(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            path, digest = context(base)
            original = json.loads(path.read_text())
            changed = {**original, "uses": {"domain-research-policy": "evals"}}
            result = invoke("domain-research-policy", ["--human-context", path,
                                                      "--human-context-sha256", save(path, changed)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("another task", result.stdout)
            record = base / "domain-research-policy.json"
            previous = record.read_bytes()
            record.write_bytes(previous + b" ")
            result = invoke("domain-research-policy", ["--human-context", path,
                                                      "--human-context-sha256", save(path, original)])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("digest differs", result.stdout)
            record.write_bytes(previous)
            repaired = invoke("domain-research-policy", ["--human-context", path, "--human-context-sha256", digest])
            self.assertEqual(repaired.returncode, 0, repaired.stdout + repaired.stderr)

    def test_no_required_use_record_can_be_omitted(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp).resolve()
            path, _ = context(base)
            original = json.loads(path.read_text())
            matrix = json.loads((base / "matrix.json").read_text())
            record = json.loads((base / "domain-research-policy.json").read_text())
            for field in ["interactions", "framing", "challenge", "criteria", "assessment"]:
                changed = {"use": {**record["use"], field: []}}
                matrix["records"]["domain-research-policy"]["sha256"] = save(base / "domain-research-policy.json", changed)
                original["matrix"]["sha256"] = save(base / "matrix.json", matrix)
                result = invoke("domain-research-policy", ["--human-context", path,
                                                          "--human-context-sha256", save(path, original)])
                self.assertNotEqual(result.returncode, 0, field)
                self.assertIn("matrix use needs", result.stdout)

    def test_target_evaluation_passes_the_explicit_bindings_to_its_actual_consumer(self):
        with tempfile.TemporaryDirectory() as temp:
            path, digest = context(Path(temp).resolve())
            result = invoke("eval-target", [SKILL_DIR, "--human-context", path, "--human-context-sha256", digest])
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('"task": "evals"', result.stdout)
            self.assertIn("acceptance: pending", result.stdout)


if __name__ == "__main__":
    unittest.main()
