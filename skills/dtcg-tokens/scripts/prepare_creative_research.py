#!/usr/bin/env python3
"""Validate and normalize a dated creative research record.

The agent gathers sources with available web tools. This script checks the saved record. It does not search the web.

Exit codes:
  0  the record passes
  1  required coverage or source fields fail
  2  usage or input data is invalid
"""
import argparse
import json
import sys
from datetime import date
from pathlib import Path

SOURCE_FIELDS = {"query", "url", "publisher", "publication_date", "retrieval_date", "source_class", "version", "mechanism", "counterevidence", "access_limits"}
CAPABILITY_STATES = {"used", "not_applicable", "unavailable", "blocked"}


def validate(record):
    errors = []
    try:
        run_date = date.fromisoformat(record["run_date"])
    except (KeyError, TypeError, ValueError):
        return ["E_SOURCE_CURRENT run_date must be ISO YYYY-MM-DD"]
    sources = record.get("sources", [])
    for index, source in enumerate(sources):
        missing = sorted(SOURCE_FIELDS - set(source))
        if missing:
            errors.append(f"source {index} missing: {', '.join(missing)}")
        if source.get("retrieval_date") != run_date.isoformat():
            errors.append(f"E_SOURCE_CURRENT source {index} retrieval_date differs from run_date")
    coverage = record.get("coverage", {})
    if len(set(coverage.get("mechanism_families", []))) < 6:
        errors.append("E_SOURCE_DISTANCE needs six mechanism families")
    if len(set(coverage.get("distant_domains", []))) < 3:
        errors.append("E_SOURCE_DISTANCE needs three distant domains")
    if not coverage.get("antithetical_source"):
        errors.append("E_SOURCE_DISTANCE needs one antithetical source")
    if not coverage.get("current_research_source"):
        errors.append("E_SOURCE_CURRENT needs one current research source")
    for name, state in record.get("capability_ledger", {}).items():
        if state.get("status") not in CAPABILITY_STATES or not state.get("reason"):
            errors.append(f"capability {name} needs a valid status and reason")
    if record.get("unchanged_additions", 0) < 2:
        errors.append("research stop rule needs two unchanged additions")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="research record JSON")
    parser.add_argument("--output", help="optional normalized output JSON")
    args = parser.parse_args(argv)
    try:
        record = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    errors = validate(record)
    report = {"status": "PASS" if not errors else "BLOCKED", "errors": errors, "record": record}
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
