"""Check one typed Figma and Code Connect request."""
import hashlib
import json
import re
from pathlib import Path

TRACE_FIELDS = ("domain_role", "outcome_contribution", "relevance",
                "expected_proof")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def words(value):
    return re.findall(r"[a-z0-9]+", str(value).casefold())


def uses_term(value, terms):
    source = words(value)
    for term in terms:
        part = words(term)
        if part and any(source[i:i + len(part)] == part
                        for i in range(len(source) - len(part) + 1)):
            return True
    return False


def checked_file(item, label, base):
    if not isinstance(item, dict):
        raise ValueError(f"{label} needs an object")
    raw, expected = item.get("path"), item.get("sha256")
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"{label}.path needs text")
    if not isinstance(expected, str) or len(expected) != 64:
        raise ValueError(f"{label}.sha256 needs a full digest")
    path = Path(raw) if Path(raw).is_absolute() else base / raw
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"{label}.path needs a plain file")
    if digest(path) != expected:
        raise ValueError(f"{label} digest does not match")
    return path.resolve()


def trace(item, label, terms):
    if not isinstance(item, dict):
        raise ValueError(f"{label}.trace needs an object")
    result = {}
    for field in TRACE_FIELDS:
        value = item.get(field)
        if not isinstance(value, str) or not uses_term(value, terms):
            raise ValueError(f"{label}.trace.{field} needs a Figma domain term")
        result[field] = value.strip()
    if len(set(value.casefold() for value in result.values())) != len(result):
        raise ValueError(f"{label}.trace fields must not repeat one claim")
    return result


def use_case(item, base):
    path = checked_file(item, "use_case", base)
    data = json.loads(path.read_text())
    terms, outcome = data.get("domain_terms"), data.get("outcome")
    if path.name != "use-case-contract.json" or not isinstance(terms, list):
        raise ValueError("use_case must bind the Figma use case file")
    if item.get("promised_outcome") != outcome:
        raise ValueError("promised outcome must match the Figma use case")
    return {"path": str(path), "sha256": digest(path), "skill": data["skill"],
            "promised_outcome": outcome, "domain_terms": terms}, terms


def prompt(item, base, terms):
    if not isinstance(item, dict):
        raise ValueError("prompt needs an object")
    choices = [key for key in ("text", "file") if key in item]
    if len(choices) != 1:
        raise ValueError("prompt needs text or one file")
    if choices[0] == "file":
        path = checked_file({"path": item["file"],
                             "sha256": item.get("sha256")}, "prompt", base)
        value = path.read_text(encoding="utf-8")
    else:
        value = item["text"]
    if not isinstance(value, str) or not uses_term(value, terms):
        raise ValueError("prompt needs Figma domain content")
    return value, trace(item.get("trace"), "prompt", terms)


def dependencies(items, base, terms):
    if not isinstance(items, list):
        raise ValueError("skills need a list")
    result = []
    for index, item in enumerate(items):
        path = checked_file(item, f"skills.{index}", base)
        if path.name != "SKILL.md":
            raise ValueError(f"skills.{index}.path must name SKILL.md")
        result.append({"path": str(path), "sha256": digest(path),
                       "trace": trace(item.get("trace"), f"skills.{index}", terms)})
    return result


def primitives(items, terms):
    if not isinstance(items, list):
        raise ValueError("primitives need a list")
    result = []
    for index, item in enumerate(items):
        kind, name = item.get("kind"), item.get("name")
        if not isinstance(kind, str) or not kind.strip():
            raise ValueError(f"primitives.{index}.kind needs text")
        if not isinstance(name, str) or not uses_term(name, terms):
            raise ValueError(f"primitives.{index}.name needs a Figma domain term")
        result.append({"kind": kind, "name": name,
            "configuration": item.get("configuration"),
            "trace": trace(item.get("trace"), f"primitives.{index}", terms)})
    return result


def build(data, base):
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("request needs version 1")
    if "runner" in data:
        raise ValueError("request data cannot pick its runner")
    case, terms = use_case(data.get("use_case"), base)
    operation = data.get("operation")
    if not isinstance(operation, str) or not uses_term(operation, terms):
        raise ValueError("operation needs a Figma domain term")
    text, prompt_trace = prompt(data.get("prompt"), base, terms)
    return {"version": 1, "operation": operation, "use_case": case,
        "prompt": text, "prompt_sha256": hashlib.sha256(text.encode()).hexdigest(),
        "prompt_trace": prompt_trace,
        "skills": dependencies(data.get("skills", []), base, terms),
        "primitives": primitives(data.get("primitives", []), terms)}
