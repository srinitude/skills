#!/usr/bin/env python3
"""Select a small slice of design questions from the bundled question files.

Reads one category file, filters it by stage, artifact type, lens, seniority
and free text, then widens the pin when the result falls under the floor.
Every dropped coordinate is named on stderr, so a widened slice never passes
for the slice that was asked for. The same flags always produce the same
bytes: rows sort by confidence then by id, and both are fixed in the files.

Exit codes:
  0  a slice was produced
  1  no questions matched, even at the widest step
  2  usage or input error

Examples:
  python3 scripts/slice.py --category Accessibility --limit 15
  python3 scripts/slice.py --category "Forms and input" --stage pre-ship --lens ethics
  python3 scripts/slice.py --category "Motion, film and moving image" --format md
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import yamlread

SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
INDEX = SKILL_DIR / "assets" / "index.yaml"
SHARDS = SKILL_DIR / "assets" / "questions"
LADDER = ["lens", "applies_to", "stage"]
FLOOR = 12
MATCH_FLOOR = 5
LIMIT = 20


def read_index():
    """Return every category name mapped to its file name."""
    if not INDEX.is_file():
        sys.stderr.write(f"index not found at {INDEX}\n")
        raise SystemExit(2)
    entries = yamlread.load(INDEX, "categories")
    return {entry["name"]: entry["file"] for entry in entries}


def read_category(name, index):
    """Return every question in one category, or exit 2 on an unknown name."""
    if name not in index:
        sys.stderr.write(f"unknown category: {name}\n")
        raise SystemExit(2)
    return yamlread.load(SHARDS / index[name], "questions")


def keeps(row, pins):
    """Report whether one question satisfies every active pin."""
    if pins.get("stage") and row["stage"] != pins["stage"]:
        return False
    if pins.get("applies_to") and pins["applies_to"] not in row["applies_to"]:
        return False
    if pins.get("lens") and pins["lens"] not in row["secondary_tags"]:
        return False
    if pins.get("seniority") and row["seniority"] != pins["seniority"]:
        return False
    if pins.get("match") and pins["match"] not in haystack(row):
        return False
    return True


def haystack(row):
    parts = [row["question"], row["tension"], row["failure_it_catches"],
             row.get("subcategory", "")]
    return " ".join(parts).lower()


def relax(rows, active, dropped, target):
    """Drop each coordinate in turn until the slice reaches the target."""
    hits = [row for row in rows if keeps(row, active)]
    for coordinate in LADDER:
        if len(hits) >= target or not active.get(coordinate):
            continue
        active[coordinate] = None
        dropped.append(coordinate.replace("_", "-"))
        hits = [row for row in rows if keeps(row, active)]
    return hits


def widen(rows, pins, floor):
    """Widen the pin until the slice is worth reading.

    The free text match earns its keep, so the other coordinates go first and
    the match goes last. A match that hit once used to be returned as the whole
    slice, which read as a precise answer and was one question.
    """
    dropped = []
    active = dict(pins)
    target = MATCH_FLOOR if active.get("match") else floor
    hits = relax(rows, active, dropped, target)
    if len(hits) >= target or not active.get("match"):
        return hits, dropped
    active["match"] = None
    dropped.append("match")
    return relax(rows, active, dropped, floor), dropped


def plain(text, joiner=", "):
    """Replace long dashes so output stays quotable in plain markdown."""
    out = (text or "").replace(" — ", joiner).replace(" – ", joiner)
    return out.replace("—", "-").replace("–", "-")


def flatten(row):
    """Return one question with every text field dash normalized."""
    copy = dict(row)
    for field in ("question", "tension", "failure_it_catches", "subcategory"):
        copy[field] = plain(row.get(field, ""))
    copy["source_name"] = cite(row)
    return copy


def cite(row):
    """Join the publisher and the title into one readable citation."""
    publisher = plain(row.get("source_publisher", ""), ": ")
    title = plain(row.get("source_title", ""), ": ")
    return f"{publisher}: {title}" if publisher and title else publisher or title


def rank(hits, limit):
    """Order by confidence then by id, which is a total order over the file."""
    ordered = sorted(hits, key=lambda row: (-row["confidence"], row["id"]))
    return [flatten(row) for row in ordered[:limit]]


def render_md(rows, dropped):
    lines = [f"# {len(rows)} questions"]
    if dropped:
        lines.append(f"Widened by dropping: {', '.join(dropped)}.")
    for row in rows:
        lines.append("")
        lines.append(f"**{row['question']}**")
        lines.append(f"- trades away: {row['tension']}")
        lines.append(f"- risks: {row['failure_it_catches']}")
        lines.append(f"- {row['category']} / {row['subcategory']} - {row['id']}")
        if row["source_url"]:
            lines.append(f"- source: {row['source_name']} {row['source_url']}")
    return "\n".join(lines)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Select a slice of design questions from the bundled files.",
        epilog="exit codes: 0 slice produced, 1 nothing matched, 2 usage error")
    parser.add_argument("--category", required=True)
    parser.add_argument("--stage")
    parser.add_argument("--applies-to", dest="applies_to")
    parser.add_argument("--lens")
    parser.add_argument("--seniority")
    parser.add_argument("--match")
    parser.add_argument("--limit", type=int, default=LIMIT)
    parser.add_argument("--floor", type=int, default=FLOOR)
    parser.add_argument("--format", choices=["json", "md"], default="md")
    return parser


def collect(args):
    """Turn parsed flags into the pin mapping the filters read."""
    return {"stage": args.stage, "applies_to": args.applies_to,
            "lens": args.lens, "seniority": args.seniority,
            "match": args.match.lower() if args.match else None}


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.limit < 1 or args.floor < 1:
        sys.stderr.write("limit and floor must be 1 or greater\n")
        return 2
    rows = read_category(args.category, read_index())
    hits, dropped = widen(rows, collect(args), args.floor)
    if not hits:
        sys.stderr.write("no questions matched, even at the widest step\n")
        return 1
    if dropped:
        sys.stderr.write(f"widened: dropped {', '.join(dropped)}\n")
    picked = rank(hits, args.limit)
    if args.format == "md":
        sys.stdout.write(render_md(picked, dropped) + "\n")
    else:
        payload = {"count": len(picked), "widened": dropped, "questions": picked}
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=1,
                                    sort_keys=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
