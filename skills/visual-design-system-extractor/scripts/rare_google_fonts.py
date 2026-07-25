#!/usr/bin/env python3
"""Find and verify rare Google Fonts families against the live catalog.

Every answer comes from the family metadata feed read at run time, so a
family that grew popular stops qualifying without any edit to this skill.

Commands:
  catalog   Write a snapshot of the live catalog as JSON.
  discover  Rank the rarest families that match the given filters.
  verify    Check that each named family exists and clears the rarity bar.

Exit codes:
  0  the command succeeded and every named family passed
  1  a named family is missing, too popular, or the live feed failed
  2  usage or input error

Examples:
  python3 scripts/rare_google_fonts.py discover --category Serif --limit 5
  python3 scripts/rare_google_fonts.py verify --family "Rubik Puddles"
"""
from __future__ import annotations

import argparse
import json
import sys

import font_selection
from google_fonts_api import FEED_URL, FeedError, find, load_catalog, rarity_block


def add_shared(parser):
    """Attach the flags every command accepts."""
    parser.add_argument("--url", default=FEED_URL, help="live metadata feed URL")
    parser.add_argument("--timeout", type=int, default=30, help="feed timeout in seconds")
    parser.add_argument("--output", help="write JSON here instead of stdout")


def add_filters(parser):
    """Attach the discover filters that map onto live feed fields."""
    parser.add_argument("--category", help="feed category, such as Serif or Display")
    parser.add_argument("--subset", help="required subset, such as latin-ext")
    parser.add_argument("--search", help="substring of the family name")
    parser.add_argument("--variable-only", action="store_true", help="require axes")
    parser.add_argument("--added-after", help="keep families added after YYYY-MM-DD")
    parser.add_argument("--include-noto", action="store_true", help="keep Noto families")
    parser.add_argument("--limit", type=int, default=font_selection.DEFAULT_LIMIT)
    parser.add_argument(
        "--min-rarity-percentile",
        type=float,
        default=font_selection.DEFAULT_MIN_PERCENTILE,
        help="lowest rarity percentile a family may hold. Default: 70.0",
    )


def build_parser():
    """Return the argument parser for every command."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    commands = parser.add_subparsers(dest="command", required=True)
    add_shared(commands.add_parser("catalog", help="snapshot the live catalog"))
    discover = commands.add_parser("discover", help="rank rare families")
    add_shared(discover)
    add_filters(discover)
    verify = commands.add_parser("verify", help="check named families")
    add_shared(verify)
    add_filters(verify)
    verify.add_argument("--family", action="append", required=True, help="family name")
    return parser


def criteria_from(args):
    """Return selection criteria built from parsed flags."""
    return font_selection.build_criteria(
        category=args.category,
        subset=args.subset,
        search=args.search,
        min_percentile=args.min_rarity_percentile,
        variable_only=args.variable_only or None,
        added_after=args.added_after,
        exclude_noto=False if args.include_noto else None,
        limit=args.limit,
    )


def emit(payload, output):
    """Write JSON to stdout or to the requested path."""
    text = json.dumps(payload, indent=2, sort_keys=True)
    if output:
        with open(output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
        return
    print(text)


def run_catalog(args, catalog):
    """Write the full live snapshot."""
    emit(catalog, args.output)
    return 0


def run_discover(args, catalog):
    """Write the ranked rare candidates that match the filters."""
    chosen = font_selection.select(catalog, criteria_from(args))
    payload = {
        "source": catalog["source"],
        "retrieved_at": catalog["retrieved_at"],
        "total_families": catalog["total_families"],
        "candidates": [
            {"family": item["family"], "category": item["category"],
             "rarity": rarity_block(item, catalog)}
            for item in chosen
        ],
    }
    emit(payload, args.output)
    return 0


def check_family(name, catalog, floor):
    """Return one verdict mapping for a single family name."""
    item = find(catalog, name)
    if item is None:
        return {"family": name, "status": "FAIL",
                "reason": "not a Google Fonts family in the live catalog"}
    if item["rarity_percentile"] < floor:
        return {"family": item["family"], "status": "FAIL",
                "reason": f"rarity percentile {item['rarity_percentile']} is below {floor}",
                "rarity": rarity_block(item, catalog)}
    return {"family": item["family"], "status": "PASS",
            "rarity": rarity_block(item, catalog)}


def run_verify(args, catalog):
    """Write one verdict per named family and fail on any rejection."""
    floor = args.min_rarity_percentile
    verdicts = [check_family(name, catalog, floor) for name in args.family]
    failed = [item for item in verdicts if item["status"] == "FAIL"]
    emit({"checked": len(verdicts), "failed": len(failed), "verdicts": verdicts}, args.output)
    return 1 if failed else 0


COMMANDS = {"catalog": run_catalog, "discover": run_discover, "verify": run_verify}


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        catalog = load_catalog(args.url, args.timeout)
    except FeedError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return COMMANDS[args.command](args, catalog)


if __name__ == "__main__":
    sys.exit(main())
