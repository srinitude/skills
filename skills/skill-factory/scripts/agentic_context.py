"""Validate initial audience declarations and capture use-case-bound resources.

This orders required reading only. It neither evaluates the ledger's semantics
nor grants authority, proves model consumption or implements a domain workflow.
Package resources retain declared paths/digests. Invocation resources are selected
by the caller only when the use-case declaration explicitly permits that binding;
every supplied resource still needs its exact current file digest.
"""
import hashlib
from graphlib import CycleError, TopologicalSorter
from pathlib import Path

from agentic_request_contract import checked_file

DECLARATION_FIELDS = {"id", "role", "path", "sha256", "depends_on"}
INVOCATION_FIELDS = {"id", "role", "binding", "depends_on"}
INPUT_FIELDS = {"id", "path", "sha256"}


def capture_body():
    """Read this dispatcher's own current body once, before request-owned context."""
    path = Path(__file__).resolve().parents[1] / "SKILL.md"
    if path.is_symlink() or not path.is_file():
        raise ValueError("package SKILL.md must be a regular file")
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    if not text.strip():
        raise ValueError("package SKILL.md must contain nonempty UTF-8 text")
    return {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "text": text}


def audience_record(data, accept=False):
    """Validate declaration shape only; preserve unresolved legacy inspection."""
    if "audience" not in data and not accept:
        return None
    audience = data.get("audience")
    if not isinstance(audience, dict) or audience.get("primary") not in ("human", "agent"):
        raise ValueError("audience.primary must explicitly be human or agent")
    secondary = audience.get("secondary", [])
    if (not isinstance(secondary, list)
            or not all(isinstance(item, str) and item.strip() for item in secondary)
            or len(secondary) != len(set(secondary))):
        raise ValueError("audience.secondary must contain unique nonempty consumer names")
    return audience


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


def check_binding(item, name):
    binding = item.get("binding", "package")
    if binding not in ("package", "invocation") or item.get("role") not in ("ledger", "resource"):
        raise ValueError(f"initial_context {name} has invalid binding or role")
    expected = INVOCATION_FIELDS if binding == "invocation" else DECLARATION_FIELDS
    if binding == "package" and "binding" in item:
        expected = expected | {"binding"}
    if set(item) != expected:
        raise ValueError(f"initial_context {name} has invalid binding fields")
    if binding == "invocation":
        return
    path, digest = item["path"], item["sha256"]
    if not isinstance(path, str) or not path.strip():
        raise ValueError(f"initial_context {name} needs a path")
    if (not isinstance(digest, str) or len(digest) != 64
            or any(letter not in "0123456789abcdef" for letter in digest)):
        raise ValueError(f"initial_context {name} needs a full SHA-256 digest")


def declaration_order(value):
    records = indexed(value, "initial_context")
    for name, item in records.items():
        check_binding(item, name)
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
    binding = declared.get("binding", "package")
    if binding == "package":
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
    return {"id": name, "role": declared["role"], "binding": binding, "path": str(path),
            "sha256": digest, "text": text, "depends_on": declared["depends_on"]}


def capture_context(use_case, supplied, input_base):
    declarations = declaration_order(use_case.get("initial_context"))
    inputs = indexed(supplied, "supplied context")
    if set(inputs) != {item["id"] for item in declarations}:
        raise ValueError("supplied context must match every declared resource exactly")
    contract_base = Path(use_case["path"]).parent
    return [resource_snapshot(item, inputs[item["id"]], contract_base, input_base)
            for item in declarations]
