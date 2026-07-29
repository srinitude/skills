#!/usr/bin/env python3
"""Validate a completed agent-action verdict.

Checks the public verdict headings, verdict label, and source URL rule.
Prints one JSON report to stdout.

Exit codes:
  0  verdict passes
  1  verdict is incomplete or malformed
  2  usage or input error

Example:
  python3 scripts/validate_verdict.py --input verdict.md
"""
import argparse
import json
import re
import sys
from pathlib import Path

TITLE = "# Agent action verdict"
HEADINGS = [
    "## Exact action",
    "## Verdict",
    "## Pinned system card",
    "## Evidence ledger",
    "## Trial metrics",
    "## Outcome, trace, and constraints",
    "## Outside view and transport",
    "## Mechanisms",
    "## Limits and safety boundary",
    "## What would change the verdict",
    "## Next safe test",
    "## Sources",
    "## Research log",
]
VERDICTS = [
    "LIKELY",
    "UNLIKELY",
    "UNCERTAIN",
    "INSUFFICIENT EVIDENCE",
    "UNVALIDATED HYPOTHESIS",
]
URL_RE = re.compile(r"https?://[^\s)]+")


def verdict_label(text):
    for label in VERDICTS:
        if re.search(rf"\b{re.escape(label)}\b", text):
            return label
    return ""


def check(text):
    errors = []
    if not text.startswith(TITLE):
        errors.append(f"document must start with {TITLE}")
    positions = []
    for heading in HEADINGS:
        position = text.find(heading)
        positions.append(position)
        if position < 0:
            errors.append(f"missing heading: {heading}")
    present = [position for position in positions if position >= 0]
    if present != sorted(present):
        errors.append("required headings are out of order")
    label = verdict_label(text)
    if not label:
        errors.append("missing allowed verdict label")
    if label != "UNVALIDATED HYPOTHESIS" and not URL_RE.search(text):
        errors.append("a researched verdict needs at least one source URL")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--input", required=True, help="completed verdict markdown")
    args = parser.parse_args(argv)
    path = Path(args.input)
    if not path.is_file():
        print(f"error: no such file: {path}", file=sys.stderr)
        return 2
    errors = check(path.read_text(encoding="utf-8"))
    report = {
        "errors": errors,
        "input": str(path),
        "status": "FAIL" if errors else "PASS",
    }
    print(json.dumps(report, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
