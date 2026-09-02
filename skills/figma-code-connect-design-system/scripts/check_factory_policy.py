#!/usr/bin/env python3
"""Check one Figma factory policy or run receipt."""
import argparse
import json
import sys
from pathlib import Path

from lib.factory_checks import CHECKS, load
from lib.factory_graph import dependencies


def invocation(root, receipt):
    data, *_, tasks = load(root)
    value = json.loads(Path(receipt).read_text())
    found, names = [], []
    if value.get("skill") != data.get("skill"):
        found.append("Figma run receipt has the wrong skill")
    for item in value.get("entries", []):
        names.append(item.get("task"))
    expected = set(tasks) - {"invocation-policy"}
    if set(names) != expected or len(names) != len(set(names)):
        found.append("Figma run receipt must name each task once")
    required, pending = set(), ["complete"]
    while pending:
        name = pending.pop()
        if name not in required:
            required.add(name)
            pending.extend(dependencies(tasks[name]))
    states = {item.get("task"): item.get("status") for item in value.get("entries", [])}
    if any(states.get(name) != "run" for name in required - {"invocation-policy"}):
        found.append("Each default Figma gate must run")
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=[*CHECKS, "invocation"])
    parser.add_argument("target", nargs="?")
    args = parser.parse_args()
    root = Path(".").resolve()
    try:
        if args.mode == "invocation":
            found = invocation(root, args.target)
        elif args.mode == "mise":
            found = CHECKS[args.mode](*load(root), root=root)
        else:
            found = CHECKS[args.mode](*load(root))
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"FAIL {error}")
        return 2
    for problem in found:
        print(f"FAIL {problem}")
    print(f"Figma factory {args.mode}: {len(found)} problems")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
