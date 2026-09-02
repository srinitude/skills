#!/usr/bin/env python3
"""Write the public file and source link record.

Exit codes:
  0  the record was written
  1  no public files were found
  2  the input path is bad
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packet_digest(rows):
    text = "".join(f"{row['source_path']}\0{row['sha256']}\n"
                   for row in sorted(rows, key=lambda item: item["source_path"]))
    return hashlib.sha256(text.encode()).hexdigest()


def public_paths(root, target):
    return sorted(str(path.relative_to(root)) for path in root.rglob("*")
                  if path.is_file() and path != target
                  and "__pycache__" not in path.parts)


def mappings(paths, source_paths):
    rows = []
    extra = ["construction/case-study-ledger.json",
             "construction/simplicity-source-ledger.json",
             "construction/current-pattern-evidence.json",
             "construction/integration-matrix.json",
             "construction/context-routing-meaning-ledger.json",
             "construction/context-routing-validation.json"]
    for path in paths:
        sources = [path] if path in source_paths else ["target-scaffolding"]
        if path in {"SKILL.md", "assets/simplicity-contract.json"}:
            sources.extend(item for item in extra if item in source_paths)
        rows.append({"path": path, "source_paths": sources})
    return rows


def case_ids(root):
    return [row["source_id"] for row in load(root / "evals/cases.json")["cases"]]


def skill_version(root):
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r'^\s*version:\s*["\']?([^"\'\n]+)', text, re.M)
    return match.group(1).strip() if match else ""


def repository_prefix(source, root):
    for row in source.get("files", []):
        if row.get("location_kind") != "repository":
            continue
        name = row.get("source_path", "")
        suffix = f"/{name}"
        location = row.get("location_path", "")
        if name and location.endswith(suffix):
            return location[:-len(suffix)]
    return str(root.relative_to(root.parents[1]))


def claim_document(root, target, claim_file):
    source = load(claim_file)
    kept = [row for row in source["files"]
            if row.get("location_kind") != "repository"]
    prefix = repository_prefix(source, root)
    rows = []
    for name in public_paths(root, target):
        path = root / name
        rows.append({"bytes": path.stat().st_size,
                     "location_kind": "repository",
                     "location_path": f"{prefix}/{name}",
                     "sha256": digest(path), "source_path": name})
    source["files"] = sorted(kept + rows,
                             key=lambda item: item["source_path"])
    value = packet_digest(source["files"])
    source["evidence_packet_sha256"] = value
    source["native_manifest_sha256"] = value
    return source


def claim_text(root, target, claim_file):
    data = claim_document(root, target, claim_file)
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def document(root, target, claim_file):
    paths = public_paths(root, target)
    source = load(claim_file)
    source_files = [{"path": row["source_path"], "sha256": row["sha256"]}
                    for row in source["files"]]
    data = {
        "schema_version": 1,
        "native_manifest_sha256": source["native_manifest_sha256"],
        "native_version": "2026-08-30",
        "public_version": skill_version(root),
        "source_case_ids": case_ids(root),
        "source_files": source_files,
        "public_files": mappings(paths, {row["path"] for row in source_files}),
    }
    return data, paths, source_files


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", help="skill folder")
    parser.add_argument("--claim-file", required=True, help="source proof file")
    parser.add_argument("--check", action="store_true",
                        help="fail when the saved lineage differs")
    parser.add_argument("--refresh-claim-only", action="store_true",
                        help="refresh repository baseline hashes and stop")
    return parser.parse_args(argv)


def refresh_claim(root, target, claim_file):
    text = claim_text(root, target, claim_file)
    claim_file.write_text(text, encoding="utf-8")
    count = len(load(claim_file)["files"])
    print(f"source manifest built: {count} files")


def main(argv=None):
    args = parse_args(argv)
    root = Path(args.skill_dir).resolve()
    if not root.is_dir():
        print("error: skill folder was not found", file=sys.stderr)
        return 2
    target = root / "evals" / "source-lineage.json"
    claim_file = Path(args.claim_file).resolve()
    if args.refresh_claim_only:
        refresh_claim(root, target, claim_file)
        return 0
    if args.check and claim_file.read_text(encoding="utf-8") != claim_text(
            root, target, claim_file):
        print("source manifest differs", file=sys.stderr)
        return 1
    data, paths, source_files = document(root, target, claim_file)
    if not paths:
        print("blocked: no public files", file=sys.stderr)
        return 1
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not target.is_file() or load(target) != data:
            print("source lineage differs", file=sys.stderr)
            return 1
        print(f"lineage matches: {len(paths)} files, {len(source_files)} sources")
        return 0
    target.write_text(text, encoding="utf-8")
    print(f"lineage built: {len(paths)} files, {len(source_files)} sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
