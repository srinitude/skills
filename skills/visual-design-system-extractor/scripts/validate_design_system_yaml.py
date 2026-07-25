#!/usr/bin/env python3
"""Validate a visual design system extraction against the schema and font rules.

Checks section coverage and order, evidence separation, confidence labels,
not-applicable objects, and the font rules: every named typeface must be a
Google Fonts family carrying a rarity record from the live catalog.

By default the recorded ranks are re-checked against the live feed. Pass
--no-live-fonts when the feed is unreachable, then say so in the answer
rather than presenting the result as verified.

Exit codes:
  0  the document passed every check
  1  at least one check failed
  2  usage or input error

Examples:
  python3 scripts/validate_design_system_yaml.py extraction.yaml
  python3 scripts/validate_design_system_yaml.py - --no-live-fonts
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import extraction_rules
from extraction_schema import count_key
from font_rules import DEFAULT_MIN_PERCENTILE, verify_live
from google_fonts_api import FeedError, load_catalog

try:
    import yaml
except ImportError as missing:
    raise SystemExit(
        "PyYAML is required. Run: uv run --no-project --with 'PyYAML>=6,<7' "
        "python scripts/validate_design_system_yaml.py <file>"
    ) from missing


class StrictLoader(yaml.SafeLoader):
    """Safe loader that rejects duplicate mapping keys."""


def no_duplicate_keys(loader, node, deep=False):
    """Build a mapping and raise when a key repeats."""
    loader.flatten_mapping(node)
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping", node.start_mark,
                f"found duplicate key {key!r}", key_node.start_mark)
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, no_duplicate_keys)


def read_input(source):
    """Return the document text from a path or from standard input."""
    if source == "-":
        return sys.stdin.read()
    return Path(source).read_text(encoding="utf-8")


def parse(text):
    """Return the parsed document, or a message describing the parse failure."""
    try:
        return yaml.load(text, Loader=StrictLoader), None
    except yaml.YAMLError as error:
        return None, f"Invalid YAML: {error}"


def build_parser():
    """Return the argument parser."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="YAML file to validate, or - for stdin")
    parser.add_argument("--min-confidence-markers", type=int, default=5,
                        help="lowest number of confidence keys. Default: 5")
    parser.add_argument("--min-rarity-percentile", type=float,
                        default=DEFAULT_MIN_PERCENTILE,
                        help="lowest rarity percentile a family may hold")
    parser.add_argument("--no-live-fonts", action="store_true",
                        help="skip the live catalog comparison")
    return parser


def add_live_errors(entries, floor, errors):
    """Compare every font entry against the live catalog."""
    try:
        catalog = load_catalog()
    except FeedError as error:
        errors.append(f"live font check failed: {error}")
        return False
    verify_live(entries, catalog, floor, errors)
    return True


def check_markers(data, minimum, errors):
    """Require enough confidence markers across the document."""
    found = count_key(data, "confidence")
    if found < minimum:
        errors.append(f"Expected at least {minimum} confidence markers; found {found}.")
    return found


def run(args):
    """Validate one document and return its report mapping."""
    text = read_input(args.input)
    data, failure = parse(text)
    if failure:
        errors = []
        extraction_rules.check_text_form(text, errors)
        return {"valid": False, "errors": errors + [failure], "font_entries": 0,
                "live_fonts_checked": False, "confidence_markers": 0}
    errors, entries = extraction_rules.validate(data, text, args.min_rarity_percentile)
    markers = check_markers(data, args.min_confidence_markers, errors) if data else 0
    live = False
    if not args.no_live_fonts and entries:
        live = add_live_errors(entries, args.min_rarity_percentile, errors)
    return {"valid": not errors, "errors": errors, "live_fonts_checked": live,
            "confidence_markers": markers, "font_entries": len(entries)}


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        report = run(args)
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
