#!/usr/bin/env python3
"""Check that each public file has a real use.

Exit codes:
  0  each file has a named use
  1  one or more files failed
  2  the skill path is bad
"""
import argparse
import json
import sys
from pathlib import Path

SKIP = {"__pycache__", ".DS_Store"}


def files(root):
    return {str(path.relative_to(root)) for path in root.rglob("*")
            if path.is_file() and not any(part in SKIP for part in path.parts)}


def check(root):
    path = root / "assets" / "file-manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("files", [])
    listed = {row.get("path") for row in rows}
    actual = files(root)
    issues = [f"unlisted file: {name}" for name in sorted(actual - listed)]
    issues += [f"missing file: {name}" for name in sorted(listed - actual)]
    for row in rows:
        name = row.get("path", "missing path")
        for key in ["role", "purpose", "consumer", "load_trigger",
                    "source", "version", "output_effect"]:
            if not row.get(key):
                issues.append(f"{name}: {key} is missing")
        if name.startswith("references/") and name.count("/") > 1:
            issues.append(f"{name}: reference path is too deep")
        if row.get("mutable"):
            issues.append(f"{name}: public files must not hold run state")
    return issues


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", help="skill folder")
    args = parser.parse_args(argv)
    root = Path(args.skill_dir).resolve()
    try:
        issues = check(root)
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: file data could not be read: {error}", file=sys.stderr)
        return 2
    for issue in issues:
        print(issue)
    print(f"directory check: {len(issues)} problems")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
