#!/usr/bin/env python3
"""Check or refresh this skill's source-lineage record.

Usage:
  python3 scripts/check_lineage.py [SKILL_DIR] [--write]

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

SELF = Path(__file__).resolve().parents[1]
LINEAGE = "evals/source-lineage.json"
SKIP_PARTS = {".git", ".mise", "__pycache__", "node_modules",
              ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SKIP_NAMES = {".DS_Store"}
VERSION_RE = re.compile(r'^\s*version:\s*["\']([^"\']+)["\']\s*$', re.M)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def files(root):
    found = []
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if path.is_file() and not path.is_symlink() and relative != LINEAGE:
            if (not SKIP_PARTS.intersection(path.parts)
                    and path.name not in SKIP_NAMES
                    and path.suffix not in {".pyc", ".pyo"}):
                found.append(relative)
    return sorted(found)


def symlink_paths(root):
    return sorted(path.relative_to(root).as_posix()
                  for path in root.rglob("*") if path.is_symlink())


def version(root):
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    match = VERSION_RE.search(text)
    if not match:
        raise ValueError("SKILL.md has no quoted metadata version")
    return match.group(1)


def case_ids(root):
    data = json.loads((root / "evals/cases.json").read_text(encoding="utf-8"))
    return [item["source_id"] for item in data["cases"]]


def current_document(root):
    paths = files(root)
    sources = [{"path": path, "sha256": digest((root / path).read_bytes())}
               for path in paths]
    packet = "".join(f"{x['path']}\0{x['sha256']}\n" for x in sources)
    release = version(root)
    return {"schema_version": 1, "public_version": release,
            "native_version": release,
            "native_manifest_sha256": digest(packet.encode()),
            "public_files": [{"path": path, "source_paths": [path]}
                             for path in paths],
            "source_files": sources, "source_case_ids": case_ids(root)}


def write_atomic(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(document, indent=2) + "\n"
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False,
                                     encoding="utf-8") as handle:
        handle.write(payload)
        temporary = handle.name
    os.replace(temporary, path)


def report(root, write=False):
    path = root / LINEAGE
    links = symlink_paths(root)
    if links:
        return {"status": "FAIL", "mode": "write" if write else "check",
                "files": len(files(root)),
                "problems": ["symlinks are not portable: " + ", ".join(links)]}
    expected = current_document(root)
    if write:
        write_atomic(path, expected)
        return {"status": "PASS", "mode": "write", "files": len(files(root))}
    try:
        actual = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {"status": "FAIL", "problems": [str(error)]}
    problems = [] if actual == expected else ["source-lineage.json is stale"]
    if actual.get("public_version") != expected["public_version"]:
        problems.append("public_version differs from SKILL.md")
    return {"status": "PASS" if not problems else "FAIL",
            "mode": "check", "files": len(files(root)), "problems": problems}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill_dir", nargs="?", default=str(SELF))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    candidate = Path(args.skill_dir)
    if candidate.is_symlink():
        result = {"status": "FAIL", "problems": ["skill root is a symlink"]}
        print(json.dumps(result, sort_keys=True))
        return 1
    root = candidate.resolve()
    if not root.is_dir():
        print(json.dumps({"status": "FAIL", "problems": ["not a directory"]}))
        return 1
    try:
        result = report(root, args.write)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        result = {"status": "FAIL", "problems": [str(error)]}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
