#!/usr/bin/env python3
"""Decode strict JSON or build an asserted-relationship ledger view.

Usage: review_ledger.py parse|view < input.json
Exit codes: 0 returns JSON, 1 rejects input, 2 is invalid CLI usage.
Example: review_ledger.py view < captured-ledger-request.json
Public entry: mise run ledger -- request.json
"""
import argparse
import json
import sys

from agentic_request_contract import read_json
from review_ledger_graph import view


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["parse", "view"])
    args = parser.parse_args(argv)
    try:
        data = read_json(sys.stdin.buffer.read().decode("utf-8"))
        if args.operation == "view":
            ledger = read_json(data["ledger_text"])
            result = view(ledger, data["request"])
            data = {"view_text": json.dumps(result, ensure_ascii=False, allow_nan=False),
                    "source_sha256": ledger["source"]["sha256"]}
        print(json.dumps(data, ensure_ascii=False, allow_nan=False))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
