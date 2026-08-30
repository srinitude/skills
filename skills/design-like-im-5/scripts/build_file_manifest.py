#!/usr/bin/env python3
"""List each public file and its fixed package role.

Exit codes:
  0  the manifest was written
  1  no public files were found
  2  the skill path is bad
"""
import argparse
import json
import sys
from pathlib import Path


def role(path):
    if path == "SKILL.md":
        return "entry", "agent", "skill use"
    if path == "mise.toml":
        return "task graph", "validator", "package check"
    if path.startswith(".github/"):
        return "automation", "host", "repository check"
    folder = path.split("/", 1)[0]
    data = {
        "assets": ("contract", "script", "run setup"),
        "evals": ("test", "evaluator", "skill evaluation"),
        "examples": ("example", "agent", "command help"),
        "references": ("guidance", "agent", "matched task"),
        "scripts": ("tool", "agent", "fixed work"),
    }
    return data.get(folder, ("support", "agent", "matched task"))


def row(path):
    item_role, consumer, trigger = role(path)
    return {
        "path": path,
        "role": item_role,
        "purpose": f"Serve the {item_role} role for this skill.",
        "consumer": consumer,
        "load_trigger": trigger,
        "source": "design-like-im-5 package",
        "version": "0.1.0",
        "output_effect": "Changes skill use, proof, or checks.",
        "mutable": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", help="skill folder")
    args = parser.parse_args(argv)
    root = Path(args.skill_dir).resolve()
    if not root.is_dir():
        print("error: skill folder was not found", file=sys.stderr)
        return 2
    target = root / "assets" / "file-manifest.json"
    paths = sorted(str(path.relative_to(root)) for path in root.rglob("*")
                   if path.is_file() and "__pycache__" not in path.parts)
    if "assets/file-manifest.json" not in paths:
        paths.append("assets/file-manifest.json")
        paths.sort()
    if not paths:
        print("blocked: no public files", file=sys.stderr)
        return 1
    data = {"version": "1.0.0", "files": [row(path) for path in paths]}
    target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(f"file manifest built: {len(paths)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
