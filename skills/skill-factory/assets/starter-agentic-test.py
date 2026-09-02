"""Behavior test for this skill's agentic request dispatcher."""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run_agentic_request.py"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trace(subject):
    return {
        "domain_role": f"{subject} supports the agent skill operation.",
        "outcome_contribution": f"{subject} advances the skill package outcome.",
        "relevance": f"{subject} is required for this agent skill result.",
        "expected_proof": f"The agent skill receipt proves {subject} was used.",
    }


def task_graph():
    task = {
        "outcome": "The agent skill sends one verified domain result.",
        "motivation": "The skill package needs relevant model-owned work.",
        "value": "The agent skill request advances the domain result.",
        "proof": "The skill package runner receipt proves dispatch.",
        "applicability": "Run for an agent skill model-owned operation.",
    }
    operation = {
        "task": "agentic-request",
        "outcome": "The agent skill sends one verified domain result.",
        "motivation": "The skill package needs relevant model-owned work.",
        "why_default_path": "The agent skill uses one typed request path.",
        "proof": "The skill package runner receipt proves dispatch.",
    }
    return {"tasks": {"agentic-request": task},
            "public_operations": [operation]}


def request(contract, skill):
    outcome = "The agent skill produces a verified domain result."
    contract.write_text(json.dumps({
        "skill": ROOT.name, "outcome": outcome,
        "domain_terms": ["agent skill", "skill package", "domain result"],
        "task_graph": task_graph(),
    }), encoding="utf-8")
    return {
        "version": 1, "operation": "produce an agent skill domain result",
        "use_case": {"path": str(contract), "sha256": digest(contract),
                     "promised_outcome": outcome},
        "prompt": {"text": "Inspect the agent skill domain result.",
                   "trace": trace("The agent skill prompt")},
        "skills": [{"path": str(skill), "sha256": digest(skill),
                    "trace": trace("The agent skill dependency")}],
        "primitives": [{"kind": "tool", "name": "agent skill evaluator",
                        "configuration": {},
                        "trace": trace("The agent skill evaluator")}],
    }


class TestAgenticRequest(unittest.TestCase):
    def test_domain_specific_request_reaches_runner(self):
        skill = ROOT / "SKILL.md"
        runner = (
            "import json,sys; d=json.load(sys.stdin); "
            "print(json.dumps({'skill':d['use_case']['skill'],"
            "'skills':len(d['skills']),'primitives':len(d['primitives'])}))"
        )
        with tempfile.TemporaryDirectory() as tmp:
            payload = request(pathlib.Path(tmp) / "use-case-contract.json", skill)
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--request", "-",
                 "--runner", sys.executable,
                 "--runner-args-json", json.dumps(["-c", runner])],
                input=json.dumps(payload), capture_output=True, text=True,
                check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["skill"], ROOT.name)

    def test_help_names_request_interface(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--request", result.stdout)


if __name__ == "__main__":
    unittest.main()
