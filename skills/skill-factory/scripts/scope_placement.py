"""Consume integration-owned placement evidence without owning host conventions."""
from pathlib import Path

from skill_package import real_path
from skill_scope import load_json


def check_placement(path, scope, target):
    if not path:
        return {"kind": "authoring", "scope": scope, "destination": str(target)}
    record = load_json(path) if not isinstance(path, dict) else path
    if record.get("kind") != "installation" or record.get("scope") != scope:
        raise ValueError("installation receipt scope differs from the selected scope")
    if real_path(record["destination"]) != target or real_path(record["scope_root"]) != target.parent:
        raise ValueError("installation destination differs from the verified integration receipt")
    roots = record.get("visible_roots", [])
    if not roots or not isinstance(record.get("reference"), str) or not record["reference"].startswith("https://"):
        raise ValueError("installation needs verified host discovery roots and an owning reference")
    if str(target.parent) not in roots:
        raise ValueError("installation destination is outside the verified discovery roots")
    for root in roots:
        collision = real_path(Path(root) / target.name)
        if collision != target and collision.exists():
            raise ValueError("variant identity would shadow an available skill")
    return record
