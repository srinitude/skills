#!/usr/bin/env python3
"""Refresh the release-bound official Mise primitive catalog."""
import argparse
import datetime
import hashlib
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

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


def extra_properties(definition):
    found = set()
    for option in definition.get("oneOf", []):
        for item in option.get("allOf", []):
            found |= set(item.get("properties", {}))
    return found


def schema_groups(schema):
    defs = schema.get("$defs", {})
    task = set(defs.get("task_props", {}).get("properties", {}))
    task |= extra_properties(defs.get("task", {}))
    tool = set(defs.get("tool_options", {}).get("properties", {}))
    tool |= extra_properties(defs.get("tool", {}))
    return {
        "config": sorted(schema.get("properties", {})),
        "task": sorted(task),
        "task_config": sorted(defs.get("task_config", {})
                              .get("properties", {})),
        "tool": sorted(tool),
    }


def catalog(version, raw):
    schema = json.loads(raw)
    groups = schema_groups(schema)
    missing = [name for name, values in groups.items() if not values]
    if missing:
        raise ValueError("missing primitive group: " + ", ".join(missing))
    checked = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
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
    return {key: item for key, item in value.items() if key != "checked_at"}


def atomic_write(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--version")
    parser.add_argument("--schema-file")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    path = root / "assets/mise-primitives-catalog.json"
    try:
        version = args.version or installed_version()
        expected = catalog(version, schema_bytes(version, args.schema_file))
        current = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}")
        return 2
    stale = stable_view(current) != stable_view(expected)
    if args.check:
        print(f"DTCG token Mise catalog: {'stale' if stale else 'current'}")
        return 1 if stale else 0
    atomic_write(path, expected)
    print(f"DTCG token Mise catalog: updated {version}; dispositions unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
