"""Capture caller-supplied initial resources under the owning use-case bindings.

This orders required reading only. It neither evaluates the ledger's semantics
nor grants authority, proves model consumption or implements a domain workflow.
"""
from graphlib import CycleError, TopologicalSorter
from pathlib import Path

from agentic_request_contract import checked_file

DECLARATION_FIELDS = {"id", "role", "path", "sha256", "depends_on"}
INPUT_FIELDS = {"id", "path", "sha256"}


def indexed(items, label):
    if not isinstance(items, list) or not items:
        raise ValueError(f"{label} must be a nonempty context array")
    records = {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f"{label} context entries must be objects")
        name = item.get("id")
        if not isinstance(name, str) or not name.strip() or name in records:
            raise ValueError(f"{label} context IDs must be nonempty and unique")
        records[name] = item
    return records


def declaration_order(value):
    records = indexed(value, "initial_context")
    for name, item in records.items():
        if set(item) != DECLARATION_FIELDS or item["role"] not in ("ledger", "resource"):
            raise ValueError(f"initial_context {name} has invalid fields or role")
        path, digest = item["path"], item["sha256"]
        if not isinstance(path, str) or not path.strip():
            raise ValueError(f"initial_context {name} needs a path")
        if (not isinstance(digest, str) or len(digest) != 64
                or any(letter not in "0123456789abcdef" for letter in digest)):
            raise ValueError(f"initial_context {name} needs a full SHA-256 digest")
        dependencies = item["depends_on"]
        if (not isinstance(dependencies, list)
                or not all(isinstance(key, str) for key in dependencies)
                or len(set(dependencies)) != len(dependencies)
                or not set(dependencies) <= records.keys()):
            raise ValueError(f"initial_context {name} has invalid reading dependencies")
    if sum(item["role"] == "ledger" for item in records.values()) != 1:
        raise ValueError("initial_context requires exactly one governing ledger")
    try:
        order = tuple(TopologicalSorter({key: item["depends_on"]
                                        for key, item in records.items()}).static_order())
    except CycleError as error:
        raise ValueError("initial_context reading dependencies contain a cycle") from error
    return [records[key] for key in order]


def resource_snapshot(declared, supplied, contract_base, input_base):
    name = declared["id"]
    if set(supplied) != INPUT_FIELDS:
        raise ValueError(f"context {name} has invalid supplied fields")
    path = supplied["path"]
    if not isinstance(path, str) or not path.strip():
        raise ValueError(f"context {name} needs a supplied path")
    expected = (contract_base / declared["path"]).resolve()
    actual = (input_base / path).resolve()
    if actual != expected or supplied["sha256"] != declared["sha256"]:
        raise ValueError(f"context {name} differs from its use-case binding")
    try:
        path, digest, text = checked_file(supplied, f"context {name}", input_base)
    except (OSError, UnicodeError, ValueError) as error:
        raise ValueError(f"context {name}: {error}") from error
    if not text.strip():
        raise ValueError(f"context {name} must not be empty")
    return {"id": name, "role": declared["role"], "path": str(path),
            "sha256": digest, "text": text, "depends_on": declared["depends_on"]}


def capture_context(use_case, supplied, input_base):
    declarations = declaration_order(use_case.get("initial_context"))
    inputs = indexed(supplied, "supplied context")
    if set(inputs) != {item["id"] for item in declarations}:
        raise ValueError("supplied context must match every declared resource exactly")
    contract_base = Path(use_case["path"]).parent
    return [resource_snapshot(item, inputs[item["id"]], contract_base, input_base)
            for item in declarations]
