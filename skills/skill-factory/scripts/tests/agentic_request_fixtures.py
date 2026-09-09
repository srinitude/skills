"""Actual subprocess transport fixtures; no full ledger or domain acceptance claim."""
import hashlib
import json
import pathlib
import subprocess
import sys

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
        "'skill_text':d['skills'][0]['text'],"
        "'contract_text':d['use_case']['text'],"
        "'prompt_sha256':d['prompt_sha256'],"
        "'primitives':[p['name'] for p in d['primitives']],"
        "'context':d['context']}))"
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


def invoke_stdin(content, code=None):
    return subprocess.run([sys.executable, str(SCRIPT), "--request", "-",
                           *runner_args(code)], input=content,
                          capture_output=True, text=True, check=False)



# These are deliberately bounded transport inputs, not goal or matrix evidence.
CONTEXT_BYTES = {
    "governing-ledger": b'{"transport_rule":"Keep these exact bytes."}\r\n',
    "study-work-matrix": "Transport input only: caf\u00e9.\r\n".encode(),
}


def context_resources(directory):
    declarations = json.loads(CONTRACT.read_text())["initial_context"]
    assert {x["id"] for x in declarations} == set(CONTEXT_BYTES)
    assert all(x["binding"] == "invocation" for x in declarations)
    resources = []
    for item in declarations:
        path = pathlib.Path(directory) / item["id"]
        path.write_bytes(CONTEXT_BYTES[item["id"]])
        resources.append({"id": item["id"], "path": str(path), "sha256": digest(path)})
    return resources
