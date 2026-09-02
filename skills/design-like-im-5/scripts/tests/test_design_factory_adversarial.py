"""Break weak design factory claims."""
import copy
import hashlib
import json
import pathlib
import sys
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.design_agentic_request import build_envelope
from lib.design_policy_research import research_problems
from lib.design_policy_text import text_problems
from check_design_invocation import problems as invocation_problems
from check_design_policy import ASPECTS


def load_json(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def task_data():
    with (ROOT / "mise.toml").open("rb") as handle:
        return tomllib.load(handle)["tasks"]


def receipt(tasks, status="run"):
    entries = [{"task": name, "status": status,
                "applicability_reason": "Human eye product design task use.",
                "proof": "Fresh human eye product design task proof."}
               for name in tasks if name != "invocation-policy"]
    return {"skill": "design-like-im-5",
            "operation": "Review product design proof.", "entries": entries}


def trace(subject):
    return {
        "domain_role": f"{subject} guides fresh product design work.",
        "outcome_contribution": f"{subject} helps the product design goal.",
        "relevance": f"{subject} is needed for this product design act.",
        "expected_proof": f"Fresh product design proof must name {subject}.",
    }


def agent_request():
    path = ROOT / "assets/use-case-contract.json"
    contract = load_json("assets/use-case-contract.json")
    primitive = {"kind": "vision", "name": "product design vision",
                 "configuration": {"direct": True}, "trace": trace("Vision")}
    return {"version": 1, "operation": "Review product design proof.",
            "use_case": {"path": str(path),
                         "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                         "promised_outcome": contract["outcome"]},
            "prompt": {"text": "Review product design proof.",
                       "trace": trace("The prompt")},
            "skills": [], "primitives": [primitive]}


class DesignFactoryAdversarialTests(unittest.TestCase):
    def test_same_claim_cannot_fill_each_owned_field(self):
        record = {name: "Fresh human eye product design proof."
                  for name in ["outcome", "motivation", "proof"]}
        found = text_problems(record, set(record), ["product design"], "choice")
        self.assertTrue(any("repeat" in item for item in found), found)

    def test_default_gate_cannot_be_marked_inapplicable(self):
        tasks = task_data()
        found = invocation_problems(tasks, load_json("assets/use-case-contract.json"),
                                    receipt(tasks, "inapplicable"))
        self.assertTrue(any("must run" in item for item in found), found)

    def test_run_name_needs_a_design_term(self):
        tasks = task_data()
        value = receipt(tasks)
        value["operation"] = "Review proof."
        found = invocation_problems(tasks, load_json("assets/use-case-contract.json"), value)
        self.assertTrue(any("operation" in item for item in found), found)

    def test_research_receipts_cannot_repeat_a_source(self):
        contract = copy.deepcopy(load_json("assets/use-case-contract.json"))
        contract["research_receipts"][-1]["source"] = contract["research_receipts"][0]["source"]
        found = research_problems(contract, ASPECTS)
        self.assertTrue(any("repeat" in item for item in found), found)

    def test_agent_trace_fields_cannot_repeat_one_claim(self):
        data = agent_request()
        phrase = "Fresh product design proof from the human eye."
        data["prompt"]["trace"] = {name: phrase for name in data["prompt"]["trace"]}
        with self.assertRaisesRegex(ValueError, "repeat"):
            build_envelope(data, ROOT)

    def test_agent_primitive_needs_a_named_kind(self):
        data = agent_request()
        data["primitives"][0]["kind"] = ""
        with self.assertRaisesRegex(ValueError, "kind"):
            build_envelope(data, ROOT)


if __name__ == "__main__":
    unittest.main()
