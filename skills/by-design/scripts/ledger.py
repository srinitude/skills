#!/usr/bin/env python3
"""Create, append to, and read a decision ledger file.

The ledger is the skill's only memory. It holds one row per decision and
survives between sessions, which is what lets the skill stay quiet about a
class of decision the user has already made well.

Exit codes:
  0  the command succeeded
  1  the ledger file is missing or holds no rows
  2  usage or input error

Examples:
  python3 scripts/ledger.py init --file decision-ledger-checkout.md --slug checkout
  python3 scripts/ledger.py add --file decision-ledger-checkout.md --decision "Row height" --origin inherited
  python3 scripts/ledger.py count --file decision-ledger-checkout.md --decision "Row height"
"""
import argparse
import pathlib
import re
import sys

COLUMNS = ["The decision", "What was chosen", "What it trades away",
           "What it risks", "Deliberate or inherited", "What would change it",
           "Source"]
ORIGINS = ["deliberate", "inherited", "open"]


def header(slug):
    """Return the opening block of a fresh ledger."""
    rule = "|".join(["---"] * len(COLUMNS))
    return "\n".join([
        f"# Decision ledger: {slug}",
        "",
        "One row per decision. A row marked inherited is a choice nobody made on purpose.",
        "",
        "| " + " | ".join(COLUMNS) + " |",
        "|" + rule + "|",
        "",
    ])


def cell(value):
    """Make one field safe to sit inside a markdown table cell."""
    text = (value or "").replace("|", "/").replace("\n", " ").strip()
    return text or "-"


def phrase(text, wanted):
    """Report whether wanted sits inside text on word boundaries."""
    if not wanted:
        return False
    pattern = r"(?<![a-z0-9])" + re.escape(wanted) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def names(line, wanted):
    """Report whether one row records this decision.

    The whole row used to be searched, so a short decision matched any row whose
    other columns happened to contain those letters, and the count that decides
    whether this skill speaks was inflated by its own trade-off text.
    """
    parts = [part.strip().lower() for part in line.strip().strip("|").split("|")]
    written = parts[0] if parts else ""
    asked = (wanted or "").strip().lower()
    if not written or written == "the decision":
        return False
    return phrase(written, asked) or phrase(asked, written)


def row_for(args):
    fields = [args.decision, args.chosen, args.trades, args.risks,
              args.origin, args.falsifier, args.source]
    return "| " + " | ".join(cell(field) for field in fields) + " |"


def do_init(args):
    path = pathlib.Path(args.file)
    if path.exists():
        sys.stderr.write(f"ledger already exists at {path}\n")
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(header(args.slug), encoding="utf-8")
    sys.stdout.write(f"created {path}\n")
    return 0


def do_add(args):
    path = pathlib.Path(args.file)
    if not args.decision:
        sys.stderr.write("add needs --decision\n")
        return 2
    if args.origin not in ORIGINS:
        sys.stderr.write(f"origin must be one of: {', '.join(ORIGINS)}\n")
        return 2
    if not path.exists():
        path.write_text(header(args.slug or path.stem), encoding="utf-8")
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(row_for(args) + "\n")
    sys.stdout.write(f"appended to {path}\n")
    return 0


def read_rows(path):
    """Return every data row of the ledger table, header excluded."""
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    return [line for line in lines
            if line.startswith("| ") and not line.startswith("| The decision")]


def do_show(args):
    rows = read_rows(pathlib.Path(args.file))
    if rows is None:
        sys.stderr.write(f"no ledger at {args.file}\n")
        return 1
    sys.stdout.write("\n".join(rows) + "\n" if rows else "ledger is empty\n")
    return 0


def do_count(args):
    if not args.decision:
        sys.stderr.write("count needs --decision\n")
        return 2
    rows = read_rows(pathlib.Path(args.file))
    if rows is None:
        sys.stderr.write(f"no ledger at {args.file}\n")
        return 1
    hits = [row for row in rows if names(row, args.decision)]
    sys.stdout.write(f"{len(hits)}\n")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        description="Create, append to, and read a decision ledger.",
        epilog="exit codes: 0 success, 1 missing ledger, 2 usage error")
    parser.add_argument("command", choices=["init", "add", "show", "count"])
    parser.add_argument("--file", required=True)
    parser.add_argument("--slug", default="")
    parser.add_argument("--decision", default="")
    parser.add_argument("--chosen", default="")
    parser.add_argument("--trades", default="")
    parser.add_argument("--risks", default="")
    parser.add_argument("--origin", default="open")
    parser.add_argument("--falsifier", default="")
    parser.add_argument("--source", default="")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    actions = {"init": do_init, "add": do_add,
               "show": do_show, "count": do_count}
    return actions[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
