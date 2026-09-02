#!/usr/bin/env python3
"""Refresh source lineage for named registry skills."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from standardization_format import format_files, format_target

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FACTORY_SOURCE = "factory/registry-standardization-profiles.json"
SCAFFOLDING_SOURCE = "target-scaffolding"


def repository_root():
    return Path(__file__).resolve().parents[3]


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
    base, found = root / "skills" / skill, []
    for path in base.rglob("*"):
        if "__pycache__" in path.parts or path.is_dir():
            continue
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"unsupported public entry: {path.relative_to(base)}")
        relative = path.relative_to(base).as_posix()
        if relative != "evals/source-lineage.json":
            found.append(relative)
    return sorted(found)


def repository_entry(root, source_path, location_path):
    data = (root / location_path).read_bytes()
    return {"bytes": len(data), "location_kind": "repository",
            "location_path": location_path, "sha256": digest(data),
            "source_path": source_path}


def baseline_state(root, skill, paths):
    entries = [repository_entry(root, path, f"skills/{skill}/{path}")
               for path in paths]
    sources = [{"path": item["source_path"], "sha256": item["sha256"]}
               for item in entries]
    public = [{"path": path, "source_paths": [path]} for path in paths]
    return entries, sources, public


def refresh_repository_entry(root, entry):
    if entry["location_kind"] != "repository":
        return entry
    return repository_entry(root, entry["source_path"], entry["location_path"])


def retained_source_state(root, manifest, lineage, paths):
    entries = [refresh_repository_entry(root, item) for item in manifest["files"]
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


def write_json(path, data):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def refresh_skill(root, skill):
    skill_root = root / "skills" / skill
    format_target(skill_root)
    lineage_path = skill_root / "evals/source-lineage.json"
    manifest_path = root / f"evidence/ports/{skill}/source-manifest.json"
    lineage = json.loads(lineage_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    paths = public_paths(root, skill)
    if manifest["source_kind"] == "repository_baseline":
        entries, sources, public = baseline_state(root, skill, paths)
        current = canonical_digest(sources)
        lineage["native_manifest_sha256"] = current
        manifest["native_manifest_sha256"] = current
    else:
        entries, sources, public = retained_source_state(
            root, manifest, lineage, paths)
        manifest["source_kind"] = classify_source_kind(entries)
    lineage.update({"source_files": sources, "public_files": public})
    manifest.update({"files": entries,
                     "evidence_packet_sha256": canonical_digest(sources)})
    write_json(lineage_path, lineage)
    write_json(manifest_path, manifest)
    format_files(skill_root, (lineage_path, manifest_path))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skills", nargs="+")
    args = parser.parse_args(argv)
    root = repository_root()
    try:
        validate_names(root, args.skills)
        for skill in args.skills:
            refresh_skill(root, skill)
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(f"registry lineage: PASS ({len(args.skills)} skills)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
