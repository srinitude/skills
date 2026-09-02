#!/usr/bin/env python3
"""Dispatch a typed agentic request without shell interpolation.

Usage:
  python3 scripts/run_agentic_request.py --request REQUEST_JSON_OR_DASH

REQUEST_JSON_OR_DASH is a JSON file or - for standard input. The request binds
to a digest-bound use-case contract and supplies a long prompt, zero or more
digest-bound SKILL.md files, and traced primitive records. The caller supplies
the runner command and argument array. The runner receives JSON stdin.

Exit codes:
  0  runner accepted and completed the request
  1  request, digest, file, or runner failed
  2  bad command usage

Example:
  python3 scripts/run_agentic_request.py --request request.json \
    --runner agent-runner --runner-args-json '["run"]'
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from agentic_request_contract import build_envelope


def read_request(source):
    if source == "-":
        return json.load(sys.stdin), Path.cwd()
    path = Path(source)
    return json.loads(path.read_text(encoding="utf-8")), path.parent


def runner_command(command, raw_arguments):
    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as error:
        raise ValueError("runner args must be a JSON array") from error
    if not isinstance(arguments, list) or not all(
            isinstance(value, str) for value in arguments):
        raise ValueError("runner args must be an array of text")
    return [command, *arguments]


def dispatch(command, payload):
    result = subprocess.run(
        command, input=json.dumps(payload), capture_output=True,
        text=True, check=False)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--request", required=True)
    parser.add_argument("--runner", required=True)
    parser.add_argument("--runner-args-json", default="[]")
    args = parser.parse_args(argv)
    try:
        data, base = read_request(args.request)
        payload = build_envelope(data, base)
        command = runner_command(args.runner, args.runner_args_json)
        return dispatch(command, payload)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
