"""Consume caller-bound matrix records at the existing policy boundary.

These checks prove input identity and record use, never semantic or human acceptance.
"""
import json
import subprocess
from pathlib import Path

from human_matrix_records import identifiers, references, shape
from skill_package import inventory, tree_digest
from source_coverage import bound_bytes, parse_json, require

TASKS = {"domain-research-policy", "use-case-policy", "decision-policy", "evals"}
FIELDS = {"framing", "challenge", "criteria", "assessment"}


def arguments(parser):
    parser.add_argument("--human-context", help="explicit matrix resource and consumer bindings")
    parser.add_argument("--human-context-sha256", help="caller-bound digest of those exact bindings")


def snapshot(root):
    return tree_digest(inventory(root))


def resource(base, binding, label):
    shape(binding, {"path", "sha256"}, label)
    require(isinstance(binding["path"], str) and bool(binding["path"]), label + " needs a path")
    path = Path(binding["path"])
    path = path if path.is_absolute() else base / path
    raw = bound_bytes(path, binding["sha256"], label)
    return path, raw


def context(args):
    require(bool(args.human_context) and bool(args.human_context_sha256),
            "human matrix use requires --human-context and --human-context-sha256")
    path = Path(args.human_context).absolute()
    raw = bound_bytes(path, args.human_context_sha256, "human context")
    value = parse_json(raw)
    shape(value, {"version", "resources", "matrix", "uses"}, "human context")
    require(type(value["version"]) is int and value["version"] == 1, "unsupported human context version")
    require(isinstance(value["uses"], dict) and set(value["uses"]) <= TASKS, "invalid matrix consumer mapping")
    identifiers(list(value["uses"].values()), "matrix consumer record")
    resources, _ = resource(path.parent, value["resources"], "human resources")
    matrix, _ = resource(path.parent, value["matrix"], "human matrix")
    return value, resources, matrix


def consume(result, record, task, subject):
    require(isinstance(result, dict) and result.get("acceptance") == "pending", "invalid matrix workflow result")
    records = result["records"]
    references([record], records, "matrix consumer")
    use = records[record]
    shape(use, FIELDS | {"task", "subject_sha256", "interactions"}, "matrix use")
    require(use["task"] == task, "matrix use belongs to another task")
    require(use["subject_sha256"] == subject, "matrix use subject differs from the checked artifact")
    interactions = {item["id"]: item for item in result["matrix"]["interactions"]}
    references(use["interactions"], interactions, "matrix use interaction")
    require(bool(use["interactions"]), "matrix use needs its relevant interaction selection")
    for name in use["interactions"]:
        require(bool(interactions[name]["study"]) and bool(interactions[name]["work"]),
                "matrix use needs both study and work selections")
    selected = {}
    for field in sorted(FIELDS):
        references(use[field], records, "matrix use " + field)
        require(bool(use[field]), "matrix use needs " + field + " records")
        selected[field] = [records[name] for name in use[field]]
        require(all(value is not None and value != "" and value != [] and value != {}
                    for value in selected[field]), "empty matrix use " + field)
    return {**use, **selected, "coverage": result["coverage"], "acceptance": "pending"}


def check(args, root, task, before):
    value, resources, matrix = context(args)
    require(task in value["uses"], "human context has no use for " + task)
    require((root / "assets/human-catalogs.json").is_file(), "checked skill lacks its matrix inventory")
    script = root / "scripts/human-matrix-workflow.ts"
    require(script.is_file(), "checked skill lacks its declared matrix workflow")
    command = ["node", str(script), "--resources", str(resources), "--matrix", str(matrix),
               "--matrix-sha256", value["matrix"]["sha256"]]
    process = subprocess.run(command, capture_output=True, text=True, timeout=120)
    require(process.returncode == 0, "human matrix workflow failed: " + process.stderr.strip())
    result = parse_json(process.stdout.encode())
    require(result["implementation"] == before, "matrix workflow belongs to another checked artifact")
    use = consume(result, value["uses"][task], task, before)
    require(context(args)[0] == value and tree_digest(inventory(root)) == before,
            "human matrix inputs or checked artifact changed during use")
    print(json.dumps({"human_matrix_use": {**use, "context_sha256": args.human_context_sha256,
                                          "matrix_sha256": result["matrix_sha256"]}}))


def problems(args, root, task, before):
    try:
        check(args, root, task, before)
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        return ["human matrix use: " + str(error)]
    return []
