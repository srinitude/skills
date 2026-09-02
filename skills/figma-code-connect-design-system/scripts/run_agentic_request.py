#!/usr/bin/env python3
"""Send one typed Figma request to an external runner."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from lib.agentic_request import build


def read_request(source):
    if source == "-":
        return json.load(sys.stdin), Path.cwd()
    path = Path(source)
    return json.loads(path.read_text(encoding="utf-8")), path.parent


def runner(command, raw):
    try:
        args = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("runner args need a JSON list") from error
    if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
        raise ValueError("runner args need a list of text")
    return [command, *args]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True)
    parser.add_argument("--runner", required=True)
    parser.add_argument("--runner-args-json", default="[]")
    args = parser.parse_args()
    try:
        data, base = read_request(args.request)
        payload = build(data, base)
        result = subprocess.run(runner(args.runner, args.runner_args_json),
            input=json.dumps(payload), capture_output=True, text=True, check=False)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
