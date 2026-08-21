#!/usr/bin/env python3
"""Check a finished delivery against the shape rules in SKILL.md step 5.

Reads the delivery text from a file argument or stdin. Prints one line per
check. Exit 0 when every check passes, 2 when any fails, 1 on usage errors.

Checks: the lead-in line, one non-empty fence, a "What changed" section with
2 to 6 bullets, "Open questions" non-empty when present, and no obvious
secret-shaped strings anywhere in the reply. The written rules in SKILL.md
decide; this script is an aid.

Usage:
    python3 check_delivery.py [file]
    cat delivery.txt | python3 check_delivery.py
"""
import re
import sys

LEAD_IN = "Here is the enhanced prompt:"

SECRETS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{4,}\b"),
    re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@]+:[^@\s]+@"),
]


def bullets_under(text: str, heading: str):
    match = re.search(re.escape(heading) + r"\s*\n(.*?)(?=\n\s*\n\S|\n\*\*|\Z)", text, re.S)
    if match is None:
        return None
    lines = [line for line in match.group(1).splitlines() if line.strip().startswith("-")]
    return lines or None


def run_checks(text: str):
    results = []

    results.append((LEAD_IN in text, f'lead-in line "{LEAD_IN}" present'))

    after = text.split(LEAD_IN, 1)[1] if LEAD_IN in text else text
    fences = re.findall(r"```[^\n]*\n(.*?)```", after, re.S)
    results.append((len(fences) >= 1, "a fenced block follows the lead-in"))
    if fences:
        results.append((bool(fences[0].strip()), "the fence is not empty"))

    changed = bullets_under(text, "**What changed**")
    if changed is None:
        results.append((False, '"**What changed**" section with bullets present'))
    else:
        count = len(changed)
        results.append((2 <= count <= 6, f'"What changed" has 2 to 6 bullets (found {count})'))

    if "**Open questions**" in text:
        questions = bullets_under(text, "**Open questions**")
        results.append((bool(questions), '"Open questions" has at least one bullet'))

    leaks = [p.pattern for p in SECRETS if p.search(text)]
    results.append((not leaks, "no secret-shaped strings in the reply"))

    return results


def main() -> int:
    if len(sys.argv) > 2:
        print("usage: check_delivery.py [file]  (or pipe text on stdin)", file=sys.stderr)
        return 1
    if len(sys.argv) == 2:
        try:
            with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError as error:
            print(f"cannot read {sys.argv[1]}: {error}", file=sys.stderr)
            return 1
    else:
        text = sys.stdin.read()
    if not text.strip():
        print("no input text; pass a file or pipe text on stdin", file=sys.stderr)
        return 1

    failed = 0
    for passed, label in run_checks(text):
        print(("pass  " if passed else "FAIL  ") + label)
        failed += 0 if passed else 1
    if failed:
        print(f"{failed} check(s) failed. Fix the draft and run the checks again.")
        return 2
    print("all shape checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
