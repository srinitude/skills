#!/usr/bin/env python3
"""Dispatch a typed agentic request without shell interpolation.

Usage:
  python3 scripts/run_agentic_request.py --request REQUEST_JSON_OR_DASH

REQUEST_JSON_OR_DASH is a JSON file or - for standard input. The request binds
to a digest-bound use-case contract and supplies a long prompt, zero or more
digest-bound SKILL.md files, and traced primitive records. Each file reference is read once;
the verified UTF-8 text is passed in use_case.text and each skills[].text.
Prompt bytes, including line endings, are preserved. Only caller-authorized
inputs may be supplied to the runner. The caller supplies the command and
argument array. The runner receives JSON stdin; duplicate keys and non-finite
numbers fail. This snapshot is not live-state isolation or semantic acceptance.
The use-case must declare initial_context resource IDs, roles, paths, digests
and reading dependencies. The request must supply matching context references,
including one governing ledger. Full context text reaches the runner in reading
dependency order; missing or invalid context blocks dispatch.

Exit codes:
  0  runner exited successfully; domain acceptance is separate
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

from agentic_request_contract import build_envelope, read_json
from agentic_context import capture_context


def read_request(source):
    if source == "-":
        return read_json(sys.stdin.read()), Path.cwd()
    path = Path(source)
    return read_json(path.read_text(encoding="utf-8")), path.parent


def runner_command(command, raw_arguments):
    try:
        arguments = read_json(raw_arguments)
    except json.JSONDecodeError as error:
        raise ValueError("runner args must be a JSON array") from error
    if not isinstance(arguments, list) or not all(
            isinstance(value, str) for value in arguments):
        raise ValueError("runner args must be an array of text")
    return [command, *arguments]


def dispatch(command, data, base=None):
    base = Path.cwd() if base is None else Path(base)
    payload = build_envelope(data, base)
    payload["context"] = capture_context(payload["use_case"], data.get("context"), base)
    result = subprocess.run(
        command, input=json.dumps(payload, allow_nan=False), capture_output=True,
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
        command = runner_command(args.runner, args.runner_args_json)
        return dispatch(command, data, base)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
