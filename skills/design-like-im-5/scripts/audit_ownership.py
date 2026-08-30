#!/usr/bin/env python3
"""Check one owner for each work step.

Exit codes:
  0  each step has one valid owner
  1  one or more steps failed
  2  the skill path is bad
"""
import argparse
import json
import sys
from pathlib import Path

OWNERS = {"script", "model", "human"}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(root):
    data = load(root / "assets" / "execution-ownership.json")
    flow = load(root / "assets" / "workflow.json")
    issues = []
    rows = data.get("actions", [])
    by_id = {row.get("id"): row for row in rows}
    if len(by_id) != len(rows):
        issues.append("action ids must be unique")
    for step in flow.get("steps", []):
        row = by_id.get(step.get("action"))
        if not row:
            issues.append(f"{step.get('action')}: no owner")
            continue
        check_row(row, root, issues)
    extra = set(by_id) - {step.get("action") for step in flow.get("steps", [])}
    for name in sorted(extra):
        issues.append(f"{name}: not in the work flow")
    return issues


def check_row(row, root, issues):
    name, owner = row.get("id"), row.get("owner")
    if owner not in OWNERS:
        issues.append(f"{name}: bad owner")
        return
    if owner == "script" and not row.get("script"):
        issues.append(f"{name}: script path is missing")
    if owner in {"model", "human"}:
        for key in ["why", "prepare_script", "check_script"]:
            if not row.get(key):
                issues.append(f"{name}: {key} is missing")
    for key in ["script", "prepare_script", "check_script"]:
        value = row.get(key)
        if value and not (root / value).is_file():
            issues.append(f"{name}: missing {value}")
    if owner == "script" and row.get("claims_judgment"):
        issues.append(f"{name}: a script claims judgment")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", help="skill folder")
    args = parser.parse_args(argv)
    root = Path(args.skill_dir).resolve()
    try:
        issues = check(root)
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: ownership data could not be read: {error}", file=sys.stderr)
        return 2
    for issue in issues:
        print(issue)
    print(f"ownership check: {len(issues)} problems")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
