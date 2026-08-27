"""Atomic JSON and hash helpers for the execution pipeline."""
import hashlib
import json
import os
import pathlib
import tempfile


class PipelineError(ValueError):
    """A user-correctable run-state error."""


def load_json(path: pathlib.Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise PipelineError(f"missing file: {path}") from error
    except json.JSONDecodeError as error:
        raise PipelineError(f"invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise PipelineError(f"expected one JSON object in {path}")
    return value


def file_hash(path: pathlib.Path) -> str:
    if not path.is_file():
        raise PipelineError(f"missing input file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def group_record(paths: list[pathlib.Path]) -> dict:
    if not paths:
        raise PipelineError("at least one path is required")
    records = [{"path": str(path), "sha256": file_hash(path)} for path in paths]
    digest = hashlib.sha256()
    for record in records:
        digest.update(record["path"].encode("utf-8"))
        digest.update(b"\0")
        digest.update(record["sha256"].encode("ascii"))
        digest.update(b"\0")
    return {"paths": records, "sha256": digest.hexdigest()}


def save_json(path: pathlib.Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=False) + "\n"
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
