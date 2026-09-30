"""Registry attribution and source identity, independent of planning and execution."""
import hashlib
import re
from skill_package import owned_paths

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FACTORY_SOURCE = "factory/registry-standardization-profiles.json"
SCAFFOLDING_SOURCE = "target-scaffolding"


def validate_names(root, names):
    if not names:
        raise ValueError("at least one registry skill is required")
    for name in names:
        target = root / "skills" / name
        if not NAME_RE.fullmatch(name) or target.is_symlink() or not target.is_dir():
            raise ValueError(f"unknown registry skill: {name}")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def public_paths(root, skill):
    base = (root / "skills" / skill).resolve()
    return sorted(path.relative_to(base).as_posix() for path in owned_paths(base)
                  if path.relative_to(base).as_posix() != "evals/source-lineage.json")


def repository_entry(root, source_path, location_path, contents=None):
    data = (root / location_path).read_bytes() if contents is None else contents[location_path]
    return {"bytes": len(data), "location_kind": "repository",
            "location_path": location_path, "sha256": digest(data),
            "source_path": source_path}


def baseline_state(root, skill, paths, contents=None):
    entries = [repository_entry(root, path, f"skills/{skill}/{path}", contents)
               for path in paths]
    sources = [{"path": item["source_path"], "sha256": item["sha256"]}
               for item in entries]
    public = [{"path": path, "source_paths": [path]} for path in paths]
    return entries, sources, public


def refresh_repository_entry(root, entry, contents=None):
    if entry["location_kind"] != "repository":
        return entry
    return repository_entry(root, entry["source_path"], entry["location_path"], contents)


def retained_source_state(root, manifest, lineage, paths, contents=None):
    entries = [refresh_repository_entry(root, item, contents) for item in manifest["files"]
               if item["source_path"] != FACTORY_SOURCE]
    sources = [{"path": item["source_path"], "sha256": item["sha256"]}
               for item in entries]
    existing = {item["path"]: item["source_paths"]
                for item in lineage["public_files"]}
    public = []
    for path in paths:
        owners = list(existing.get(path, []))
        owners = [owner for owner in owners if owner != FACTORY_SOURCE]
        if SCAFFOLDING_SOURCE not in owners:
            owners.append(SCAFFOLDING_SOURCE)
        public.append({"path": path, "source_paths": owners})
    return entries, sources, public


def classify_source_kind(entries):
    kinds = {item["location_kind"] for item in entries}
    archived = bool(kinds & {"archive", "evidence"})
    repository = "repository" in kinds
    if archived and repository:
        return "hybrid_archived_and_repository_baseline"
    if repository:
        return "repository_baseline"
    return "archived_source"


def canonical_digest(sources):
    value = "".join(f"{item['path']}\0{item['sha256']}\n"
                    for item in sorted(sources, key=lambda item: item["path"]))
    return digest(value.encode())
