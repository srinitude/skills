"""Shared file, hashing, and naming helpers."""
import hashlib
import json
import re
from pathlib import Path


class InputError(ValueError):
    """Bad user input that maps to exit code 2."""


class WorkflowError(RuntimeError):
    """A checked workflow failure that maps to exit code 1."""


def digest_bytes(value):
    return hashlib.sha256(value).hexdigest()


def digest_text(value):
    return digest_bytes(value.encode("utf-8"))


def digest_file(path):
    return digest_bytes(path.read_bytes())


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def load_json(path, label="JSON"):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise InputError(f"invalid {label} at {path}: {error}") from error


def at_path(value, base=None):
    if not value.startswith("@"):
        raise InputError("file references must start with @")
    path = Path(value[1:])
    if not path.is_absolute() and base:
        path = Path(base) / path
    path = path.resolve()
    if not path.is_file():
        raise InputError(f"referenced file does not exist: {path}")
    return path


def safe_slug(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "tool"


def generated_name(profile):
    identity = profile["identity"]
    parts = [identity["origin_class"], identity["provider_or_owner"],
             identity["runtime_or_server"], identity["callable_name"]]
    base = "-".join(safe_slug(item) for item in parts)
    suffix = profile["identity_hash"][:8]
    return f"{base[:55].rstrip('-')}-{suffix}"[:64].rstrip("-")


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")


def confined(root, relative):
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise InputError(f"path is outside the declared target: {relative}")
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as error:
        raise InputError(f"path escapes the declared target: {relative}") from error
    return candidate
