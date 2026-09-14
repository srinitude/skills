"""Current source and project evidence for a digest-bound adaptation."""
from pathlib import Path

from skill_package import inventory, tree_digest
from skill_scope import read_fields

PROJECT_FACTS = {"instructions", "structure", "tools", "commands", "configuration", "constraints"}


def project_files(project, target, staging=None, excluded_paths=()):
    root = Path(project["root"])
    excluded = [path.relative_to(root).as_posix() for path in [target, staging, *excluded_paths]
                if path is not None and path.is_relative_to(root)]
    return {key: value for key, value in inventory(root).items()
            if not any(key == prefix or key.startswith(prefix + "/") for prefix in excluded)}


def check_current(plan, staging=None, source_root=None, excluded_paths=()):
    source = plan["source"]
    if source_root is not None and not plan["in_place"]:
        raise ValueError("a retained source is valid only for explicit in-place verification")
    source_root = Path(source_root) if source_root is not None else Path(source["root"])
    if inventory(source_root) != source["files"]:
        raise ValueError("source changed since planning; create a fresh plan")
    if tree_digest(source["files"]) != source["digest"]:
        raise ValueError("source digest does not match its inventory")
    metadata = read_fields(source_root).get("metadata", {})
    if metadata.get("scope") and metadata["scope"] != source["scope"]:
        raise ValueError("source scope differs from the immutable baseline")
    if metadata.get("version", "unversioned") != source["version"]:
        raise ValueError("source version differs from its package")
    project = plan["project"]
    if project:
        if not project["files"] or tree_digest(project["files"]) != project["digest"]:
            raise ValueError("project context needs a complete digest-bound inventory")
        if project_files(project, Path(plan["target"]["path"]), staging, excluded_paths) != project["files"]:
            raise ValueError("project context changed since planning")


def check_project_review(plan, review):
    context = review.get("project_review")
    project = plan["project"]
    if not project:
        if context is not None:
            raise ValueError("a user variant must not retain a project_review binding")
        return
    if not isinstance(context, dict) or context.get("digest") != project["digest"]:
        raise ValueError("project_review must bind the declared project digest")
    if set(context.get("coverage", {})) != set(project["files"]):
        raise ValueError("project_review must cover the complete relevant project context")
    facts = context.get("facts", {})
    if set(facts) != PROJECT_FACTS or not all(isinstance(x, str) and x.strip() for x in facts.values()):
        raise ValueError("project_review needs instructions, structure, tools, commands, configuration, and constraints")
