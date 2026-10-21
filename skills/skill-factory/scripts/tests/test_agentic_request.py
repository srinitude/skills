"""Behavior tests for the platform-neutral agentic request dispatcher."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

from agentic_request_fixtures import (
    CONTRACT, CONTEXT_BYTES, ROOT, SCRIPT, context_resources, digest,
    generic_trace, invoke_stdin, request, runner_args, trace,
)


def _TestAgenticRequest_test_long_prompt_skill_and_primitives_reach_real_runner(self):
    with tempfile.TemporaryDirectory() as tmp:
        prompt = pathlib.Path(tmp) / "prompt.md"
        prompt.write_bytes(("Agent skill caf\u00e9 instruction.\r\n" * 10000).encode())
        skill = ROOT / "SKILL.md"
        manifest = pathlib.Path(tmp) / "request.json"
        payload = request(prompt, skill)
        payload["context"] = context_resources(tmp)
        manifest.write_text(json.dumps(payload), encoding="utf-8")
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
    self.assertEqual(output["skill_text"], skill.read_bytes().decode())
    self.assertEqual(output["contract_text"], CONTRACT.read_bytes().decode())
    self.assertEqual(output["prompt_sha256"], payload["prompt"]["sha256"])
    self.assertEqual({x["id"]: x["text"].encode() for x in output["context"]},
                     CONTEXT_BYTES)

def _TestAgenticRequest_test_request_can_arrive_on_standard_input(self):
    payload = request(ROOT / "SKILL.md", ROOT / "SKILL.md")
    payload["prompt"] = {
        "text": "Use the supplied agent skill.",
        "trace": trace("The inline agent skill prompt"),
    }
    with tempfile.TemporaryDirectory() as tmp:
        payload["context"] = context_resources(tmp)
        result = invoke_stdin(json.dumps(payload))
    self.assertEqual(result.returncode, 0, result.stderr)
    output = json.loads(result.stdout)
    self.assertEqual(output["skills"], 1)
    self.assertEqual({x["id"]: x["text"].encode() for x in output["context"]},
                     CONTEXT_BYTES)

def _TestAgenticRequest_test_digest_mismatch_blocks_before_runner(self):
    payload = request(ROOT / "SKILL.md", ROOT / "SKILL.md")
    payload["skills"][0]["sha256"] = "0" * 64
    result = invoke_stdin(json.dumps(payload))
    self.assertEqual(result.returncode, 1)
    self.assertIn("digest", result.stderr.lower())

def _TestAgenticRequest_test_request_cannot_authorize_its_own_runner(self):
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

def _TestAgenticRequest_test_generic_or_untraced_inputs_fail_before_runner(self):
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

def _TestAgenticRequest_test_promised_outcome_must_match_the_owning_contract(self):
    payload = request(ROOT / "SKILL.md", ROOT / "SKILL.md")
    payload["use_case"]["promised_outcome"] = "A generic result."
    result = invoke_stdin(json.dumps(payload))
    self.assertEqual(result.returncode, 1)
    self.assertIn("promised outcome", result.stderr.lower())

def _TestAgenticRequest_test_contract_without_domain_specific_agentic_task_fails(self):
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

def _TestAgenticRequest_test_noncanonical_json_blocks_before_runner(self):
    raw = json.dumps(request(ROOT / "SKILL.md", ROOT / "SKILL.md"))
    cases = [('{"version":0,' + raw[1:], "duplicate JSON key"),
             (raw.replace('"version": 1', '"version": true'), "version 1")]
    cases += [(raw.replace('"provider": "web"', '"provider": ' + value), "finite")
              for value in ["NaN", "Infinity", "-Infinity", "1e999"]]
    for content, message in cases:
        with self.subTest(content=content[:40], message=message):
            result = invoke_stdin(content, "print('RUNNER_STARTED')")
            self.assertEqual(result.returncode, 1)
            self.assertIn(message, result.stderr)
            self.assertEqual(result.stdout, "")

def _TestAgenticRequest_test_duplicate_contract_does_not_reach_runner(self):
    with tempfile.TemporaryDirectory() as tmp:
        contract = pathlib.Path(tmp) / "use-case-contract.json"
        contract.write_text('{"skill":"wrong",' + CONTRACT.read_text()[1:])
        payload = request(ROOT / "SKILL.md", ROOT / "SKILL.md")
        payload["use_case"].update(path=str(contract), sha256=digest(contract))
        result = invoke_stdin(json.dumps(payload), "print('RUNNER_STARTED')")
    self.assertEqual(result.returncode, 1)
    self.assertIn("duplicate JSON key", result.stderr)
    self.assertEqual(result.stdout, "")


class TestAgenticRequest(unittest.TestCase):
    test_long_prompt_skill_and_primitives_reach_real_runner = _TestAgenticRequest_test_long_prompt_skill_and_primitives_reach_real_runner
    test_request_can_arrive_on_standard_input = _TestAgenticRequest_test_request_can_arrive_on_standard_input
    test_digest_mismatch_blocks_before_runner = _TestAgenticRequest_test_digest_mismatch_blocks_before_runner
    test_request_cannot_authorize_its_own_runner = _TestAgenticRequest_test_request_cannot_authorize_its_own_runner
    test_generic_or_untraced_inputs_fail_before_runner = _TestAgenticRequest_test_generic_or_untraced_inputs_fail_before_runner
    test_promised_outcome_must_match_the_owning_contract = _TestAgenticRequest_test_promised_outcome_must_match_the_owning_contract
    test_contract_without_domain_specific_agentic_task_fails = _TestAgenticRequest_test_contract_without_domain_specific_agentic_task_fails
    test_noncanonical_json_blocks_before_runner = _TestAgenticRequest_test_noncanonical_json_blocks_before_runner
    test_duplicate_contract_does_not_reach_runner = _TestAgenticRequest_test_duplicate_contract_does_not_reach_runner


if __name__ == "__main__":
    unittest.main()
