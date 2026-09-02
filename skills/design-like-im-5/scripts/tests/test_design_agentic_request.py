"""Test the typed design request path."""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "run_design_agentic_request.py"
CONTRACT = ROOT / "assets" / "use-case-contract.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trace(subject):
    return {
        "domain_role": f"{subject} helps a fresh design choice.",
        "outcome_contribution": f"{subject} helps the design goal.",
        "relevance": f"{subject} is needed for this design work.",
        "expected_proof": f"Fresh design proof shows use of {subject}.",
    }


def request(prompt):
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    return {
        "version": 1, "operation": "review fresh product design proof",
        "use_case": {"path": str(CONTRACT), "sha256": digest(CONTRACT),
                     "promised_outcome": contract["outcome"]},
        "prompt": {"file": str(prompt), "sha256": digest(prompt),
                   "trace": trace("The product design prompt")},
        "skills": [{"path": str(ROOT / "SKILL.md"),
                    "sha256": digest(ROOT / "SKILL.md"),
                    "trace": trace("The product design skill")}],
        "primitives": [{"kind": "vision", "name": "product design vision",
                        "configuration": {"direct": True},
                        "trace": trace("The product design vision primitive")}],
    }


def command(payload, code=None):
    code = code or "import json,sys; print(len(json.load(sys.stdin)['prompt']))"
    return subprocess.run(
        [sys.executable, str(RUNNER), "--request", "-", "--runner",
         sys.executable, "--runner-args-json", json.dumps(["-c", code])],
        input=json.dumps(payload), capture_output=True, text=True, check=False)


class TestDesignAgenticRequest(unittest.TestCase):
    def test_long_prompt_skill_and_vision_reach_the_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt = pathlib.Path(tmp) / "prompt.md"
            prompt.write_text("Product design human eye evidence.\n" * 10000)
            result = command(request(prompt))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater(int(result.stdout), 100000)

    def test_changed_dependency_digest_blocks_before_the_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt = pathlib.Path(tmp) / "prompt.md"
            prompt.write_text("Product design human touch evidence.\n")
            payload = request(prompt)
            payload["skills"][0]["sha256"] = "0" * 64
            result = command(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("digest", result.stderr.lower())

    def test_request_cannot_choose_its_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            prompt = pathlib.Path(tmp) / "prompt.md"
            prompt.write_text("Product design human brain evidence.\n")
            payload = request(prompt)
            payload["runner"] = {"command": "untrusted"}
            result = command(payload)
        self.assertEqual(result.returncode, 1)
        self.assertIn("runner", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
