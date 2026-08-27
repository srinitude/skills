#!/usr/bin/env python3
"""Validate DTCG 2025.10 token structure, values, aliases, and cycles.

Exit codes:
  0  the token file passes
  1  the token file fails
  2  usage or input error

Example:
  python3 scripts/validate_dtcg.py tokens.tokens.json
"""
import argparse
import json
import sys
from pathlib import Path

from lib.dtcg import validate


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("tokens", help="DTCG JSON token file")
    args = parser.parse_args(argv)
    path = Path(args.tokens)
    if not path.is_file():
        print(f"error: token file not found: {path}", file=sys.stderr)
        return 2
    schema = Path(__file__).resolve().parents[1] / "assets" / "dtcg-format-2025.10.schema.json"
    report = validate(path, schema)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
