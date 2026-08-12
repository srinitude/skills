#!/usr/bin/env python3
"""Read targeted parts of the canonical schema contract.

The contract is machine readable YAML, so these commands answer a question
without loading the whole file into the working context.

Commands:
  skeleton  Print the canonical YAML skeleton.
  sections  Print the top level section names in schema order.
  groups    Print the field detail group names.
  group     Print every field rule inside one group.
  field     Print the rule for one dotted field path.
  rules     Print the font rules, syntax rules, and self-check list.

Exit codes:
  0  the requested text was printed
  1  the requested group, field, or file was not found
  2  usage or input error

Examples:
  python3 scripts/schema_tools.py skeleton --output /tmp/skeleton.yaml
  python3 scripts/schema_tools.py field typography.font_families.primary
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from extraction_schema import SCHEMA

SKELETON = Path(__file__).resolve().parents[1] / "assets" / "schema-skeleton.yaml"


class NotFound(LookupError):
    """The requested part of the contract does not exist."""


def dump(value):
    """Return one YAML block for any contract fragment."""
    if isinstance(value, str):
        return value.rstrip() + "\n"
    return yaml.safe_dump(value, sort_keys=False, width=100, allow_unicode=True)


def skeleton():
    """Return the canonical YAML skeleton."""
    if not SKELETON.is_file():
        raise NotFound(f"missing skeleton: {SKELETON}")
    return SKELETON.read_text(encoding="utf-8")


def sections():
    """Return the top level section names in schema order."""
    return "\n".join(SCHEMA["top_level_sections"]) + "\n"


def groups():
    """Return the field detail group names."""
    return "\n".join(SCHEMA["field_details"]) + "\n"


def group(name):
    """Return every field rule inside one group."""
    found = SCHEMA["field_details"].get(name)
    if found is None:
        raise NotFound(f"group not found: {name}")
    return dump(found)


def field(path):
    """Return the rule for one dotted field path."""
    for rules in SCHEMA["field_details"].values():
        if path in rules:
            return dump({path: rules[path]})
    raise NotFound(f"field not found: {path}")


def rules():
    """Return the font rules, syntax rules, and self-check list."""
    return dump({"font_rules": SCHEMA["font_rules"],
                 "universal_shapes": SCHEMA["universal_shapes"],
                 "token_object": SCHEMA["token_object"],
                 "yaml_syntax_rules": SCHEMA["yaml_syntax_rules"],
                 "self_check": SCHEMA["self_check"]})


def emit(text, output):
    """Write the text to stdout or to the requested path."""
    if output:
        Path(output).write_text(text, encoding="utf-8")
        return
    sys.stdout.write(text)


def build_parser():
    """Return the argument parser for every command."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("skeleton", "sections", "groups", "rules"):
        commands.add_parser(name).add_argument("--output")
    named = commands.add_parser("group")
    named.add_argument("name", help="field detail group name")
    named.add_argument("--output")
    single = commands.add_parser("field")
    single.add_argument("path", help="dotted field path, such as typography.weights")
    single.add_argument("--output")
    return parser


def resolve(args):
    """Return the text the requested command produces."""
    if args.command == "group":
        return group(args.name)
    if args.command == "field":
        return field(args.path)
    return {"skeleton": skeleton, "sections": sections,
            "groups": groups, "rules": rules}[args.command]()


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        emit(resolve(args), args.output)
    except NotFound as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
