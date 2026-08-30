#!/usr/bin/env python3
"""Propose the coordinates for a slice by reading the artifact instead of guessing.

Scores the artifact text against the distinctive terms of every category and
prints the ranked result, with the terms that earned each place. Picking the
category by hand is the step most likely to send a slice to the wrong shelf,
so this turns it into a reading of the work.

Exit codes:
  0  a ranking was printed
  1  the term index is missing
  2  usage or input error

Examples:
  python3 scripts/locate.py --file page.md
  python3 scripts/locate.py --text "out of stock notify me, checkout as guest" --top 3
  python3 scripts/locate.py --file brief.md --hint "moving image"
"""
import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import yamlread

SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
INDEX = SKILL_DIR / "assets" / "terms-index.yaml"
TRADE = SKILL_DIR / "assets" / "trade-terms.yaml"
CRAFTS = SKILL_DIR / "assets" / "disciplines.yaml"
TRADE_WEIGHT = 4.0
CRAFT_WEIGHT = 9.0
WORD = re.compile(r"[a-z][a-z-]{2,}")
CLOSE = 1.25
SUFFIX = ["ability", "ibility", "ableness", "ation", "ition", "ment", "ness",
          "able", "ible", "ings", "ing", "ies", "ed", "es", "s"]


def stem(word):
    """Strip one known ending, keeping at least four letters.

    The er and ers endings are deliberately absent. Stripping them turns header
    into head and ticker into tick, which loses the words a brief leans on.
    """
    for suffix in SUFFIX:
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            cut = word[:-len(suffix)]
            if len(cut) >= 4:
                return cut
    return word


def variants(word):
    """Return the forms of a word that a stored term could match.

    A plural of a word ending in e loses that e when the es ending comes off, so
    postcodes reached postcod while the index holds postcode. Both forms are
    offered rather than restemming the stored terms.
    """
    forms = {stem(word)}
    if word.endswith("es") and len(word) > 5 and word[-3] not in "sxzh":
        forms.add(word[:-1])
    return forms


def load_index():
    if not INDEX.is_file():
        sys.stderr.write(f"term index not found at {INDEX}\n")
        raise SystemExit(1)
    entries = yamlread.load(INDEX, "categories")
    return merged(merged(entries, TRADE, TRADE_WEIGHT), CRAFTS, CRAFT_WEIGHT)


def merged(entries, path, weight):
    """Add one hand written vocabulary file to each category's counted terms.

    Three sources stay in three files. One is counted from the questions, one
    holds the words a discipline uses for its work, and one holds the names of
    the disciplines themselves, which carry the most weight because naming your
    craft is the strongest thing you can say about where the questions are. A
    single word keeps its ending, and a term holding a space reads as a phrase.
    """
    if not path.is_file():
        return entries
    extra = {row["name"]: row["terms"] for row in yamlread.load(path, "categories")}
    for entry in entries:
        adding = [term for term in extra.get(entry["name"], [])
                  if term not in entry["terms"]]
        entry["terms"] = entry["terms"] + adding
        entry["weights"] = entry["weights"] + [weight] * len(adding)
    return entries


def boost(name, hint):
    """Return how much of the hint appears in a category name."""
    if not hint:
        return 0.0
    words = {stem(word) for word in WORD.findall(hint.lower())}
    parts = {stem(word) for word in WORD.findall(name.lower())}
    return float(len(words & parts))


def present(term, stems, plain, words):
    """Report whether one index term is in the text.

    A term holding a space is a phrase and is read against the words as written.
    A single word is tried against the stems and against the words as written,
    so a hand written trade word such as lighting keeps its ending and does not
    quietly become light. Whole word sets are used rather than a search per
    term, because the index now carries thousands of terms and the benchmark
    runs it ninety times.
    """
    if " " in term:
        return term in plain
    return term in stems or term in words


def written(text):
    """Return every word as written, plus the singular of each plural."""
    found = set()
    for word in WORD.findall(text):
        found.add(word)
        if word.endswith("es") and len(word) > 4:
            found.add(word[:-2])
        if word.endswith("s") and len(word) > 3:
            found.add(word[:-1])
    return found


def rank(text, entries, hint=""):
    """Score each category by the weight of its distinctive terms present in the text.

    Each term's weight is damped before it is added, so a category wins by
    matching several of its terms rather than one rare one. A single unusual
    word used to carry a whole ranking, which read as confidence and was not.
    """
    stems = set()
    for word in WORD.findall(text.lower()):
        stems |= variants(word)
    plain = " ".join(text.lower().split())
    words = written(plain)
    scored = []
    for entry in entries:
        weights = entry.get("weights") or [1.0] * len(entry["terms"])
        found = [(float(weights[i]), term)
                 for i, term in enumerate(entry["terms"])
                 if present(term, stems, plain, words)]
        total = sum(weight ** 0.5 for weight, _ in found)
        named = boost(entry["name"], hint)
        if named:
            hits_extra = ["hint"]
            total += named * 10.0
        else:
            hits_extra = []
        hits = hits_extra + [term for _, term in sorted(found, reverse=True)]
        scored.append((round(total, 2), entry["name"], hits))
    scored.sort(key=lambda row: (-row[0], row[1]))
    return scored


def weakness(scored, hint):
    """Return why a ranking should not be trusted, or an empty string.

    Two ways a place can look decided without being decided: it rests on one
    term, or the top two places are too close to separate. A place carried by a
    hint is neither, because the artifact type came from the person who has the
    work in front of them. The closeness figure was set by measuring every brief
    on file: it flags every ranking whose first place is wrong, and the two right
    ones it also flags cost a hint each, which is the cheaper mistake.
    """
    top = scored[0]
    terms = [term for term in top[2] if term != "hint"]
    if hint and "hint" in top[2]:
        return ""
    if len(terms) < 2:
        return "the top place rests on one term"
    if len(scored) > 1 and scored[1][0] and top[0] < CLOSE * scored[1][0]:
        return "the top two places are too close to separate"
    return ""


def read_text(args):
    if args.text is not None:
        return args.text
    if args.file:
        try:
            return pathlib.Path(args.file).read_text(encoding="utf-8")
        except OSError as problem:
            sys.stderr.write(f"cannot read {args.file}: {problem}\n")
            raise SystemExit(2)
    return sys.stdin.read()


def build_parser():
    parser = argparse.ArgumentParser(
        description="Propose slice coordinates by reading the artifact.",
        epilog="exit codes: 0 ranking printed, 1 missing index, 2 usage error")
    parser.add_argument("--text")
    parser.add_argument("--file")
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--hint", default="",
                        help="words naming the artifact type, for a weak read")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.top < 1:
        sys.stderr.write("top must be 1 or greater\n")
        return 2
    text = read_text(args)
    if not text.strip():
        sys.stderr.write("no artifact text given\n")
        return 2
    scored = rank(text, load_index(), args.hint)
    if scored[0][0] == 0:
        sys.stderr.write("no category matched this text; name the artifact type "
                         "in the request and run this again\n")
        return 1
    for total, name, hits in scored[:args.top]:
        if total == 0:
            break
        shown = ", ".join(hits[:6])
        sys.stdout.write(f"{total:6.2f}  {len(hits):2d} terms  {name}  [{shown}]\n")
    reason = weakness(scored, args.hint)
    if reason:
        sys.stderr.write(f"weak read: {reason}, so name the artifact type with "
                         "--hint and run this again\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
