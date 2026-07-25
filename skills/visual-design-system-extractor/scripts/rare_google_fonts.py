#!/usr/bin/env python3
"""Find and verify rare Google Fonts families against the live catalog.

Every answer comes from the family metadata feed read at run time, so a
family that grew popular stops qualifying without any edit to this skill.

Ranking runs fit first. A candidate must match the reference skeleton and
clear the legibility floor for its role before rarity is consulted, and
rarity only breaks a tie between candidates that already fit.

Commands:
  catalog   Write a snapshot of the live catalog as JSON.
  discover  Rank the families that fit the brief, rarest tie broken first.
  set       Fill every role of one design system as a paired set.
  verify    Check that each named family exists and clears the rarity bar.

Exit codes:
  0  the command succeeded and every named family passed
  1  a named family is missing, too popular, or the live feed failed
  2  usage or input error

Examples:
  python3 scripts/rare_google_fonts.py discover --skeleton Serif --need-weight 400
  python3 scripts/rare_google_fonts.py set --brief assets/font-brief.json
  python3 scripts/rare_google_fonts.py verify --family "Rubik Puddles"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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
    parser.add_argument("--skeleton", help="wanted skeleton, such as Serif")
    parser.add_argument("--role", help="text, display, mono, or accent")
    parser.add_argument("--need-weight", type=int, action="append", dest="weights",
                        help="weight the reference needs, repeatable")
    parser.add_argument("--need-italic", action="store_true", help="require italics")
    parser.add_argument("--min-fit", type=float, help="lowest fit score. Default: 0.65")
    parser.add_argument("--allow-common", action="store_true",
                        help="allow an overexposed default, needs --common-reason")
    parser.add_argument("--common-reason", help="why the common face is the true fit")
    parser.add_argument("--show-rejected", action="store_true",
                        help="list the candidates the fit bars dropped")
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
    chooser = commands.add_parser("set", help="fill every role as a paired set")
    add_shared(chooser)
    chooser.add_argument("--brief", required=True, help="path to the brief JSON")
    verify = commands.add_parser("verify", help="check named families")
    add_shared(verify)
    add_filters(verify)
    verify.add_argument("--family", action="append", required=True, help="family name")
    return parser


def criteria_from(args):
    """Return selection criteria built from parsed flags."""
    return font_selection.build_criteria(
        category=args.category,
        skeleton=args.skeleton,
        role=args.role,
        weights=args.weights,
        italic=args.need_italic or None,
        min_fit=args.min_fit,
        allow_common=args.allow_common or None,
        common_reason=args.common_reason,
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


def row_of(item, catalog):
    """Return one candidate row with its fit verdict and rarity block."""
    return {"family": item["family"], "category": item["category"],
            "fit": item["fit"], "rarity": rarity_block(item, catalog)}


def run_discover(args, catalog):
    """Write the candidates that fit, ranked by fit then by rarity."""
    criteria = criteria_from(args)
    payload = {
        "source": catalog["source"],
        "retrieved_at": catalog["retrieved_at"],
        "total_families": catalog["total_families"],
        "ranked_by": "fit_band descending, then rarity_percentile, then rank",
        "candidates": [row_of(item, catalog)
                       for item in font_selection.rank(catalog, criteria)],
    }
    if args.show_rejected:
        payload["rejected"] = [
            {"family": item["family"], "reason": item["reject_reason"],
             "rarity_percentile": item["rarity_percentile"]}
            for item in font_selection.rejected(catalog, criteria)[:args.limit]]
    emit(payload, args.output)
    return 0


def briefs_from(path):
    """Return the role briefs recorded in a brief file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    roles = data.get("roles_to_fill")
    if not isinstance(roles, list) or not roles:
        raise ValueError("the brief needs a roles_to_fill list of role objects")
    return [{"role": item["role"],
             "criteria": font_selection.build_criteria(**item.get("criteria", {}))}
            for item in roles]


def run_set(args, catalog):
    """Fill every role as one paired set and write the decision record."""
    try:
        briefs = briefs_from(args.brief)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    result = font_selection.choose_set(catalog, briefs)
    result["retrieved_at"] = catalog["retrieved_at"]
    emit(result, args.output)
    return 1 if result["unfilled"] or not result["pairing"]["passes"] else 0


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


COMMANDS = {"catalog": run_catalog, "discover": run_discover, "set": run_set,
            "verify": run_verify}


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
