#!/usr/bin/env python3
"""Flag secret-shaped strings in text.

Reads text from a file argument or stdin. Prints one line per finding with
the line number, the kind of secret, and a masked preview. Never prints a
full value. Exit 0 when clean, 2 when findings exist, 1 on usage errors.

Usage:
    python3 scan_secrets.py [file]
    cat prompt.txt | python3 scan_secrets.py
"""
import math
import re
import sys

MAX_BYTES = 5_000_000

PATTERNS = [
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{4,}\b")),
    ("URL with password", re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^@\s]+@")),
    ("bearer token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._-]{16,}\b")),
    ("credential assignment",
     re.compile(r"(?i)\b(api[_-]?key|secret|token|password|passwd)\b\s*[:=]\s*['\"]?[^\s'\"]{8,}")),
]

ENTROPY_TOKEN = re.compile(r"\b[A-Za-z0-9+/=_-]{24,}\b")


def entropy(value: str) -> float:
    counts = {c: value.count(c) for c in set(value)}
    total = len(value)
    return -sum(n / total * math.log2(n / total) for n in counts.values())


def looks_random(token: str) -> bool:
    if token.startswith(("http", "www.")) or "/" in token:
        return False
    has_upper = any(c.isupper() for c in token)
    has_lower = any(c.islower() for c in token)
    has_digit = any(c.isdigit() for c in token)
    return has_digit and has_upper and has_lower and entropy(token) > 4.2


def mask(value: str) -> str:
    return value[:4] + "…" if len(value) > 4 else "…"


def scan(text: str):
    findings = []
    for number, line in enumerate(text.splitlines(), start=1):
        seen_spans = []
        for kind, pattern in PATTERNS:
            for match in pattern.finditer(line):
                findings.append((number, kind, mask(match.group(0))))
                seen_spans.append(match.span())
        for match in ENTROPY_TOKEN.finditer(line):
            span = match.span()
            covered = any(s <= span[0] and span[1] <= e for s, e in seen_spans)
            if not covered and looks_random(match.group(0)):
                findings.append((number, "high-entropy string", mask(match.group(0))))
    return findings


def main() -> int:
    if len(sys.argv) > 2:
        print("usage: scan_secrets.py [file]  (or pipe text on stdin)", file=sys.stderr)
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
    findings = scan(text)
    if not findings:
        print("clean: no secret-shaped strings found")
        return 0
    for number, kind, preview in findings:
        print(f"line {number}: {kind} ({preview}) — replace with a named placeholder")
    print(f"{len(findings)} finding(s). Replace each with a placeholder like {{{{API_KEY}}}}.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
