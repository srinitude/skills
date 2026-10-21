"""Prepare an unaccepted review and save operation artifacts outside packages."""
import json
import os
import tempfile
from pathlib import Path

from skill_package import inventory, real_path, tree_digest
from skill_scope import load_json
from variant_context import PROJECT_FACTS, check_current
from variant_plan import validate_plan


def draft(plan, candidate):
    validate_plan(plan)
    check_current(plan)
    files = inventory(real_path(candidate))
    result = {"source_digest": plan["source"]["digest"], "candidate_digest": tree_digest(files),
              "coverage": coverage(plan["source"]["files"]), "adaptations": [],
              "requirements": [], "compatibility": "", "privacy_review": "",
              "independence_review": "", "forbidden_strings": [],
              "resolutions": {}, "metadata_changes": {}, "scenarios": []}
    if plan["project"]:
        result["project_review"] = {"digest": plan["project"]["digest"],
            "coverage": coverage(plan["project"]["files"]),
            "facts": {key: "" for key in sorted(PROJECT_FACTS)}}
    return result


def coverage(files):
    return {name: {"disposition": "reviewed", "reason": ""} for name in files}


def write_atomic(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(document, indent=2) + "\n"
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False,
                                     encoding="utf-8") as handle:
        handle.write(payload)
        temporary = handle.name
    os.replace(temporary, path)


def save_output(path, result, plan, candidate=None):
    destination = real_path(path)
    roots = [plan["source"]["root"], plan["target"]["path"]]
    if plan["project"]:
        roots.append(plan["project"]["root"])
    if candidate:
        roots.append(candidate)
    if any(destination.is_relative_to(real_path(root)) for root in roots):
        raise ValueError("operation artifacts must stay outside source, candidate, target, and project")
    if destination.exists():
        if load_json(destination) != result:
            raise ValueError("operation artifact destination already contains different content")
        return
    write_atomic(destination, result)
