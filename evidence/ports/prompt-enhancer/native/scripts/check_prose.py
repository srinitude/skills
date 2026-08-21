#!/usr/bin/env python3
"""Run the deterministic writing-quality checks, or print the full law.

Reads prose from a file argument or stdin. Counts pattern hits by category,
then applies the convergence rule: single hits mean nothing; clusters are the
signal. Prints per-category findings with line numbers, then measured
properties that carry no verdict on their own.

--guide prints the judgment half of the writing-quality law: what wastes a
reader, what carries a person, and what must never be faked. Run it at step 4
when the prompt's output is prose, and write its constraints into the prompt.

Exit 0 when no cluster forms, 2 when the convergence rule fires, 1 on usage
errors. Signals, not verdicts: judge every result against the genre's own
norms. The written rules decide.

Usage:
    python3 check_prose.py [file]
    cat draft.txt | python3 check_prose.py
    python3 check_prose.py --guide
"""
import re
import statistics
import sys

GUIDE = """WRITING QUALITY — the judgment half. Write these into the prompt
when its output is prose; apply them to your own "What changed" bullets.

THE TEST THAT OUTRANKS THE REST
After reading, the reader should hold something they did not have before: a
claim they could check, a decision they could act on, a detail they could not
have looked up. Text that reads smoothly but leaves nothing behind fails,
whatever its style. Make the enhanced prompt demand that residue: name what
the output must let the reader do or verify.

WHAT WASTES THE READER (the scan half of this script measures these; judge
by clusters against the genre's own norms — a single instance means nothing)
- Claims with no way to check them: no names, numbers, dates, or sources.
- Effort pushed downstream: it looks finished, and the reader must
  interpret, verify, or redo the work to use it.
- Unnamed authority; filler frames; praise words standing in for detail;
  significance tags bolted onto sentences; manufactured revelation as a
  reflex; templated symmetry; more words than content.

WHAT CARRIES A PERSON (ask the target for these where the format supports
them; the author must supply what only they have)
- Particulars the author could only know by being there. Detail a search
  could return is information; detail it could not return is presence.
- A position: one side taken, a prediction that could be wrong, a preference
  with a reason. Symmetric hedging closed by a tidy summary reads as no one
  home.
- Named sources a reader can follow, cited precisely enough that finding
  them took work.
- Structure that follows care: depth where the author knows most, brisk
  elsewhere. Balance imposed for its own sake reads as empty.
- Details allowed to stand without an appended interpretation.
- Register true to the occasion, including real informality where the genre
  has it.
- Honest unresolvedness: an open question left open beats a balanced
  conclusion that resolves nothing.
- Emotion carried by incident, not named: the moment that made it sad, not
  the word "poignant".

NEVER FAKE IT
- Never ask for inserted errors or roughness as proof of effort.
- Never ask for casual style as a substitute for substance.
- Never ask for invented first-person stories. An anecdote counts only when
  it is true and checkable; the prompt can ask its author for a real one.
- Never read these lists as accusations. Formal register, careful hedging in
  careful genres, and polished mechanics are legitimate wherever they are
  native. The lists judge whether text serves its reader, not how it was
  made."""

MAX_BYTES = 5_000_000

CATEGORIES = {
    "unnamed authority": [
        r"\bexperts?\s+(say|argue|agree|believe|warn)\b",
        r"\bstudies\s+(show|suggest|indicate)\b",
        r"\bresearch\s+(shows|suggests|indicates)\b",
        r"\bobservers\s+have\b", r"\bindustry\s+reports?\b",
        r"\bmany\s+(believe|argue|say)\b", r"\bwidely\s+regarded\b",
        r"\bsome\s+critics?\b",
    ],
    "filler frames": [
        r"\bit'?s\s+worth\s+noting\b", r"\bit\s+is\s+important\s+to\s+note\b",
        r"\bin\s+today'?s\b", r"\bin\s+the\s+ever-evolving\b",
        r"\bat\s+the\s+end\s+of\s+the\s+day\b", r"\bneedless\s+to\s+say\b",
        r"\bin\s+conclusion\b", r"\bgreat\s+question\b",
    ],
    "praise words standing in for detail": [
        r"\bvital\b", r"\bcrucial\b", r"\bpivotal\b", r"\bremarkable\b",
        r"\btestament\b", r"\bvibrant\b", r"\bgame-chang\w+\b",
        r"\btransformative\b",
    ],
    "significance tags": [
        r",\s+(highlighting|underscoring|showcasing|reflecting|cementing|emphasizing)\b[^.]*\.",
    ],
    "manufactured revelation": [
        r"\b(it'?s|is|are|was|isn'?t)\s+not\s+(just|only|merely)\b",
        r"\bnot\s+only\b[^.]*\bbut\s+(also\s+)?",
    ],
    "copula avoidance": [
        r"\bserves\s+as\b", r"\bstands\s+as\b", r"\bfunctions\s+as\b",
        r"\bboasts\b",
    ],
    "inflated diction": [
        r"\bdelve\b", r"\btapestry\b", r"\bleverag\w+\b", r"\bseamless\w*\b",
        r"\bintricate\b", r"\bmeticulous\w*\b", r"\bfoster\w*\b",
        r"\belevate\w*\b", r"\bunderscore\w*\b",
    ],
    "transition stacking": [
        r"(?m)^\s*(Moreover|Furthermore|Additionally|Overall),",
    ],
}


def category_hits(text: str):
    hits = {}
    for name, patterns in CATEGORIES.items():
        found = []
        for number, line in enumerate(text.splitlines(), start=1):
            for pattern in patterns:
                for match in re.finditer(pattern, line, re.I):
                    found.append((number, match.group(0)[:40]))
        if found:
            hits[name] = found
    return hits


def measurements(text: str):
    words = max(1, len(text.split()))
    sentences = [s for s in re.split(r"[.!?]+\s", text) if s.strip()]
    lengths = [len(s.split()) for s in sentences]
    spread = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0
    dashes = text.count("—") * 1000 / words
    numerals = len(re.findall(r"\b\d[\d,.]*\b", text)) * 1000 / words
    triads = len(re.findall(r"\b\w+, \w+, and \w+\b", text))
    return [
        f"sentence-length spread {spread:.1f} (low spread = uniform rhythm; weigh lightly)",
        f"em-dashes per 1000 words {dashes:.1f} (weak signal alone)",
        f"numerals per 1000 words {numerals:.1f} (few = little checkable detail; genre-dependent)",
        f"three-item lists {triads} (a habit only when most lists come in threes)",
    ]


def main() -> int:
    if "--guide" in sys.argv:
        print(GUIDE)
        return 0
    if len(sys.argv) > 2:
        print("usage: check_prose.py [file | --guide]  (or pipe text on stdin)", file=sys.stderr)
        return 1
    if len(sys.argv) == 2:
        try:
            with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as handle:
                text = handle.read(MAX_BYTES)
        except OSError as error:
            print(f"cannot read {sys.argv[1]}: {error}", file=sys.stderr)
            return 1
    else:
        text = sys.stdin.read(MAX_BYTES)
    if not text.strip():
        print("no input text; pass a file or pipe text on stdin", file=sys.stderr)
        return 1

    hits = category_hits(text)
    words = max(1, len(text.split()))
    clustered = [n for n, f in hits.items() if len(f) >= 2 or len(f) * 1000 / words >= 4]

    for name, found in hits.items():
        marker = "CLUSTER" if name in clustered else "note   "
        for number, sample in found[:6]:
            print(f"{marker} line {number}: {name} ({sample})")
    for line in measurements(text):
        print(f"measure {line}")

    converged = len(clustered) >= 2
    print()
    print("Signals, not verdicts. Judge clusters against the genre's own norms.")
    if converged:
        print(f"Convergence: {len(clustered)} categories cluster ({', '.join(clustered)}).")
        print("Rework the flagged passages toward checkable detail; the written rules decide.")
        return 2
    print("No convergence: no rework required by this check.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
