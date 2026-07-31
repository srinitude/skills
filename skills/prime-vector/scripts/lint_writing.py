#!/usr/bin/env python3
"""Mechanical writing checks for markdown files."""
import argparse
import re
import sys
from pathlib import Path

WORDS = [
    "delve", "delves", "delving", "delved", "tapestry", "camaraderie",
    "kaleidoscope", "cacophony", "palpable", "solace", "fleeting",
    "unravel", "grapple", "vibrant", "intricate", "meticulous",
    "meticulously", "unspoken", "amidst", "underscore", "underscores",
    "showcase", "showcasing", "realm", "embark", "pivotal", "seamless",
    "seamlessly", "holistic", "foster", "elevate", "leverage",
    "leveraging", "robust",
]
PHRASES = [
    "in today's", "important to note", "crucial to note",
    "a testament to", "blur the line between", "ever-evolving",
    "fast-paced", "cutting-edge", "not just", "not only",
    "plays a vital role", "plays a crucial role", "in conclusion",
    "certainly!", "i'd be happy to", "great question",
    "let me know if", "i hope this helps", "a sense of", "a mix of",
    "click here", "navigate the",
]
DASHES = {"\u2014": "em dash", "\u2013": "en dash"}
LATIN = [
    (re.compile(r"\be\.g\."), 'Latin shorthand "e.g."; write "for example"'),
    (re.compile(r"\bi\.e\."), 'Latin shorthand "i.e."; write "that is"'),
]
WORD_RES = [(word, re.compile(r"\b%s\b" % re.escape(word), re.I)) for word in WORDS]
LIST_RE = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def check_words(line):
    return [f'banned word "{word}"' for word, pattern in WORD_RES if pattern.search(line)]


def check_phrases(line):
    lowered = line.lower()
    return [f'banned frame "{phrase}"' for phrase in PHRASES if phrase in lowered]


def check_symbols(line):
    found = [name for char, name in DASHES.items() if char in line]
    found.extend(message for pattern, message in LATIN if pattern.search(line))
    if line.startswith("####"):
        found.append("heading nested past three levels")
    return found


def skip_frontmatter(lines):
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                return index + 1
    return 0


def breaks_block(line, fence):
    if FENCE_RE.match(line):
        return True, not fence
    stripped = line.strip()
    if fence or not stripped or stripped.startswith(("#", "|", ">")):
        return True, fence
    return False, fence


def collect_blocks(lines):
    blocks, current, fence = [], [], False
    for number in range(skip_frontmatter(lines), len(lines)):
        line = lines[number]
        broke, fence = breaks_block(line, fence)
        code = not current and (line[:4] == "    " or line[:1] == "\t")
        if broke or code:
            if current:
                blocks.append(current)
            current = []
            continue
        if LIST_RE.match(line) and current:
            blocks.append(current)
            current = []
        current.append((number + 1, line))
    if current:
        blocks.append(current)
    return blocks


def check_file(path):
    problems = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, start=1):
        messages = check_words(line) + check_phrases(line) + check_symbols(line)
        problems.extend(f"{path}:{number}: {message}" for message in messages)
    for block in collect_blocks(lines):
        for number, _ in block[1:]:
            problems.append(f"{path}:{number}: hard line break inside a wrappable block; join the block into one line")
    return problems


def collect(targets):
    files = []
    for target in targets:
        path = Path(target)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError(target)
    return files


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("targets", nargs="+", help="markdown files or directories to scan")
    args = parser.parse_args(argv)
    try:
        files = collect(args.targets)
    except FileNotFoundError as missing:
        print(f"error: no such file or directory: {missing}", file=sys.stderr)
        return 2
    problems = []
    for path in files:
        problems.extend(check_file(path))
    for problem in problems:
        print(problem)
    print(f"checked {len(files)} files, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
