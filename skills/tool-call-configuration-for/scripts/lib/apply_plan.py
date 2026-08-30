"""Apply one checked integration plan with stale checks and rollback."""
import json
import re
import subprocess
from pathlib import Path

from common import (InputError, WorkflowError, at_path, confined, digest_file,
                    load_json, write_json)
from lineage import lineage_satisfied, update_lineage


def resolve_target(value, skills_root):
    root = Path(skills_root).resolve()
    raw = Path(value)
    candidate = raw if raw.is_absolute() or "/" in value else root / value
    if candidate.is_symlink():
        raise InputError(f"target is a symlink: {candidate}")
    target = candidate.resolve()
    try:
        target.relative_to(root)
    except ValueError as error:
        raise InputError(f"target is outside skills root: {target}") from error
    if not (target / "SKILL.md").is_file():
        raise InputError(f"target has no SKILL.md: {target}")
    return target


def load_plan(value, tool, behavior):
    plan = load_json(at_path(value), "integration plan")
    if plan.get("schema") != "tool-call-config/integration-plan/v1":
        raise InputError("integration plan has the wrong schema")
    if plan.get("tool_identity_hash") != tool["identity_hash"]:
        raise InputError("integration plan tool identity does not match")
    if plan.get("behavior_hash") != behavior["behavior_hash"]:
        raise InputError("integration plan behavior does not match")
    return plan


def marker(operation):
    value = operation.get("marker")
    return f"<!-- tccf:{value}:start -->" if value else None


def operation_satisfied(target, operation):
    path = confined(target, operation["path"])
    if operation["kind"] == "add":
        return path.is_file() and path.read_text(encoding="utf-8") == operation["content"]
    if operation["kind"] in {"insert_before", "insert_after"}:
        return path.is_file() and marker(operation) in path.read_text(encoding="utf-8")
    if operation["kind"] == "replace_text":
        return path.is_file() and operation["new"] in path.read_text(encoding="utf-8")
    if operation["kind"] == "json_append":
        return json_value_present(path, operation)
    raise InputError(f"unknown operation kind: {operation['kind']}")


def json_value_present(path, operation):
    if not path.is_file():
        return False
    value = load_json(path)
    for key in operation["keys"]:
        value = value[key]
    return operation["value"] in value


def stale_paths(target, expected):
    stale = []
    for relative, wanted in expected.items():
        path = confined(target, relative)
        actual = digest_file(path) if path.is_file() else None
        if actual != wanted:
            stale.append(relative)
    return stale


def snapshot(target, declared):
    saved = {}
    for relative in declared:
        path = confined(target, relative)
        saved[relative] = path.read_bytes() if path.is_file() else None
    return saved


def restore(target, saved):
    for relative, content in saved.items():
        path = confined(target, relative)
        if content is None and path.exists():
            path.unlink()
        elif content is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)


def insert_text(text, operation):
    anchor = operation["anchor"]
    if text.count(anchor) != 1:
        raise WorkflowError(f"anchor must occur once: {anchor}")
    start = marker(operation)
    block = f"{start}\n{operation['content']}<!-- tccf:{operation['marker']}:end -->\n\n"
    if operation["kind"] == "insert_before":
        return text.replace(anchor, block + anchor, 1)
    return text.replace(anchor, anchor + "\n\n" + block.rstrip(), 1)


def apply_operation(target, operation):
    path = confined(target, operation["path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    kind = operation["kind"]
    if kind == "add":
        path.write_text(operation["content"], encoding="utf-8")
        return
    if kind in {"insert_before", "insert_after"}:
        text = path.read_text(encoding="utf-8")
        path.write_text(insert_text(text, operation), encoding="utf-8")
        return
    if kind == "replace_text":
        replace_text(path, operation)
        return
    if kind == "json_append":
        append_json(path, operation)
        return
    raise InputError(f"unknown operation kind: {kind}")


def replace_text(path, operation):
    text = path.read_text(encoding="utf-8")
    if text.count(operation["old"]) != operation.get("count", 1):
        raise WorkflowError(f"replacement count changed in {operation['path']}")
    path.write_text(text.replace(operation["old"], operation["new"],
                                 operation.get("count", 1)), encoding="utf-8")


def append_json(path, operation):
    value = load_json(path)
    parent = value
    for key in operation["keys"]:
        parent = parent[key]
    if operation["value"] not in parent:
        parent.append(operation["value"])
    write_json(path, value)


def run_validation(target, commands):
    records = []
    for command in commands:
        if not isinstance(command, list) or not command:
            raise InputError("validation commands must be non-empty argv arrays")
        result = subprocess.run(command, cwd=target, capture_output=True,
                                text=True, timeout=300)
        records.append({"argv": command, "exit_code": result.returncode,
                        "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode:
            raise WorkflowError(json.dumps(records))
    return records


def file_hashes(target, declared):
    return {name: digest_file(confined(target, name))
            if confined(target, name).is_file() else None for name in declared}


def apply(target, plan):
    operations = plan.get("operations", [])
    declared = plan.get("declared_files", [])
    touched = {item.get("path") for item in operations}
    if not operations or not touched <= set(declared):
        raise InputError("operations must stay inside declared_files")
    lineage = plan.get("lineage")
    if (all(operation_satisfied(target, item) for item in operations)
            and lineage_satisfied(target, lineage)):
        return {"status": "no-op", "target": str(target),
                "changed_files": [], "post_hashes": file_hashes(target, declared)}
    stale = stale_paths(target, plan.get("expected_hashes", {}))
    if stale:
        raise WorkflowError("stale plan for: " + ", ".join(stale))
    saved = snapshot(target, declared)
    pre = file_hashes(target, declared)
    try:
        for operation in operations:
            if not operation_satisfied(target, operation):
                apply_operation(target, operation)
        update_lineage(target, lineage)
        records = run_validation(target, plan.get("validation_commands", []))
    except Exception as error:
        restore(target, saved)
        raise WorkflowError(f"validation failed; rolled back: {error}") from error
    return {"status": "applied", "target": str(target),
            "changed_files": sorted(touched), "pre_hashes": pre,
            "post_hashes": file_hashes(target, declared), "validation": records,
            "dispositions": plan.get("dispositions", [])}
