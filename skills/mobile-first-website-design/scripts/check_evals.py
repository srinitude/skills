#!/usr/bin/env python3
"""Validate the public eval and trigger registries."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name):
    return json.loads((ROOT / "evals" / name).read_text(encoding="utf-8"))


def main():
    problems = []
    cases = load("cases.json")
    triggers = load("trigger-cases.json")
    legacy = load("evals.json")
    queries = load("trigger-queries.json")
    if cases.get("skill") != "mobile-first-website-design" or len(cases.get("cases", [])) != 8:
        problems.append("cases")
    ids = [row.get("id") for row in cases.get("cases", [])]
    if ids != [f"MFWD-{number:03d}" for number in range(1, 9)]:
        problems.append("case-ids")
    trigger_rows = triggers.get("cases", [])
    labels = {row.get("should_trigger") for row in trigger_rows}
    if len(trigger_rows) < 8 or labels != {True, False}:
        problems.append("triggers")
    if len(legacy.get("evals", [])) != 8 or len(queries) != len(trigger_rows):
        problems.append("public-registries")
    print(json.dumps({"errors": problems, "status": "PASS" if not problems else "BLOCKED"}, sort_keys=True, separators=(",", ":")))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
