#!/usr/bin/env python3
"""Decide whether a request touches design work, before any other step runs.

Continues by default and stops only when a request clearly belongs to another
craft and names no design surface. Design conversation runs on ordinary words,
so a list of design nouns can never recognise all of it, and letting a
borderline request through costs one ledger row while stopping one costs a
decision nobody recorded. The matched terms print alongside the verdict so the
answer can be checked, and the same request always gets the same answer.

Exit codes:
  0  a verdict was printed, either design or not-design
  1  the vocabulary file is missing
  2  usage or input error

Examples:
  python3 scripts/gate.py --text "review this checkout screen"
  echo "what time is my next meeting" | python3 scripts/gate.py
"""
import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import yamlread

SKILL_DIR = pathlib.Path(__file__).resolve().parents[1]
TERMS = SKILL_DIR / "assets" / "gate-terms.yaml"
TIERS = ["strong", "weak", "verbs", "exclusions"]
SURFACE = ["strong"]


def load_terms():
    """Return every tier of the vocabulary, each as a sorted list."""
    if not TERMS.is_file():
        sys.stderr.write(f"vocabulary not found at {TERMS}\n")
        raise SystemExit(1)
    return {tier: sorted(entry["name"] for entry in yamlread.load(TERMS, tier))
            for tier in TIERS}


def holds(lowered, term):
    """Match a term on word boundaries, so apprenticeship never counts as ship."""
    pattern = r"(?<![a-z])" + re.escape(term) + r"(?:s|es)?(?![a-z])"
    return re.search(pattern, lowered) is not None


def score(text, terms):
    """Return every matched term, tier by tier, in fixed order."""
    lowered = f" {text.lower()} "
    matched = []
    for tier in TIERS:
        for term in terms[tier]:
            if holds(lowered, term):
                matched.append(f"{tier}:{term}")
    return matched


def independent(surfaces, blocks):
    """Drop a surface term that sits inside a matched exclusion phrase.

    The word push is a design surface and it is also half of git push, so a
    term swallowed by a named craft is not evidence of its own.
    """
    phrases = [m.split(":", 1)[1] for m in blocks]
    return [m for m in surfaces
            if not any(m.split(":", 1)[1] in phrase for phrase in phrases)]


def verdict(matched):
    """Continue unless another craft is named and no design surface appears.

    Only the strong tier overrides an exclusion. A weak noun or a bare verb is
    too common in other crafts to outrank a named one.
    """
    surfaces = [m for m in matched if m.split(":")[0] in SURFACE]
    signals = [m for m in matched if not m.startswith("exclusions:")]
    blocks = [m for m in matched if m.startswith("exclusions:")]
    surfaces = independent(surfaces, blocks)
    if blocks and not surfaces:
        return "not-design", f"another craft named, matched {', '.join(blocks)}"
    if blocks:
        return "design", f"design surface overrides {', '.join(blocks)}, matched {', '.join(surfaces)}"
    if signals:
        return "design", f"matched {', '.join(signals)}"
    return "design", "no other craft named, so the request stays in scope"


def build_parser():
    parser = argparse.ArgumentParser(
        description="Decide whether a request touches design work.",
        epilog="exit codes: 0 verdict printed, 1 missing vocabulary, 2 usage error")
    parser.add_argument("--text", help="the request; omit to read stdin")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    text = args.text if args.text is not None else sys.stdin.read()
    if not text.strip():
        sys.stderr.write("no request text given\n")
        return 2
    call, reason = verdict(score(text, load_terms()))
    sys.stdout.write(f"{call}: {reason}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
