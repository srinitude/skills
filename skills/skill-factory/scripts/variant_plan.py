"""Digest-bound plans for independently maintained skill variants."""
import re
from pathlib import Path
from urllib.parse import urlsplit

from skill_package import content_files, inventory, real_path, sha, tree_digest
from skill_scope import SCOPES, load_json, read_fields, resolve
from scope_placement import check_placement


def identity(value):
    if not value or not isinstance(value, str) or any(c.isspace() for c in value):
        raise ValueError("identity must be nonempty portable text")
    url = urlsplit(value)
    if (value.startswith(("/", "~", ".")) or "\\" in value or url.username
            or url.password or url.query or url.fragment or url.scheme == "file"
            or re.match(r"^[A-Za-z]:/", value)):
        raise ValueError("identity must not contain local paths, credentials, or query data")
    return value


def opaque_files(files):
    return {sha(path.encode()): value for path, value in files.items()}


def changed(baseline, current):
    return sorted(key for key in set(baseline) | set(current)
                  if baseline.get(key) != current.get(key))


def source_record(args):
    root = real_path(args.source)
    fields = read_fields(root)
    existing = fields.get("metadata", {}).get("scope")
    if existing and args.source_scope and existing != args.source_scope:
        raise ValueError("source scope cannot be relabeled during variant creation")
    scope = resolve(existing, args.source_scope)["scope"]
    files = inventory(root)
    return {"root": str(root), "requested_root": str(Path(args.source).absolute()),
            "identity": identity(args.source_id),
            "name": fields["name"], "scope": scope,
            "version": fields.get("metadata", {}).get("version", "unversioned"),
            "files": files, "digest": tree_digest(files)}


def project_record(args, target):
    if args.scope != "project":
        if args.project or args.project_id:
            raise ValueError("a user variant must not bind a target project")
        return None
    if not args.project or not args.project_id:
        raise ValueError("Which target project should this project-level skill fit?")
    root = real_path(args.project)
    files = inventory(root)
    if not files:
        raise ValueError("project context is empty; retrieve instructions, structure, tools, and configuration")
    if target.is_relative_to(root) and target.exists():
        prefix = target.relative_to(root).as_posix() + "/"
        files = {key: value for key, value in files.items() if not key.startswith(prefix)}
    return {"root": str(root), "identity": identity(args.project_id),
            "files": files, "digest": tree_digest(files)}


def refresh_record(source, target):
    prior = load_json(target / "evals/source-lineage.json").get("derivation")
    if not prior or prior["source"]["identity"] != source["identity"]:
        raise ValueError("refresh source differs from recorded source identity")
    if prior["source"]["scope"] != source["scope"]:
        raise ValueError("refresh source scope changed; resolve the adaptation before refreshing")
    source_changes = changed(prior["source"]["baseline"], opaque_files(source["files"]))
    current = content_files(target)
    customizations = changed(prior["target_baseline"], current)
    conflicts = [path for path in customizations if sha(path.encode()) in source_changes]
    return {"prior": prior, "target_files": inventory(target),
            "source_changes": source_changes, "customizations": customizations,
            "conflicts": conflicts}


def make_plan(args):
    source = source_record(args)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.name) or len(args.name) > 64:
        raise ValueError("variant name must use portable kebab-case")
    parent = real_path(args.dest)
    if not parent.is_dir():
        raise ValueError("destination parent is missing")
    target = real_path(parent / args.name)
    original = Path(source["root"])
    if args.in_place and (target != original or args.refresh):
        raise ValueError("in-place requires the source destination and cannot be a refresh")
    if not args.in_place and (args.name == source["name"] or target.is_relative_to(original)
                              or original.is_relative_to(target)):
        raise ValueError("variant identity or destination would overwrite or shadow its source")
    if args.scope == source["scope"]:
        raise ValueError("variant target scope must differ from source scope")
    if target.exists() and not (args.refresh or args.in_place):
        raise ValueError("destination collision; use the original accept plan for a safe rerun")
    refresh = refresh_record(source, target) if args.refresh else None
    if refresh and read_fields(target).get("metadata", {}).get("scope") != args.scope:
        raise ValueError("refresh must preserve the target scope")
    result = {"schema_version": 1, "operation": "refresh" if args.refresh else "variant",
              "source": source, "target": {"name": args.name, "scope": args.scope,
              "path": str(target)}, "project": project_record(args, target),
              "in_place": args.in_place, "refresh": refresh, "writes": 0}
    result["placement"] = check_placement(args.placement_receipt, args.scope, target)
    return result


def validate_plan(plan):
    source, target = plan["source"], plan["target"]
    if plan.get("schema_version") != 1 or type(plan.get("in_place")) is not bool:
        raise ValueError("invalid variant plan schema")
    if source["scope"] not in SCOPES or target["scope"] not in SCOPES or source["scope"] == target["scope"]:
        raise ValueError("invalid variant plan scopes")
    if plan["operation"] not in {"variant", "refresh"}:
        raise ValueError("invalid variant operation")
    if bool(plan["refresh"]) != (plan["operation"] == "refresh"):
        raise ValueError("refresh requires a recorded baseline comparison")
    original, destination = real_path(source["root"]), real_path(target["path"])
    if destination.name != target["name"] or source["name"] != read_fields(original)["name"]:
        raise ValueError("variant plan identity differs from its package")
    if plan["in_place"] and (original != destination or plan["refresh"]):
        raise ValueError("invalid in-place target")
    if not plan["in_place"] and (destination.is_relative_to(original)
                                or original.is_relative_to(destination)
                                or source["name"] == target["name"]):
        raise ValueError("variant would overwrite or shadow its source")
    if bool(plan["project"]) != (target["scope"] == "project"):
        raise ValueError("project scope requires target project context")
    identity(source["identity"])
    if plan["project"]:
        identity(plan["project"]["identity"])
    if plan["refresh"] and refresh_record(source, destination) != plan["refresh"]:
        raise ValueError("refresh comparison no longer matches the recorded baseline")
