#!/usr/bin/env python3
"""Check direct support and rich guidance for every skill section.

The script checks structure. The model owns every product and design judgment.

Exit codes:
  0  every section passed
  1  one or more sections failed
  2  section data could not be read

Example:
  python3 scripts/check_section_support.py .
"""
import argparse
import json
import re
import sys
from pathlib import Path

HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SUPPORT_FOLDERS = {"references", "scripts", "assets", "evals", "examples"}
REQUIRED = {
    "id", "heading", "level", "purpose", "enter_when", "support",
    "load_order", "actions", "evidence", "output", "judgment_owner",
    "deterministic_scope", "model_freedom", "fixed_constraints",
    "do_not_substitute", "wall_clock", "blocked_when",
}
LIST_FIELDS = {
    "support", "load_order", "actions", "evidence", "deterministic_scope",
    "model_freedom", "fixed_constraints", "wall_clock", "blocked_when",
}
TEXT_FIELDS = {"purpose", "enter_when", "output", "do_not_substitute"}
FORBIDDEN = {
    "decision", "rank", "score", "chosen_direction", "chosen_state",
    "design_verdict",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sections(text):
    found, current = [], None
    fence, front = False, text.startswith("---\n")
    for line in text.splitlines():
        if front:
            if line == "---":
                front = False
            continue
        if line.strip().startswith(("```", "~~~")):
            fence = not fence
        match = None if fence else HEADING.match(line)
        if match:
            if current:
                found.append(current)
            current = {"heading": match.group(2),
                       "level": len(match.group(1)), "body": []}
        elif current:
            current["body"].append(line)
    if current:
        found.append(current)
    return found


def safe_file(root, name):
    if not isinstance(name, str) or not name:
        return False
    path = Path(name)
    if path.is_absolute() or ".." in path.parts:
        return False
    if path.parts[0] not in SUPPORT_FOLDERS:
        return False
    try:
        target = (root / path).resolve(strict=True)
    except OSError:
        return False
    return target.is_file() and root in target.parents


def path_issue(root, section_id, item):
    if not isinstance(item, dict):
        return [f"{section_id}: support item must be a map"]
    if set(item) != {"path", "load_when", "contribution"}:
        return [f"{section_id}: support item needs path, load_when, and contribution"]
    path = item.get("path", "")
    issues = []
    if not safe_file(root, path):
        issues.append(f"{section_id}: support path is missing or unsafe: {path}")
    for key in ["load_when", "contribution"]:
        if not isinstance(item.get(key), str) or not item[key].strip():
            issues.append(f"{section_id}: {path} needs {key}")
    return issues


def record_issues(root, record, body):
    section_id = record.get("id", "missing section id")
    issues = []
    if set(record) != REQUIRED:
        issues.append(f"{section_id}: section fields do not match the owner map")
    for key in TEXT_FIELDS:
        if not isinstance(record.get(key), str) or not record[key].strip():
            issues.append(f"{section_id}: {key} needs useful text")
    for key in LIST_FIELDS:
        if not isinstance(record.get(key), list) or not record[key]:
            issues.append(f"{section_id}: {key} needs at least one item")
    if record.get("judgment_owner") != "model":
        issues.append(f"{section_id}: model must own judgment")
    if FORBIDDEN & set(record):
        issues.append(f"{section_id}: section map claims a model verdict")
    support = record.get("support", [])
    for item in support:
        issues.extend(path_issue(root, section_id, item))
    paths = [item.get("path") for item in support if isinstance(item, dict)]
    if record.get("load_order") != paths:
        issues.append(f"{section_id}: load_order must match support order")
    if not any(path in body for path in paths if isinstance(path, str)):
        issues.append(f"{record.get('heading')}: direct body needs a mapped support path")
    return issues


def document_issues(root, doc, body_sections):
    issues = []
    if set(doc.get("support_folders", [])) != SUPPORT_FOLDERS:
        issues.append("support_folders must name all five folders")
    records = doc.get("sections", [])
    expected = [(row["heading"], row["level"]) for row in body_sections]
    actual = [(row.get("heading"), row.get("level")) for row in records]
    if actual != expected:
        issues.append("section records must match every heading in body order")
    ids = [row.get("id") for row in records]
    if len(ids) != len(set(ids)):
        issues.append("section ids must be unique")
    bodies = {row["heading"]: "\n".join(row["body"]) for row in body_sections}
    for record in records:
        issues.extend(record_issues(root, record,
                                    bodies.get(record.get("heading"), "")))
    product = next((row for row in records
                    if row.get("heading") == "Discover product states"), {})
    kinds = {row.get("path", "").split("/", 1)[0]
             for row in product.get("support", [])}
    if kinds != SUPPORT_FOLDERS:
        issues.append("Discover product states: needs all five support folders")
    return issues


def check(root):
    body = sections((root / "SKILL.md").read_text(encoding="utf-8"))
    doc = load(root / "assets" / "section-support.json")
    return document_issues(root, doc, body)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", nargs="?", default=".")
    args = parser.parse_args(argv)
    root = Path(args.skill_dir).resolve()
    try:
        issues = check(root)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"error: section support could not be read: {error}",
              file=sys.stderr)
        return 2
    for issue in issues:
        print(issue)
    print(f"section support check: {len(issues)} problems")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
