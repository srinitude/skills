#!/usr/bin/env python3
"""Write the public file and source link record.

Exit codes:
  0  the record was written
  1  no public files were found
  2  the input path is bad
"""
import argparse
import json
import sys
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def public_paths(root, target):
    return sorted(str(path.relative_to(root)) for path in root.rglob("*")
                  if path.is_file() and path != target
                  and "__pycache__" not in path.parts)


def mappings(paths, source_paths):
    rows = []
    extra = ["construction/case-study-ledger.json",
             "construction/simplicity-source-ledger.json",
             "construction/current-pattern-evidence.json",
             "construction/integration-matrix.json"]
    for path in paths:
        sources = [path] if path in source_paths else ["target-scaffolding"]
        if path in {"SKILL.md", "assets/simplicity-contract.json"}:
            sources.extend(item for item in extra if item in source_paths)
        rows.append({"path": path, "source_paths": sources})
    return rows


def case_ids(root):
    return [row["source_id"] for row in load(root / "evals/cases.json")["cases"]]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", help="skill folder")
    parser.add_argument("--claim-file", required=True, help="source proof file")
    args = parser.parse_args(argv)
    root = Path(args.skill_dir).resolve()
    if not root.is_dir():
        print("error: skill folder was not found", file=sys.stderr)
        return 2
    target = root / "evals" / "source-lineage.json"
    paths = public_paths(root, target)
    if not paths:
        print("blocked: no public files", file=sys.stderr)
        return 1
    source = load(args.claim_file)
    source_files = [{"path": row["source_path"], "sha256": row["sha256"]}
                    for row in source["files"]]
    data = {
        "schema_version": 1,
        "native_manifest_sha256": source["native_manifest_sha256"],
        "native_version": "2026-08-30",
        "public_version": "0.1.0",
        "source_case_ids": case_ids(root),
        "source_files": source_files,
        "public_files": mappings(paths, {row["path"] for row in source_files}),
    }
    target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(f"lineage built: {len(paths)} files, {len(source_files)} sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
