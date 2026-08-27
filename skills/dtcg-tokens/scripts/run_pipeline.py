#!/usr/bin/env python3
"""Create and enforce the deterministic 25-step run scaffold."""
import json
import sys

from lib.pipeline_cli import parser
from lib.pipeline_io import PipelineError


def main() -> int:
    args = parser().parse_args()
    try:
        result = args.handler(args)
    except PipelineError as error:
        print(json.dumps({"valid": False, "error": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
