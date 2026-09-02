"""Behavior tests for the platform-neutral agentic request dispatcher."""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run_agentic_request.py"
CONTRACT = ROOT / "assets" / "use-case-contract.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def echo_runner_code():
    return (
        "import json,sys; d=json.load(sys.stdin); "
        "print(json.dumps({'operation':d['operation'],"
        "'prompt_bytes':len(d['prompt'].encode()),"
        "'skill':d['use_case']['skill'],"
        "'skills':len(d['skills']),"
        "'primitives':[p['name'] for p in d['primitives']]}))"
    )


def trace(subject):
    return {
        "domain_role": f"{subject} supports the agent skill operation.",
        "outcome_contribution": f"{subject} advances the skill package outcome.",
        "relevance": f"{subject} is needed for this agent skill update.",
        "expected_proof": f"The skill package receipt proves {subject} was used.",
    }


def generic_trace(subject):
    return {
        "domain_role": f"{subject} supports the operation.",
        "outcome_contribution": f"{subject} advances the result.",
        "relevance": f"{subject} is needed for this update.",
        "expected_proof": f"The receipt proves {subject} was used.",
    }


def request(prompt, skill):
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    return {
        "version": 1,
        "operation": "update agent skill package",
        "use_case": {
            "path": str(CONTRACT),
            "sha256": digest(CONTRACT),
            "promised_outcome": contract["outcome"],
        },
        "prompt": {"file": str(prompt), "sha256": digest(prompt),
                   "trace": trace("The domain prompt")},
        "skills": [{"path": str(skill), "sha256": digest(skill),
                    "trace": trace("The skill-factory dependency")}],
        "primitives": [{
            "kind": "tool",
            "name": "agent skill web evidence",
            "configuration": {"provider": "web"},
            "trace": trace("The agent skill web tool"),
        }],
    }


def runner_args(code=None):
    arguments = ["-c", code or echo_runner_code()]
    return ["--runner", sys.executable,
            "--runner-args-json", json.dumps(arguments)]


class TestAgenticRequest(unittest.TestCase):
    def test_long_prompt_skill_and_primitives_reach_real_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt = pathlib.Path(tmp) / "prompt.md"
            prompt.write_text("Agent skill domain instruction.\n" * 10000,
                              encoding="utf-8")
            skill = ROOT / "SKILL.md"
            manifest = pathlib.Path(tmp) / "request.json"
            manifest.write_text(json.dumps(request(prompt, skill)), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--request", str(manifest),
                 *runner_args()],
                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertGreater(output["prompt_bytes"], 100000)
        self.assertEqual(output["skills"], 1)
        self.assertEqual(output["skill"], "skill-factory")
        self.assertEqual(output["primitives"], ["agent skill web evidence"])

    def test_request_can_arrive_on_standard_input(self):
        payload = request(ROOT / "SKILL.md", ROOT / "SKILL.md")
        payload["prompt"] = {
            "text": "Use the supplied agent skill.",
            "trace": trace("The inline agent skill prompt"),
        }
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--request", "-", *runner_args()],
            input=json.dumps(payload), capture_output=True, text=True,
            check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["skills"], 1)

    def test_digest_mismatch_blocks_before_runner(self):
        payload = request(ROOT / "SKILL.md", ROOT / "SKILL.md")
        payload["skills"][0]["sha256"] = "0" * 64
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--request", "-", *runner_args()],
            input=json.dumps(payload), capture_output=True, text=True,
            check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("digest", result.stderr.lower())

    def test_request_cannot_authorize_its_own_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = pathlib.Path(tmp) / "should-not-exist"
            payload = request(ROOT / "SKILL.md", ROOT / "SKILL.md")
            payload["runner"] = {
                "command": sys.executable,
                "args": ["-c", f"open({str(marker)!r},'w').write('bad')"],
            }
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--request", "-"],
                input=json.dumps(payload), capture_output=True, text=True,
                check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(marker.exists())

    def test_generic_or_untraced_inputs_fail_before_runner(self):
        mutations = [
            lambda item: item["prompt"].pop("trace"),
            lambda item: item.update(
                prompt={"text": "Do a generic thing.",
                        "trace": trace("The agent skill prompt")}),
            lambda item: item["skills"][0].update(
                trace=generic_trace("A generic dependency")),
            lambda item: item["primitives"][0].update(
                trace=generic_trace("A generic tool")),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                payload = request(ROOT / "SKILL.md", ROOT / "SKILL.md")
                mutate(payload)
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), "--request", "-",
                     *runner_args()], input=json.dumps(payload),
                    capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 1)
                self.assertIn("domain", result.stderr.lower())

    def test_promised_outcome_must_match_the_owning_contract(self):
        payload = request(ROOT / "SKILL.md", ROOT / "SKILL.md")
        payload["use_case"]["promised_outcome"] = "A generic result."
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--request", "-", *runner_args()],
            input=json.dumps(payload), capture_output=True, text=True,
            check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("promised outcome", result.stderr.lower())

    def test_contract_without_domain_specific_agentic_task_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            contract = pathlib.Path(tmp) / "use-case-contract.json"
            outcome = "The agent skill produces a verified domain result."
            contract.write_text(json.dumps({
                "skill": "agent-skill-trial", "outcome": outcome,
                "domain_terms": ["agent skill", "skill package", "domain result"],
            }), encoding="utf-8")
            payload = request(ROOT / "SKILL.md", ROOT / "SKILL.md")
            payload["use_case"] = {
                "path": str(contract), "sha256": digest(contract),
                "promised_outcome": outcome,
            }
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--request", "-",
                 *runner_args()], input=json.dumps(payload),
                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("agentic-request", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
