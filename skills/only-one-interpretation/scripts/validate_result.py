#!/usr/bin/env python3
"""Validate bounded only-one-interpretation result records.

This script checks record structure, branch exclusivity, exact ledger equality,
trace completeness, attack coverage, method levels, and secret redaction. It
does not decide whether prose has one meaning.

Exit codes:
  0  every record passes
  1  at least one record fails
  2  usage or input error

Example:
  python3 scripts/validate_result.py evals/result-fixtures/*.json
"""
import argparse
import json
import sys
from pathlib import Path

from result_contract import validate


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, json.JSONDecodeError) as error:
        return None, str(error)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", nargs="+", help="JSON result records")
    args = parser.parse_args(argv)
    failed = False
    for name in args.records:
        path = Path(name)
        record, error = load(path)
        if error:
            print(f"{path.name}: input error: {error}", file=sys.stderr)
            return 2
        problems = validate(record)
        for problem in problems:
            print(f"{path.name}: {problem}")
        if problems:
            failed = True
        else:
            result = {"file": path.name, "status": record["status"], "problems": 0}
            print(json.dumps(result))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
