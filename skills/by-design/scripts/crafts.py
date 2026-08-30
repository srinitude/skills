#!/usr/bin/env python3
"""Measure how far this skill reaches across design occupations.

Two questions, kept apart because they are not the same question. Can the gate
admit a craft and can the index place it, and once placed, does that shelf talk
about the craft in the craft's own words.

Exit codes:
  0  the coverage was printed
  1  the occupation file is missing
  2  usage or input error

Examples:
  python3 scripts/crafts.py
  python3 scripts/crafts.py --thin
"""
import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import gate
import locate
import slice as slicer
import yamlread

SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
CRAFTS = SKILL_DIR / "evals" / "files" / "occupations.json"
WORD = re.compile(r"[a-z][a-z-]{4,}")
STRONG = 5
THIN = 3


def coverage(entries, terms):
    """How many design occupations the gate admits and the index can place.

    One line of real work per occupation, written in that trade's words, from a
    published list of design occupations plus the disciplines that list is too
    old to name. This is the measure of whether the skill is for design or only
    for screens.
    """
    jobs = json.loads(CRAFTS.read_text(encoding="utf-8"))
    admitted = first = within = 0
    for name in sorted(jobs):
        task, shelf = jobs[name]["task"], jobs[name]["shelf"]
        admitted += gate.verdict(gate.score(task, terms))[0] == "design"
        found = [row[1] for row in locate.rank(task, entries) if row[0] > 0]
        spot = found.index(shelf) + 1 if shelf in found else 0
        first += spot == 1
        within += 1 <= spot <= 3
    return {"crafts_gated": admitted, "crafts_top1": first,
            "crafts_top3": within, "crafts_total": len(jobs)}


def shelf_text(shelf, index, cache):
    """Return every question on one shelf as one searchable line each."""
    if shelf not in cache:
        rows = yamlread.load(SKILL_DIR / "assets" / "questions" / index[shelf], "questions")
        cache[shelf] = [slicer.haystack(row) for row in rows]
    return cache[shelf]


def thin():
    """Count the crafts whose own words barely appear on their own shelf.

    Placing a craft is not the same as serving it. This counts how many of a
    craft's words turn up in at least five questions on the shelf it was sent
    to, and calls the craft thin when fewer than three do. It is the measure
    that says where the library is shallow rather than where it is silent.
    """
    jobs = json.loads(CRAFTS.read_text(encoding="utf-8"))
    index = {row["name"]: row["file"] for row in
             yamlread.load(SKILL_DIR / "assets" / "index.yaml", "categories")}
    cache = {}
    thin = []
    for name in sorted(jobs):
        lines = shelf_text(jobs[name]["shelf"], index, cache)
        words = dict.fromkeys(WORD.findall(jobs[name]["task"].lower()))
        strong = [w for w in words if sum(1 for line in lines if w in line) >= STRONG]
        if len(strong) < THIN:
            thin.append(name)
    return thin


def build_parser():
    parser = argparse.ArgumentParser(
        description="Report how far this skill reaches across design occupations.",
        epilog="exit codes: 0 printed, 1 missing occupation file, 2 usage error")
    parser.add_argument("--thin", action="store_true",
                        help="list the crafts their own shelf serves thinly")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not CRAFTS.is_file():
        sys.stderr.write(f"no occupation file at {CRAFTS}\n")
        return 1
    if args.thin:
        for name in thin():
            sys.stdout.write(name + "\n")
        return 0
    reach = coverage(locate.load_index(), gate.load_terms())
    for key in sorted(reach):
        sys.stdout.write(f"{key} {reach[key]}\n")
    sys.stdout.write(f"crafts_thin {len(thin())}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
