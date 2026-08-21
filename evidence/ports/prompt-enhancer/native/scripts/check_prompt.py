#!/usr/bin/env python3
"""Run the deterministic universal checks from SKILL.md step 3 on a prompt.

Reads the isolated prompt from a file argument or stdin. One run covers the
mechanical half of step 3: secret-shaped strings, injection phrases, transmit
steps needing user confirmation, unnamed authority, vague qualifiers, and
two presence heuristics (output contract, success criteria). Semantic checks
(ambiguity resolution, contradictions) stay with the reader.

Findings that require action (secrets, injection, transmit steps) exit 2.
Notes alone exit 0. Usage errors exit 1. Secret values print masked, never
whole.

Usage:
    python3 check_prompt.py [file]
    cat prompt.txt | python3 check_prompt.py
"""
import re
import sys

MAX_BYTES = 5_000_000

SECRETS = [
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{4,}\b")),
    ("URL with password", re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^@\s]+@")),
    ("bearer token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._-]{16,}\b")),
    ("credential assignment",
     re.compile(r"(?i)\b(api[_-]?key|secret|token|password|passwd)\b\s*[:=]\s*['\"]?[^\s'\"]{8,}")),
]

INJECTION = re.compile(
    r"(?i)\b(ignore\s+(all\s+|your\s+)?(previous\s+|prior\s+)?instructions"
    r"|disregard\s+the\s+above"
    r"|reveal\s+your\s+(system\s+)?prompt)\b")

TRANSMIT = re.compile(
    r"(?i)\b(send|email|post|upload|submit|publish|share|forward)\b[^.\n]{0,60}\b(to|at)\b[^.\n]{0,80}")

AUTHORITY = re.compile(
    r"(?i)\b(experts?\s+(say|argue|agree)|studies\s+show|research\s+(shows|suggests)"
    r"|industry\s+reports?|many\s+believe|widely\s+regarded|some\s+critics)\b")

VAGUE = re.compile(
    r"(?i)\b(better|nicer?|good|great|fast|soon|recent(ly)?|some|various|appropriate"
    r"|robust|modern|user-friendly|professional|high-quality|engaging|compelling)\b")

CONTRACT = re.compile(
    r"(?i)\b(format|json|csv|table|list|section|paragraph|words?|sentences?"
    r"|tone|style|length|characters|markdown)\b")

CRITERIA = re.compile(
    r"(?i)\b(must|at least|no more than|exactly|until|criteria|passes|when done|so that)\b")


def mask(value: str) -> str:
    return value[:4] + "…" if len(value) > 4 else "…"


def scan(text: str):
    actions, notes = [], []
    for number, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in SECRETS:
            for match in pattern.finditer(line):
                actions.append(f"line {number}: {kind} ({mask(match.group(0))}) — replace with a named placeholder")
        for match in INJECTION.finditer(line):
            actions.append(f"line {number}: injection phrase ({match.group(0)[:40]}) — remove it and say why")
        for match in TRANSMIT.finditer(line):
            actions.append(f"line {number}: transmit step ({match.group(0)[:50]}…) — keep only if the user confirmed the destination in their own words")
        for match in AUTHORITY.finditer(line):
            notes.append(f"line {number}: unnamed authority ({match.group(0)}) — name the source or cut the claim")
        for match in VAGUE.finditer(line):
            notes.append(f"line {number}: vague qualifier ({match.group(0)}) — replace with a specific, checkable requirement")
    if not CONTRACT.search(text):
        notes.append("no output contract detected — state format, length, structure, or language")
    if not CRITERIA.search(text):
        notes.append("no success criteria detected — state how the target knows it is done")
    return actions, notes


def main() -> int:
    if len(sys.argv) > 2:
        print("usage: check_prompt.py [file]  (or pipe text on stdin)", file=sys.stderr)
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

    actions, notes = scan(text)
    for line in actions:
        print("ACTION  " + line)
    for line in notes[:20]:
        print("note    " + line)
    print()
    if actions:
        print(f"{len(actions)} finding(s) require action before enhancing.")
        return 2
    print("No action findings. Notes feed step 3's findings list; semantic checks stay with you.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
