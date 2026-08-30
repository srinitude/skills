#!/usr/bin/env python3
"""Check public hashes and source links.

Exit codes:
  0  all links passed
  1  one or more links failed
  2  the skill data could not be read
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packet_digest(rows):
    text = "".join(f"{row['path']}\0{row['sha256']}\n"
                   for row in sorted(rows, key=lambda item: item["path"]))
    return hashlib.sha256(text.encode()).hexdigest()


def public_files(root, target):
    return sorted(path for path in root.rglob("*") if path.is_file()
                  and path != target and "__pycache__" not in path.parts)


def skill_version(root):
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r'^\s*version:\s*["\']?([^"\'\n]+)', text, re.M)
    return match.group(1).strip() if match else None


def check_files(root, target, data):
    actual = {str(path.relative_to(root)): digest(path)
              for path in public_files(root, target)}
    public = {row["path"]: row["source_paths"] for row in data["public_files"]}
    sources = {row["path"]: row["sha256"] for row in data["source_files"]}
    issues = [f"unlisted file: {path}" for path in sorted(actual.keys() - public.keys())]
    issues += [f"missing file: {path}" for path in sorted(public.keys() - actual.keys())]
    issues += [f"stale hash: {path}" for path, value in actual.items()
               if sources.get(path) != value]
    allowed = set(sources) | {"target-scaffolding"}
    issues += [f"unknown source: {source}" for paths in public.values()
               for source in paths if source not in allowed]
    return issues


def check(root):
    target = root / "evals/source-lineage.json"
    data = json.loads(target.read_text(encoding="utf-8"))
    cases = json.loads((root / "evals/cases.json").read_text())
    mapping = json.loads((root / "evals/source-mapping.json").read_text())
    issues = check_files(root, target, data)
    if data.get("public_version") != skill_version(root):
        issues.append("public version does not match the skill")
    if data.get("native_manifest_sha256") != packet_digest(data["source_files"]):
        issues.append("source packet hash is stale")
    wanted = {row["source_id"] for row in cases["cases"]}
    if set(data.get("source_case_ids", [])) != wanted:
        issues.append("source case ids do not match eval cases")
    sources = {row["path"] for row in data["source_files"]}
    for claim in mapping["claims"]:
        if claim.get("owner_id") != "source-manifest":
            issues.append(f"{claim.get('id')}: wrong source owner")
        for path in claim.get("source_paths", []):
            if path not in sources:
                issues.append(f"{claim.get('id')}: unknown source {path}")
    return issues


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", help="skill folder")
    args = parser.parse_args(argv)
    root = Path(args.skill_dir).resolve()
    try:
        issues = check(root)
    except (OSError, json.JSONDecodeError, KeyError) as error:
        print(f"error: skill data could not be read: {error}", file=sys.stderr)
        return 2
    for issue in issues:
        print(issue)
    print(f"source lineage check: {len(issues)} problems")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
