#!/usr/bin/env python3
"""Check a drafted reply against the shape this skill promises, before it is sent.

Reads the draft from a file or from stdin and reports every rule it breaks.
Running this after drafting catches the case where the rules were understood
and the reply still broke them.

Exit codes:
  0  the draft passed every rule
  1  at least one rule was broken, each printed on its own line
  2  usage or input error

Examples:
  python3 scripts/check_reply.py --file draft.md
  python3 scripts/check_reply.py --file draft.md --ledger-dir .
  cat draft.md | python3 scripts/check_reply.py
"""
import argparse
import pathlib
import re
import sys

POSTURES = ["judge", "choose", "shape", "audit", "watch", "ask"]
MAX_QUESTIONS = 1
QUESTION_RE = re.compile(r"\?(\s|$)")
LEDGER_RE = re.compile(r"ledger:\s*(\S+?),\s*(\d+) rows added,\s*(\d+) marked inherited",
                       re.IGNORECASE)


def count_questions(text):
    """Count how many questions the draft puts to the reader."""
    return len(QUESTION_RE.findall(text))


def named_posture(text):
    """Return the posture the draft names, or an empty string."""
    lowered = text.lower()
    found = [name for name in POSTURES if f"posture: {name}" in lowered]
    return found[0] if found else ""


def tally(path):
    """Return how many decision rows a ledger holds and how many are inherited."""
    rows = [line for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith("| ") and not line.startswith("| The decision")]
    inherited = [line for line in rows if "| inherited |" in line]
    return len(rows), len(inherited)


def counted(text, folder):
    """Check the counts in the ledger line against the ledger on disk.

    Step 7 says to take the counts from a command rather than from memory. This
    is the check that says whether that happened, because a reply carrying a
    count nobody ran reads exactly like one that did. It also holds the reply to
    the rule in step 8: a question is earned by an inherited row, so a reply that
    asks one against a ledger holding none has overridden its own governor. The
    ask posture is exempt, since it returns a slice and leaves the ledger alone.
    """
    if named_posture(text) == "ask":
        return []
    found = LEDGER_RE.search(text)
    if not found:
        return ["ledger line does not read: Ledger: <path>, <n> rows added, <n> marked inherited"]
    path = pathlib.Path(folder) / found.group(1)
    if not path.is_file():
        return [f"the ledger named in the reply is not on disk at {path}"]
    rows, inherited = tally(path)
    said_rows, said_inherited = int(found.group(2)), int(found.group(3))
    notes = []
    if said_rows != rows:
        notes.append(f"reply says {said_rows} rows and the ledger holds {rows}")
    if said_inherited != inherited:
        notes.append(f"reply says {said_inherited} inherited and the ledger holds {inherited}")
    if inherited == 0 and count_questions(text):
        notes.append("the ledger holds no inherited row, so this reply has not earned its question")
    return notes


def problems_in(text, allow_full, folder="."):
    """Return every rule the draft breaks."""
    found = []
    if not text.strip():
        found.append("draft is empty")
        return found
    asked = count_questions(text)
    if asked > MAX_QUESTIONS and not allow_full:
        found.append(f"draft asks {asked} questions; the cap is {MAX_QUESTIONS}")
    if not named_posture(text):
        found.append("draft never names the posture, as 'Posture: judge'")
    if "ledger" not in text.lower():
        found.append("draft never names the ledger it wrote to")
        return found
    return found + counted(text, folder)


def build_parser():
    parser = argparse.ArgumentParser(
        description="Check a drafted reply against the rules of this skill.",
        epilog="exit codes: 0 passed, 1 rules broken, 2 usage error")
    parser.add_argument("--file")
    parser.add_argument("--full-slice", action="store_true",
                        help="allow many questions, for the ask posture")
    parser.add_argument("--ledger-dir", default="",
                        help="where the ledger named in the reply lives, default beside the draft")
    return parser


def read_draft(path):
    if path:
        try:
            return open(path, encoding="utf-8").read()
        except OSError as problem:
            sys.stderr.write(f"cannot read {path}: {problem}\n")
            raise SystemExit(2)
    return sys.stdin.read()


def main(argv=None):
    args = build_parser().parse_args(argv)
    folder = args.ledger_dir or (str(pathlib.Path(args.file).parent) if args.file else ".")
    found = problems_in(read_draft(args.file), args.full_slice, folder)
    for line in found:
        sys.stdout.write(line + "\n")
    if found:
        return 1
    sys.stdout.write("draft passed every rule\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
