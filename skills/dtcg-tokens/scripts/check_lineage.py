#!/usr/bin/env python3
"""Check or refresh the package source-lineage record.

Usage:
  python3 scripts/check_lineage.py [skill-root] [--write]

Exit codes:
  0  lineage is current, or refresh succeeded
  1  lineage is stale or invalid
  2  bad usage

Example:
  python3 scripts/check_lineage.py . --write
"""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

LINEAGE = "evals/source-lineage.json"
SKIP_PARTS = {".git", "__pycache__"}
VERSION_RE = re.compile(r'^\s*version:\s*["\']([^"\']+)["\']\s*$', re.M)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.relative_to(root).as_posix() != LINEAGE
        and not SKIP_PARTS.intersection(path.parts)
    )


def version(root):
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    match = VERSION_RE.search(text)
    if not match:
        raise ValueError("SKILL.md has no quoted metadata version")
    return match.group(1)


def refreshed(root, current):
    paths = inventory(root)
    routes = {item["path"]: item.get("source_paths", [item["path"]])
              for item in current.get("public_files", [])}
    current["public_version"] = version(root)
    current["public_files"] = [
        {"path": path, "source_paths": routes.get(path, ["target-scaffolding"])}
        for path in paths
    ]
    source_paths = [item["path"] for item in current.get("source_files", [])]
    if "SKILL.md" not in source_paths:
        source_paths.append("SKILL.md")
    current["source_files"] = [
        {"path": path, "sha256": digest(root / path)}
        for path in sorted(source_paths) if (root / path).is_file()
    ]
    return current


def problems(root, current):
    found = []
    if current.get("public_version") != version(root):
        found.append("public_version differs from SKILL.md")
    actual = sorted(item.get("path") for item in current.get("public_files", []))
    if actual != inventory(root):
        found.append("public file inventory is stale")
    for item in current.get("source_files", []):
        path = root / item.get("path", "")
        if not path.is_file() or item.get("sha256") != digest(path):
            found.append(f"source hash is stale: {item.get('path', '<missing>')}")
    return found


def write_atomic(path, document):
    payload = json.dumps(document, indent=2) + "\n"
    with tempfile.NamedTemporaryFile(
            "w", dir=path.parent, delete=False, encoding="utf-8") as handle:
        handle.write(payload)
        temporary = handle.name
    os.replace(temporary, path)


def report(root, write):
    path = root / LINEAGE
    current = json.loads(path.read_text(encoding="utf-8"))
    if write:
        write_atomic(path, refreshed(root, current))
        return {"status": "PASS", "mode": "write", "files": len(inventory(root))}
    found = problems(root, current)
    return {"status": "PASS" if not found else "FAIL", "mode": "check",
            "files": len(inventory(root)), "problems": found}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill_root", nargs="?", default=".")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.skill_root).resolve()
    try:
        result = report(root, args.write)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        result = {"status": "FAIL", "problems": [str(error)]}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
