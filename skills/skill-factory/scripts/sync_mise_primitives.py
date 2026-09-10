#!/usr/bin/env python3
"""Refresh the official Mise primitive catalog without editing dispositions.

Usage: sync_mise_primitives.py [skill-root] [--check | --plan | --review REQUEST]
Exit codes: 0 current or updated, 1 stale in check mode, 2 input failure.
Example: sync_mise_primitives.py . --plan

Save content_utf8 unchanged and supply the ordinary write-file request targeting
assets/mise-primitives-catalog.json with its current initial_body_review. The
prepared checked_at is the declared timezone-aware planning observation, not
an authenticated clock or semantic acceptance. Current version/schema and exact
request/prepared bytes are checked around the effect using the shared file guard.
"""
import argparse
import datetime
import hashlib
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from agentic_request_contract import read_json
from review_ledger_context import require
from review_ledger_source import read_file
from review_ledger_write import write_file

SCHEMA_ID = "https://mise.jdx.dev/schema/mise.json"
TASK_SOURCE = "https://mise.jdx.dev/tasks/task-configuration.html"


def installed_version():
    result = subprocess.run(["mise", "--version"], capture_output=True,
                            text=True, timeout=15)
    if result.returncode:
        raise ValueError(result.stderr.strip() or "mise --version failed")
    return result.stdout.split()[0].removeprefix("v")


def schema_bytes(version, schema_file):
    if schema_file:
        return Path(schema_file).read_bytes()
    url = ("https://raw.githubusercontent.com/jdx/mise/"
           f"v{version}/schema/mise.json")
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read()
    except (urllib.error.URLError, TimeoutError) as error:
        raise ValueError(f"cannot read official Mise schema: {error}") from error


def property_names(definition):
    require(isinstance(definition, dict), "schema definition must be an object")
    properties = definition.get("properties", {})
    require(isinstance(properties, dict), "schema properties must be an object")
    return set(properties)


def extra_properties(definition):
    require(isinstance(definition, dict), "schema definition must be an object")
    options = definition.get("oneOf", [])
    require(isinstance(options, list), "schema oneOf must be an array")
    found = set()
    for option in options:
        require(isinstance(option, dict), "schema option must be an object")
        items = option.get("allOf", [])
        require(isinstance(items, list), "schema allOf must be an array")
        for item in items:
            found |= property_names(item)
    return found


def schema_groups(schema):
    require(isinstance(schema, dict), "schema must be an object")
    defs = schema.get("$defs", {})
    require(isinstance(defs, dict), "schema definitions must be an object")
    task = property_names(defs.get("task_props", {}))
    task |= extra_properties(defs.get("task", {}))
    tool = property_names(defs.get("tool_options", {}))
    tool |= extra_properties(defs.get("tool", {}))
    return {"config": sorted(property_names(schema)), "task": sorted(task),
            "task_config": sorted(property_names(defs.get("task_config", {}))),
            "tool": sorted(tool)}


def catalog(version, raw, checked=None):
    schema = read_json(raw.decode("utf-8"))
    groups = schema_groups(schema)
    missing = [name for name, values in groups.items() if not values]
    if missing:
        raise ValueError("missing primitive group: " + ", ".join(missing))
    checked = checked if checked is not None else datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    require(isinstance(checked, str) and datetime.datetime.fromisoformat(checked).tzinfo is not None,
            "catalog checked_at must be a timezone-aware planning observation")
    return {
        "version": version,
        "source": SCHEMA_ID,
        "release_source": ("https://raw.githubusercontent.com/jdx/mise/"
                           f"v{version}/schema/mise.json"),
        "task_source": TASK_SOURCE,
        "checked_at": checked,
        "schema_sha256": hashlib.sha256(raw).hexdigest(),
        "groups": groups,
    }


def stable_view(value):
    require(isinstance(value, dict), "catalog must be an object")
    return {key: item for key, item in value.items() if key != "checked_at"}


def reviewed_refresh(root, args):
    require(args.review is not None, 'catalog writes require --review with a current write-file request')
    binding = {'path': str(args.review)}
    raw = read_file(binding)
    request = read_json(raw.decode('utf-8'))
    require(isinstance(request, dict) and isinstance(request.get('change'), dict)
            and request['change'].get('path') == 'assets/mise-primitives-catalog.json',
            'catalog review must target assets/mise-primitives-catalog.json')
    prepared = read_file(request['change']['new_file'])
    value = read_json(prepared.decode('utf-8'))
    require(isinstance(value, dict) and isinstance(value.get('checked_at'), str), 'missing catalog planning observation')
    def current_inputs():
        require(read_file(binding) == raw, 'catalog review request changed')
        version = args.version or installed_version()
        expected = catalog(version, schema_bytes(version, args.schema_file), value['checked_at'])
        return read_file(request['change']['new_file']) == (json.dumps(expected, indent=2) + '\n').encode()
    result = write_file(request, root, effect_check=current_inputs)
    return {'status': 'PASS', 'mode': 'write', 'change': result}


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--version")
    parser.add_argument("--schema-file")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true")
    modes.add_argument("--plan", action="store_true")
    modes.add_argument("--review")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    candidate = Path(args.root)
    try:
        require(not candidate.is_symlink() and candidate.is_dir(), 'catalog root must be a regular directory')
        root = candidate.resolve()
        if not args.check and not args.plan:
            result = reviewed_refresh(root, args)
        else:
            version = args.version or installed_version()
            expected = catalog(version, schema_bytes(version, args.schema_file))
            if args.plan:
                result = {'status': 'PASS', 'mode': 'plan', 'content_utf8': json.dumps(expected, indent=2) + '\n'}
            else:
                current = read_json((root / 'assets/mise-primitives-catalog.json').read_text(encoding='utf-8'))
                stale = stable_view(current) != stable_view(expected)
                print(f"Mise primitive catalog: {'stale' if stale else 'current'}")
                return 1 if stale else 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
