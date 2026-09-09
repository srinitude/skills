"""Real context transport checks; no domain or human acceptance claim."""
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
    ledger = contract.with_name("review-ledger.json")
    ledger.write_text(json.dumps({"rules": ["Preserve supplied agent skill inputs."]}))
    initial = [{"id": "ledger", "role": "ledger", "path": ledger.name,
                "sha256": digest(ledger), "depends_on": []}]
    contract.write_text(json.dumps({
        "skill": ROOT.name, "outcome": outcome, "audience": {"primary": "agent"},
        "domain_terms": ["agent skill", "skill package", "domain result"],
        "task_graph": task_graph(),
        "initial_context": initial,
    }), encoding="utf-8")
    return {
        "version": 1, "operation": "produce an agent skill domain result",
        "context": [{"id": "ledger", "path": str(ledger), "sha256": digest(ledger)}],
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


def invoke(payload, runner):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--request", "-", "--runner", sys.executable,
         "--runner-args-json", json.dumps(["-c", runner])],
        input=json.dumps(payload), capture_output=True, text=True, check=False)


class TestAgenticRequest(unittest.TestCase):
    def test_typed_request_with_context_reaches_runner(self):
        skill = ROOT / "SKILL.md"
        runner = (
            "import json,sys; d=json.load(sys.stdin); "
            "print(json.dumps({'skill':d['use_case']['skill'],"
            "'skills':len(d['skills']),'primitives':len(d['primitives']),'context':d['context'],"
            "'skill_text':d['skills'][0]['text'],'contract_text':d['use_case']['text']}))"
        )
        with tempfile.TemporaryDirectory() as tmp:
            payload = request(pathlib.Path(tmp) / "use-case-contract.json", skill)
            expected_context = pathlib.Path(payload["context"][0]["path"]).read_bytes().decode()
            result = invoke(payload, runner)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["skill"], ROOT.name)
        self.assertEqual(output["context"][0]["text"], expected_context)
        self.assertEqual(output["skill_text"], skill.read_bytes().decode())
        self.assertEqual(json.loads(output["contract_text"])["outcome"],
                         payload["use_case"]["promised_outcome"])

    def test_missing_context_blocks_and_valid_input_recovers(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = request(pathlib.Path(tmp) / "use-case-contract.json", ROOT / "SKILL.md")
            context = payload.pop("context")
            blocked = invoke(payload, "print('RUNNER_STARTED')")
            self.assertEqual(blocked.returncode, 1)
            self.assertIn("context", blocked.stderr)
            self.assertEqual(blocked.stdout, "")
            payload["context"] = context
            recovered = invoke(payload, "print('RUNNER_STARTED')")
            self.assertEqual(recovered.returncode, 0, recovered.stderr)
            self.assertEqual(recovered.stdout.strip(), "RUNNER_STARTED")

    def test_invocation_binding_transports_current_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            contract = pathlib.Path(tmp) / "use-case-contract.json"
            payload = request(contract, ROOT / "SKILL.md")
            data = json.loads(contract.read_text())
            data["initial_context"] = [{"id": "ledger", "role": "ledger",
                                        "binding": "invocation", "depends_on": []}]
            contract.write_text(json.dumps(data))
            payload["use_case"]["sha256"] = digest(contract)
            result = invoke(payload, "import json,sys; print(json.dumps(json.load(sys.stdin)['context']))")
            self.assertEqual(result.returncode, 0, result.stderr)
            context = json.loads(result.stdout)
            self.assertEqual(context[0]["binding"], "invocation")
            self.assertEqual(context[0]["text"],
                             pathlib.Path(payload["context"][0]["path"]).read_text())
            payload["context"][0]["sha256"] = "0" * 64
            failed = invoke(payload, "print('RUNNER_STARTED')")
            self.assertEqual(failed.returncode, 1)
            self.assertEqual(failed.stdout, "")

    def test_help_names_request_interface(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--request", result.stdout)


if __name__ == "__main__":
    unittest.main()
