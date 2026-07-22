#!/usr/bin/env python3
"""Scaffold a new skill directory that passes every factory check.

Creates SKILL.md, mise.toml, a CI workflow, support directories,
starter script and tests, seed evals, and copies of the checker
scripts so the new skill verifies itself. Prints a JSON summary.

Exit codes:
  0  skill created
  1  target already exists (rerun with --force to replace it)
  2  usage or input error

Example:
  python3 scripts/scaffold_skill.py --name release-notes \\
    --description "Use when release notes are needed from a git log." \\
    --dest ~/skills
"""
import argparse
import datetime
import json
import re
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
ASSETS = SKILL_DIR / "assets"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
DIRS = ["references", "assets", "scripts", "scripts/tests", "evals",
        ".github/workflows"]
FILLED = [
    ("SKILL.md", "skill-template.md"),
    ("references/decisions.md", "decisions-template.md"),
    ("evals/evals.json", "evals-template.json"),
    ("evals/trigger-queries.json", "trigger-template.json"),
]
COPIED = [
    ("mise.toml", "mise-template.toml"),
    (".github/workflows/ci.yml", "ci/ci.yml"),
    ("scripts/skill_info.py", "starter-script.py"),
    ("scripts/tests/test_scripts.py", "starter-test.py"),
    ("assets/eval-case-template.json", "eval-case-template.json"),
]
CHECKERS = ["lint_writing.py", "validate_skill.py",
            "check_code_rules.py", "check_evals.py"]


def fill(template, tokens):
    text = (ASSETS / template).read_text(encoding="utf-8")
    for key, value in tokens.items():
        text = text.replace("{{%s}}" % key, value)
    return text


def argument_error(args):
    if not NAME_RE.fullmatch(args.name) or len(args.name) > 64:
        return ("name must be 1 to 64 characters matching "
                f"^[a-z0-9][a-z0-9._-]*$ and got: {args.name!r}")
    if "Use when" not in args.description:
        return 'description must contain "Use when" so the skill triggers'
    if len(args.description) > 1024:
        return "description caps at 1024 characters"
    if not Path(args.dest).is_dir():
        return f"destination directory does not exist: {args.dest}"
    return None


def build(target, tokens):
    for sub in DIRS:
        (target / sub).mkdir(parents=True)
    for destination, template in FILLED:
        (target / destination).write_text(fill(template, tokens),
                                          encoding="utf-8")
    for destination, source in COPIED:
        shutil.copy(ASSETS / source, target / destination)
    for name in CHECKERS:
        shutil.copy(SKILL_DIR / "scripts" / name, target / "scripts" / name)
    shutil.copy(SKILL_DIR / "references" / "generation-contract.md",
                target / "references" / "generation-contract.md")
    return len(FILLED) + len(COPIED) + len(CHECKERS) + 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--name", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--dest", required=True,
                        help="parent directory for the new skill")
    parser.add_argument("--force", action="store_true",
                        help="replace an existing target directory")
    args = parser.parse_args(argv)
    error = argument_error(args)
    if error:
        print(f"error: {error}")
        return 2
    target = Path(args.dest).resolve() / args.name
    if target.exists() and not args.force:
        print(f"error: {target} exists; rerun with --force to replace it")
        return 1
    if target.exists():
        shutil.rmtree(target)
    tokens = {"NAME": args.name, "DESCRIPTION": args.description,
              "DATE": datetime.date.today().isoformat()}
    count = build(target, tokens)
    print(json.dumps({"created": str(target), "files": count,
                      "next": "run mise run ci inside the new skill"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
