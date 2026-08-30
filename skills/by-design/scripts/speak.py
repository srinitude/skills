#!/usr/bin/env python3
"""Decide whether one decision earns a question, using the ledger as the record.

The three tests are counted here rather than judged in the moment, so the same
decision and the same ledger always give the same answer. Run this once per
decision before writing any question into a reply.

Exit codes:
  0  a verdict was printed, either ask or hold
  1  the ledger file is missing
  2  usage or input error

Examples:
  python3 scripts/speak.py --file decision-ledger-orders.md --decision "Row height" --origin inherited --live yes
  python3 scripts/speak.py --file decision-ledger-orders.md --rank
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ledger

BUDGET = 3
ORIGINS = ["deliberate", "inherited", "open"]


def rows_for(path, decision):
    """Return every ledger row that already names this decision."""
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line for line in lines
            if line.startswith("| ") and ledger.names(line, decision)]


def verdict(rows, origin, live):
    """Return ask or hold with the reason, from counts alone."""
    if live != "yes":
        return "hold", "the decision is not being made right now"
    if origin != "inherited":
        return "hold", f"the choice is marked {origin}, so the question is not needed"
    settled = [line for line in rows if "| deliberate |" in line]
    if len(rows) >= BUDGET:
        return "hold", f"recorded {len(rows)} times including this one, so raise it once at project level"
    if len(settled) >= BUDGET:
        return "hold", f"this class was decided on purpose {len(settled)} times already"
    seen = "once" if len(rows) == 1 else f"{len(rows)} times"
    return "ask", f"inherited, live, and recorded {seen} including this one"


def unknowns(line):
    """Count the empty columns in one ledger row."""
    return [cell.strip() for cell in line.split("|")].count("-")


def rank_rows(path):
    """Return every inherited row, least examined first, then in ledger order."""
    lines = path.read_text(encoding="utf-8").splitlines()
    rows = [line for line in lines
            if line.startswith("| ") and "| inherited |" in line]
    ordered = sorted(enumerate(rows), key=lambda pair: (-unknowns(pair[1]), pair[0]))
    return [line for _, line in ordered]


def do_rank(path):
    """Print the inherited rows in the order they earn a question."""
    rows = rank_rows(path)
    if not rows:
        sys.stdout.write("no inherited rows, so nothing earns a question\n")
        return 0
    for position, line in enumerate(rows, 1):
        name = line.split("|")[1].strip()
        gaps = unknowns(line)
        word = "column" if gaps == 1 else "columns"
        sys.stdout.write(f"{position}. {name} ({gaps} {word} unknown)\n")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        description="Decide whether one decision earns a question.",
        epilog="exit codes: 0 verdict printed, 1 missing ledger, 2 usage error")
    parser.add_argument("--file", required=True)
    parser.add_argument("--rank", action="store_true",
                        help="print inherited rows in the order they earn a question")
    parser.add_argument("--decision", default="")
    parser.add_argument("--origin", default="inherited", choices=ORIGINS)
    parser.add_argument("--live", default="yes", choices=["yes", "no"])
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    path = pathlib.Path(args.file)
    if not path.is_file():
        sys.stderr.write(f"no ledger at {path}\n")
        return 1
    if args.rank:
        return do_rank(path)
    if not args.decision.strip():
        sys.stderr.write("decision must hold text, or pass --rank\n")
        return 2
    call, reason = verdict(rows_for(path, args.decision), args.origin, args.live)
    sys.stdout.write(f"{call}: {reason}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
