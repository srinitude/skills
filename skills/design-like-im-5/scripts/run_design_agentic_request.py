#!/usr/bin/env python3
"""Send one typed design request. Do not use a shell.

Usage: run_design_agentic_request.py --request FILE_OR_DASH --runner COMMAND
Exit 0 when the runner works. Exit 1 when the request or runner fails.
Exit 2 for bad use.
Example: run_design_agentic_request.py --request request.json --runner tool
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from lib.design_agentic_request import build_envelope


def read_request(source):
    if source == "-":
        return json.load(sys.stdin), Path.cwd()
    path = Path(source)
    return json.loads(path.read_text(encoding="utf-8")), path.parent


def runner_command(command, raw):
    try:
        arguments = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("runner args need a JSON list") from error
    if not isinstance(arguments, list) or not all(
            isinstance(value, str) for value in arguments):
        raise ValueError("runner args need a list of text")
    return [command, *arguments]


def dispatch(command, payload):
    result = subprocess.run(command, input=json.dumps(payload),
                            capture_output=True, text=True, check=False)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", required=True)
    parser.add_argument("--runner", required=True)
    parser.add_argument("--runner-args-json", default="[]")
    args = parser.parse_args(argv)
    try:
        data, base = read_request(args.request)
        payload = build_envelope(data, base)
        return dispatch(runner_command(args.runner, args.runner_args_json), payload)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
