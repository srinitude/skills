"""Check standalone DTCG use-case and decision record semantics."""
import re

from lib.token_policy_text import text_problems, words


DECISION_FIELDS = {"id", "kind", "outcome", "motivation", "why_this_path",
                   "owner", "inputs", "expected_effect", "proof",
                   "falsifier", "failure_branch"}
DECISION_TEXT = {"outcome", "motivation", "why_this_path", "expected_effect",
                 "proof", "falsifier", "failure_branch"}
OWNERS = {"deterministic": "mise", "model_owned": "model",
          "human_owned": "human"}


def term_problems(terms):
    if not isinstance(terms, list) or len(terms) < 3:
        return ["DTCG token domain terms need three specific phrases"]
    normalized = [" ".join(words(term)) for term in terms]
    if any(len(term.replace(" ", "")) < 3 for term in normalized):
        return ["DTCG token domain terms contain an underspecified phrase"]
    if len(normalized) != len(set(normalized)):
        return ["DTCG token domain terms must be unique"]
    return []


def dimension_problems(dimensions, expected, terms):
    if not isinstance(dimensions, dict) or set(dimensions) != expected:
        return ["DTCG token aspect inventory is incomplete"]
    found = []
    for name, values in dimensions.items():
        if not isinstance(values, list) or not values:
            found.append(f"DTCG token domain dimension {name} is empty")
            continue
        if any(not any(" ".join(words(term)) in " ".join(words(value))
                       for term in terms) for value in values):
            found.append(f"DTCG token domain dimension {name} lacks a token term")
    return found


def decision_problems(decisions, terms):
    records, found, ids = decisions.get("records", []), [], []
    if not isinstance(records, list) or not records:
        return ["DTCG token decision records are empty"]
    for index, item in enumerate(records):
        if not isinstance(item, dict) or not DECISION_FIELDS <= set(item):
            found.append(f"DTCG token decision {index} is incomplete")
            continue
        ids.append(item["id"])
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", item["id"]):
            found.append(f"DTCG token decision {index} has an invalid id")
        if item["owner"] != OWNERS.get(item["kind"]):
            found.append(f"DTCG token decision {index} has the wrong owner")
        if not isinstance(item["inputs"], list) or not item["inputs"]:
            found.append(f"DTCG token decision {index} needs inputs")
        found += text_problems(item, DECISION_TEXT, terms, f"decision.{index}")
    if len(ids) != len(set(ids)):
        found.append("DTCG token decision ids must be unique")
    return found
