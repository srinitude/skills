"""Validate domain-specific agentic request data."""
import hashlib
import json
from pathlib import Path

from domain_text import uses_term

TRACE_FIELDS = ("domain_role", "outcome_contribution", "relevance",
                "expected_proof")
TASK_FIELDS = ("outcome", "motivation", "value", "proof", "applicability")
OPERATION_FIELDS = ("outcome", "motivation", "why_default_path", "proof")
SENTINEL = "SCAFFOLD-" + "PLACEHOLDER"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_file(item, label, base):
    if not isinstance(item, dict):
        raise ValueError(f"{label} must be an object")
    raw_path, expected = item.get("path"), item.get("sha256")
    if not isinstance(raw_path, str) or not raw_path:
        raise ValueError(f"{label}.path must be nonempty text")
    if not isinstance(expected, str) or len(expected) != 64:
        raise ValueError(f"{label}.sha256 must be a full digest")
    path = Path(raw_path)
    path = path if path.is_absolute() else base / path
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"{label}.path must be a regular file: {path}")
    actual = digest(path)
    if actual != expected:
        raise ValueError(f"{label} digest mismatch: {path}")
    return path.resolve(), actual


def trace_record(item, label, terms):
    if not isinstance(item, dict):
        raise ValueError(f"{label}.domain trace must be an object")
    result = {}
    for field in TRACE_FIELDS:
        value = item.get(field)
        if not isinstance(value, str) or len(value.strip()) < 20:
            raise ValueError(f"{label}.trace.{field} needs specific text")
        if not uses_term(value, terms):
            raise ValueError(f"{label}.trace.{field} needs a domain term")
        result[field] = value.strip()
    return result


def domain_fields(item, label, fields, terms):
    if not isinstance(item, dict):
        raise ValueError(f"{label} must be an object")
    result = {}
    for field in fields:
        value = item.get(field)
        if not isinstance(value, str) or len(value.strip()) < 20:
            raise ValueError(f"{label}.{field} needs specific text")
        if not uses_term(value, terms):
            raise ValueError(f"{label}.{field} needs a domain term")
        result[field] = value.strip()
    return result


def agentic_task_record(data, terms):
    graph = data.get("task_graph", {})
    tasks = graph.get("tasks", {}) if isinstance(graph, dict) else {}
    task = domain_fields(tasks.get("agentic-request"),
                         "agentic-request task", TASK_FIELDS, terms)
    operations = graph.get("public_operations", [])
    matches = [item for item in operations if isinstance(item, dict)
               and item.get("task") == "agentic-request"]
    if len(matches) != 1:
        raise ValueError("agentic-request needs one public operation")
    operation = domain_fields(matches[0], "agentic-request operation",
                              OPERATION_FIELDS, terms)
    return {"task": task, "public_operation": operation}


def use_case_record(item, base):
    path, actual = checked_file(item, "use_case", base)
    if path.name != "use-case-contract.json":
        raise ValueError("use_case.path must name use-case-contract.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    skill, outcome = data.get("skill"), data.get("outcome")
    terms = data.get("domain_terms")
    if not isinstance(skill, str) or not skill:
        raise ValueError("use-case contract needs a skill")
    if not isinstance(outcome, str) or not outcome:
        raise ValueError("use-case contract needs a promised outcome")
    if not isinstance(terms, list) or len(terms) < 3:
        raise ValueError("use-case contract needs domain terms")
    if SENTINEL in json.dumps(data):
        raise ValueError("use-case contract contains scaffold placeholders")
    if item.get("promised_outcome") != outcome:
        raise ValueError("promised outcome must match the use-case contract")
    task = agentic_task_record(data, terms)
    record = {"path": str(path), "sha256": actual, "skill": skill,
              "promised_outcome": outcome, "domain_terms": terms,
              "agentic_task": task}
    return record, terms


def prompt_record(item, base, terms):
    if not isinstance(item, dict):
        raise ValueError("prompt must be an object")
    choices = [key for key in ("text", "file") if key in item]
    if len(choices) != 1:
        raise ValueError("prompt needs exactly one of text or file")
    trace = trace_record(item.get("trace"), "prompt", terms)
    if choices[0] == "text":
        if not isinstance(item["text"], str) or not item["text"]:
            raise ValueError("prompt.text must be nonempty text")
        text = item["text"]
    else:
        path, _ = checked_file(
            {"path": item["file"], "sha256": item.get("sha256")},
            "prompt", base)
        text = path.read_text(encoding="utf-8")
    if not uses_term(text, terms):
        raise ValueError("prompt content needs a use-case domain term")
    return text, trace


def skill_records(items, base, terms):
    if not isinstance(items, list):
        raise ValueError("skills must be an array")
    records = []
    for index, item in enumerate(items):
        path, actual = checked_file(item, f"skills.{index}", base)
        if path.name != "SKILL.md":
            raise ValueError(f"skills.{index}.path must name SKILL.md")
        records.append({"path": str(path), "sha256": actual,
                        "trace": trace_record(item.get("trace"),
                                              f"skills.{index}", terms)})
    return records


def primitive_records(items, terms):
    if not isinstance(items, list):
        raise ValueError("primitives must be an array")
    records = []
    for index, item in enumerate(items):
        label = f"primitives.{index}"
        if not isinstance(item, dict):
            raise ValueError(f"{label} must be an object")
        kind, name = item.get("kind"), item.get("name")
        if not isinstance(kind, str) or not kind.strip():
            raise ValueError(f"{label}.kind must be nonempty text")
        if not isinstance(name, str) or not uses_term(name, terms):
            raise ValueError(f"{label}.name needs a domain term")
        if "configuration" not in item:
            raise ValueError(f"{label}.configuration is required")
        records.append({"kind": kind.strip(), "name": name.strip(),
                        "configuration": item["configuration"],
                        "trace": trace_record(item.get("trace"), label, terms)})
    return records


def build_envelope(data, base):
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("request must be a version 1 object")
    if "runner" in data:
        raise ValueError("request data cannot select its runner")
    use_case, terms = use_case_record(data.get("use_case"), base)
    operation = data.get("operation")
    if not isinstance(operation, str) or not uses_term(operation, terms):
        raise ValueError("operation needs a use-case domain term")
    prompt, prompt_trace = prompt_record(data.get("prompt"), base, terms)
    return {
        "version": 1, "operation": operation, "use_case": use_case,
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "prompt_trace": prompt_trace,
        "skills": skill_records(data.get("skills", []), base, terms),
        "primitives": primitive_records(data.get("primitives", []), terms),
    }
