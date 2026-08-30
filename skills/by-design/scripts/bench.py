#!/usr/bin/env python3
"""Measure the skill against every recorded case and refuse a result that got worse.

Real work becomes a fixture, a fixture becomes a number, and the number only
moves up. Run this after any change to the vocabulary, the term index or the
scoring, and after adding a brief from a job you actually did.

Exit codes:
  0  every measure met or beat the recorded baseline
  1  at least one measure fell, each named on its own line
  2  usage or input error, or a fixture is missing

Examples:
  python3 scripts/bench.py
  python3 scripts/bench.py --update
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import crafts
import gate
import locate
import yamlread

SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
DISC = SKILL_DIR / "evals" / "files"
NEG = SKILL_DIR / "evals" / "files" / "non-design.json"
BASE = SKILL_DIR / "evals" / "baseline.json"


def gate_recall(terms):
    """Share of every question in the library the gate lets through.

    Measured over all of them rather than a sample. A sample of 30 per category
    reported a clean 100% while 15 questions were in fact being stopped, which
    is the one thing this number exists to notice.
    """
    entries = yamlread.load(SKILL_DIR / "assets" / "index.yaml", "categories")
    passed = total = 0
    for entry in entries:
        rows = yamlread.load(SKILL_DIR / "assets" / "questions" / entry["file"], "questions")
        for row in rows:
            total += 1
            if gate.verdict(gate.score(row["question"], terms))[0] == "design":
                passed += 1
    return round(passed / total, 5), total


def gate_precision(terms):
    """Share of recorded non-design requests the gate stops."""
    requests = json.loads(NEG.read_text(encoding="utf-8"))
    stopped = sum(1 for text in requests
                  if gate.verdict(gate.score(text, terms))[0] == "not-design")
    return round(stopped / len(requests), 4), len(requests)


def positions(expected, entries):
    """Rank position of each expected shelf, 0 when it never appears.

    Position is finer than a top-three flag. A weakened term index usually moves
    a shelf from second to fifth long before it drops out of the top three, and
    the coarse flag reports that run as unchanged.
    """
    place = {}
    for name, shelf in sorted(expected.items()):
        text = (DISC / f"brief-{name}.txt").read_text(encoding="utf-8")
        ranked = [row[1] for row in locate.rank(text, entries) if row[0] > 0]
        place[name] = ranked.index(shelf) + 1 if shelf in ranked else 0
    return place


def locate_scores(entries):
    """Top-1 accuracy, top-3 accuracy and every fixture's rank position."""
    expected = json.loads((DISC / "briefs.json").read_text(encoding="utf-8"))
    place = positions(expected, entries)
    first = sum(1 for spot in place.values() if spot == 1)
    within = sum(1 for spot in place.values() if 1 <= spot <= 3)
    per = {name: 1 <= spot <= 3 for name, spot in place.items()}
    return first, within, len(expected), per, place


def signals(expected, entries):
    """Count the wrong first places that stayed silent, and the right ones that did.

    A ranking that is wrong and silent is the expensive failure, because it
    reads as decided. A ranking that is right and warns costs one hint. Counted
    rather than expressed as a share, because adding fixtures moves a share for
    reasons that have nothing to do with the change being measured.
    """
    silent = quiet = 0
    for name, shelf in sorted(expected.items()):
        ranked = locate.rank((DISC / f"brief-{name}.txt").read_text(encoding="utf-8"), entries)
        noisy = bool(locate.weakness(ranked, ""))
        if ranked[0][1] == shelf:
            quiet += 0 if noisy else 1
        else:
            silent += 0 if noisy else 1
    return silent, quiet


def measure():
    """Return every measure as one flat mapping."""
    terms = gate.load_terms()
    recall, n_recall = gate_recall(terms)
    precision, n_precision = gate_precision(terms)
    entries = locate.load_index()
    first, within, total, per, place = locate_scores(entries)
    expected = json.loads((DISC / "briefs.json").read_text(encoding="utf-8"))
    silent, quiet = signals(expected, entries)
    reach = crafts.coverage(entries, terms)
    reach["crafts_thin"] = len(crafts.thin())
    return {"silent_when_wrong": silent, "quiet_when_right": quiet, **reach,
            "gate_recall": recall, "gate_recall_n": n_recall,
            "gate_precision": precision, "gate_precision_n": n_precision,
            "locate_top1": first, "locate_top3": within, "locate_total": total,
            "per_fixture": per, "per_rank": place}


UP = ["gate_recall", "gate_precision", "locate_top1", "locate_top3",
      "quiet_when_right", "crafts_gated", "crafts_top1", "crafts_top3"]
DOWN = ["silent_when_wrong", "crafts_thin"]


def slipped(now, base):
    """Return one line per fixture whose expected shelf now ranks lower."""
    lines = []
    for name, was in sorted(base.get("per_rank", {}).items()):
        got = now["per_rank"].get(name, 0)
        if not was:
            continue
        if not got:
            lines.append(f"fixture {name} lost its shelf, which used to rank {was}")
        elif got > was:
            lines.append(f"fixture {name} slipped from rank {was} to {got}")
    return lines


def compare(now, base):
    """Return one line per measure that fell below the recorded baseline."""
    fallen = []
    for key in UP:
        if now[key] < base.get(key, 0):
            fallen.append(f"{key} fell from {base[key]} to {now[key]}")
    for key in DOWN:
        if now[key] > base.get(key, now[key]):
            fallen.append(f"{key} rose from {base[key]} to {now[key]}")
    for name, passed in sorted(base.get("per_fixture", {}).items()):
        if passed and not now["per_fixture"].get(name, False):
            fallen.append(f"fixture {name} used to land and no longer does")
    return fallen + slipped(now, base)


def report(now):
    sys.stdout.write(
        f"gate recall     {now['gate_recall']*100:6.3f}%  over {now['gate_recall_n']} questions\n"
        f"gate precision  {now['gate_precision']*100:5.1f}%  over {now['gate_precision_n']} requests\n"
        f"locate top 1    {now['locate_top1']}/{now['locate_total']}\n"
        f"locate top 3    {now['locate_top3']}/{now['locate_total']}\n"
        f"wrong and silent {now['silent_when_wrong']}   right and quiet "
        f"{now['quiet_when_right']}\n"
        f"crafts gated    {now['crafts_gated']}/{now['crafts_total']}   placed first "
        f"{now['crafts_top1']}   in the top three {now['crafts_top3']}\n"
        f"crafts thinly served by their shelf {now['crafts_thin']}\n")
    for name, spot in sorted(now["per_rank"].items()):
        where = str(spot) if spot else "unranked"
        sys.stdout.write(f"  {name:<16} rank {where}\n")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Measure the skill and refuse a result that got worse.",
        epilog="exit codes: 0 held or improved, 1 something fell, 2 usage error")
    parser.add_argument("--update", action="store_true",
                        help="record the current result as the new baseline")
    args = parser.parse_args(argv)
    if not DISC.is_dir() or not NEG.is_file():
        sys.stderr.write("fixtures are missing under evals/files/\n")
        return 2
    now = measure()
    report(now)
    if not BASE.is_file():
        BASE.write_text(json.dumps(now, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        sys.stdout.write("no baseline existed, so this run became it\n")
        return 0
    base = json.loads(BASE.read_text(encoding="utf-8"))
    fallen = compare(now, base)
    for line in fallen:
        sys.stdout.write(line + "\n")
    if fallen and not args.update:
        return 1
    if args.update:
        BASE.write_text(json.dumps(now, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        sys.stdout.write("baseline updated\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
