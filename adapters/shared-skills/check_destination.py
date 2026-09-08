#!/usr/bin/env python3
"""Verify shared skill-directory placement without installing anything.

Exit codes: 0 verified, 1 mismatch or shadowing, 2 usage.
Example: mise run check-skill-destination -- --scope project --project . --name audit --dest .agents/skills/audit
"""
import argparse
import json
from pathlib import Path

REFERENCE = "https://agentskills.io/client-implementation/adding-skills-support"


def check(args):
    home = Path(args.home).expanduser().resolve()
    project = Path(args.project).resolve() if args.project else None
    roots = [home / ".agents/skills"]
    if project:
        roots.append(project / ".agents/skills")
    if args.scope == "project" and project is None:
        raise ValueError("project scope requires the target project")
    scope_root = roots[0] if args.scope == "user" else roots[1]
    target = Path(args.dest).absolute()
    if target.is_symlink() or scope_root.is_symlink():
        raise ValueError("installation destination must not be a symlink")
    if target.resolve() != scope_root / args.name or Path(args.name).name != args.name:
        raise ValueError("destination does not match the selected scope")
    for root in roots:
        existing = root / args.name
        if existing != target.resolve() and existing.exists():
            raise ValueError("another available skill would shadow this identity")
    return {"kind": "installation", "scope": args.scope, "destination": str(target.resolve()),
            "scope_root": str(scope_root), "visible_roots": [str(p) for p in roots],
            "reference": REFERENCE, "writes": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=["user", "project"], required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--home", default=str(Path.home()))
    parser.add_argument("--project")
    args = parser.parse_args()
    try:
        result = check(args)
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error), "writes": 0}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
