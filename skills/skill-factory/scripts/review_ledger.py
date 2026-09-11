#!/usr/bin/env python3
"""Decode strict JSON or build an asserted-relationship ledger view.

Usage: review_ledger.py parse|view|write [--write-root ROOT] < input.json
Exit codes: 0 returns JSON, 1 rejects input, 2 is invalid CLI usage.
Example: review_ledger.py view < captured-ledger-request.json
Public entry: mise run ledger -- request.json
"""
import argparse
import json
import sys

from agentic_request_contract import read_json
from review_ledger_graph import view
from review_ledger_write import write_file


def operation_result(data, operation, write_root):
    if operation == "write":
        if not write_root:
            raise ValueError("write requires a caller-selected --write-root")
        result = write_file(data, write_root)
        data = {"view_text": json.dumps(result, ensure_ascii=False, allow_nan=False),
                "source_sha256": result["before"]["source_sha256"],
                "ledger_bytes": result["before"]["ledger_bytes"]}
    elif operation == "view":
        ledger = read_json(data["ledger_text"])
        result = view(ledger, data["request"])
        data = {"view_text": json.dumps(result, ensure_ascii=False, allow_nan=False),
                "source_sha256": ledger["source"]["sha256"]}
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["parse", "view", "write"])
    parser.add_argument("--write-root")
    args = parser.parse_args(argv)
    if args.operation != "write" and args.write_root is not None:
        parser.error("write root only applies to write")
    try:
        data = read_json(sys.stdin.buffer.read().decode("utf-8"))
        data = operation_result(data, args.operation, args.write_root)
        print(json.dumps(data, ensure_ascii=False, allow_nan=False))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
