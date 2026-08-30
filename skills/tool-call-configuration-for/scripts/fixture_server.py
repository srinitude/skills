#!/usr/bin/env python3
"""Run a confined line-delimited JSON-RPC fixture server.

Exit codes:
  0  input stream handled
  2  invalid command arguments

Examples:
  python3 scripts/fixture_server.py --root /tmp/tool-fixture
  python3 scripts/fixture_server.py --help
"""
import argparse
import json
import re
import sys
from pathlib import Path


def tool_list():
    text = {"type": "string"}
    key = {"type": "string", "pattern": "^[a-z0-9-]+$"}
    return [
        {"name": "sandbox.write-note", "description": "Write one confined note.",
         "inputSchema": {"type": "object", "properties": {"key": key,
                         "text": text}, "required": ["key", "text"]}},
        {"name": "sandbox.read-note", "description": "Read one confined note.",
         "inputSchema": {"type": "object", "properties": {"key": key},
                         "required": ["key"]}},
    ]


def checked_path(root, arguments):
    key = arguments.get("key")
    if not isinstance(key, str) or not re.fullmatch(r"[a-z0-9-]+", key):
        raise ValueError("key must match ^[a-z0-9-]+$")
    return root / f"{key}.txt", key


def call_tool(root, params):
    name = params.get("name")
    arguments = params.get("arguments", {})
    path, key = checked_path(root, arguments)
    if name == "sandbox.write-note":
        text = arguments.get("text")
        if not isinstance(text, str):
            raise ValueError("text must be a string")
        path.write_text(text, encoding="utf-8")
        return {"content": [{"type": "text", "text": key}]}
    if name == "sandbox.read-note":
        return {"content": [{"type": "text", "text": path.read_text()}]}
    raise LookupError(f"unknown tool: {name}")


def reply(root, request):
    method = request.get("method")
    if method == "initialize":
        result = {"protocolVersion": "2025-11-25", "capabilities": {"tools": {}},
                  "serverInfo": {"name": "owned-fixture", "version": "1.0.0"}}
    elif method == "tools/list":
        result = {"tools": tool_list()}
    elif method == "tools/call":
        result = call_tool(root, request.get("params", {}))
    else:
        raise LookupError(f"unknown method: {method}")
    return {"jsonrpc": "2.0", "id": request.get("id"), "result": result}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="confined fixture state directory")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    for line in sys.stdin:
        request = json.loads(line)
        try:
            response = reply(root, request)
        except (LookupError, OSError, ValueError) as error:
            response = {"jsonrpc": "2.0", "id": request.get("id"),
                        "error": {"code": -32602, "message": str(error)}}
        print(json.dumps(response, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
