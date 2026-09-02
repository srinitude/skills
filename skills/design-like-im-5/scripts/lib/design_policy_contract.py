"""Check design use and choice rules."""
import re

from lib.design_policy_text import text_problems, words


DECISION_FIELDS = {
    "id", "kind", "outcome", "motivation", "why_this_path", "owner",
    "inputs", "expected_effect", "proof", "falsifier", "failure_branch",
}
DECISION_TEXT = {
    "outcome", "motivation", "why_this_path", "expected_effect", "proof",
    "falsifier", "failure_branch",
}
OWNERS = {"deterministic": "mise", "model_owned": "model",
          "human_owned": "human"}


def term_problems(terms):
    if not isinstance(terms, list) or len(terms) < 3:
        return ["design terms need three clear phrases"]
    normalized = [" ".join(words(term)) for term in terms]
    if any(len(term.replace(" ", "")) < 3 for term in normalized):
        return ["a design term is too short"]
    if len(normalized) != len(set(normalized)):
        return ["design terms must not repeat"]
    return []


def dimension_problems(dimensions, expected, terms):
    if not isinstance(dimensions, dict) or set(dimensions) != expected:
        return ["design part list is not full"]
    found = []
    for name, values in dimensions.items():
        if not isinstance(values, list) or not values:
            found.append(f"design part {name} is empty")
        elif any(not any(" ".join(words(term)) in " ".join(words(value))
                         for term in terms) for value in values):
            found.append(f"design part {name} lacks a design term")
    return found


def decision_problems(decisions, terms):
    records, found, ids = decisions.get("records", []), [], []
    if not isinstance(records, list) or not records:
        return ["design choice records are empty"]
    for index, item in enumerate(records):
        if not isinstance(item, dict) or not DECISION_FIELDS <= set(item):
            found.append(f"design choice {index} lacks fields")
            continue
        ids.append(item["id"])
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item["id"]):
            found.append(f"design choice {index} has a bad id")
        if item["owner"] != OWNERS.get(item["kind"]):
            found.append(f"design choice {index} has the wrong owner")
        if not isinstance(item["inputs"], list) or not item["inputs"]:
            found.append(f"design choice {index} needs input")
        found += text_problems(item, DECISION_TEXT, terms, f"decision.{index}")
    if len(ids) != len(set(ids)):
        found.append("design choice ids must not repeat")
    return found
