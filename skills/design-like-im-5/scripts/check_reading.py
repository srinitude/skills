#!/usr/bin/env python3
"""Check plain words and short prose.

The score uses Flesch-Kincaid Grade Level. Exact code is left out.
One approved contract copy is the sole full-file exception.

Exit codes:
  0  the text passed
  1  the text failed
  2  the input could not be read
"""
import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "assets" / "reading-contract.json"
EXCEPTIONS = ROOT / "assets" / "reading-exceptions.json"
TEXT_TYPES = {".md", ".json", ".py", ".toml", ".yml", ".yaml", ".txt"}
SENTENCE = re.compile(r"(?<=[.!?])\s+")
WORD = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
EXACT = re.compile(r"`[^`]+`|https?://\S+|\b[a-f0-9]{32,}\b|(?:\.?\.?/)?[\w.-]+/[\w./-]+")


def syllables(word):
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    count = len(re.findall(r"[aeiouy]+", word))
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def strings_from_json(text):
    data = json.loads(text)
    found = []
    todo = [data]
    while todo:
        value = todo.pop()
        if isinstance(value, str):
            found.append(value)
            continue
        if isinstance(value, list):
            todo.extend(value)
            continue
        if isinstance(value, dict):
            todo.extend(value.values())
    return found


def strings_from_python(text):
    tree = ast.parse(text)
    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            value = ast.get_docstring(node, clean=True)
            if value:
                found.append(value)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if " " in node.value.strip():
                found.append(node.value)
        if isinstance(node, ast.JoinedStr):
            value = "".join(part.value for part in node.values
                            if isinstance(part, ast.Constant)
                            and isinstance(part.value, str))
            if " " in value.strip():
                found.append(value)
    found.extend(line.lstrip()[1:].strip() for line in text.splitlines()
                 if line.lstrip().startswith("#")
                 and not line.lstrip().startswith("#!"))
    return found


def strings_from_markdown(text):
    found, fence = [], False
    for line in text.splitlines():
        if line.strip().startswith(("```", "~~~")):
            fence = not fence
            continue
        if fence or not line.strip() or line.strip() == "---":
            continue
        if re.match(r"^\s*[-*]\s+`", line):
            continue
        found.append(re.sub(r"^\s*(?:#+|[-*+] |\d+[.)] )", "", line))
    return found


def prose(path, text):
    if path.suffix == ".json":
        return strings_from_json(text)
    if path.suffix == ".py":
        return strings_from_python(text)
    if path.suffix in {".md", ".txt"}:
        return strings_from_markdown(text)
    found = []
    for line in text.splitlines():
        match = re.search(r"#\s*(.+)", line)
        if match:
            found.append(match.group(1))
        found.extend(re.findall(r'"([^"\n]+)"', line))
    return found


def is_machine_text(text):
    value = text.strip()
    if not value:
        return True
    if value.startswith(("python3 ", "mise ", "set -", "npm ", "uvx ")):
        return True
    if re.fullmatch(r"[A-Z0-9_.:/-]+", value):
        return True
    if re.fullmatch(r"[a-z0-9_.:/-]+", value):
        return True
    return False


def clean_chunks(items):
    out = []
    seen = set()
    for item in items:
        if is_machine_text(item):
            continue
        clean = re.sub(r"\s+", " ", EXACT.sub(" ", item)).strip()
        if WORD.search(clean) and clean not in seen:
            out.append(clean)
            seen.add(clean)
    return out


def split_sentences(chunks):
    out = []
    for chunk in chunks:
        out.extend(item.strip() for item in SENTENCE.split(chunk)
                   if WORD.search(item))
    return out


def grade(words, sentence_count):
    value = sum(syllables(word) for word in words)
    return 0.39 * (len(words) / sentence_count) + 11.8 * (value / len(words)) - 15.59


def evaluate(chunks, rules):
    sentences = split_sentences(chunks)
    words = [word for sentence in sentences for word in WORD.findall(sentence)]
    issues = []
    lengths = [len(WORD.findall(item)) for item in sentences]
    for sentence, length in zip(sentences, lengths):
        if length > rules["max_sentence_words"]:
            note = " ".join(sentence.split()[:12])
            issues.append(f"long sentence: {length} words: {note}")
    if lengths and sum(lengths) / len(lengths) > rules["max_mean_sentence_words"]:
        issues.append(f"mean sentence: {sum(lengths) / len(lengths):.2f} words")
    if words and sentences:
        value = grade(words, len(sentences))
        if value > rules["max_grade"]:
            issues.append(f"grade score: {value:.2f}")
    return issues


def settings():
    rules = json.loads(CONTRACT.read_text(encoding="utf-8"))
    exceptions = json.loads(EXCEPTIONS.read_text(encoding="utf-8"))
    return rules, exceptions


def check_file(path, rules, exceptions):
    raw = path.read_bytes()
    full = exceptions["full_file"][0]
    if path.name == full["name"]:
        digest = hashlib.sha256(raw).hexdigest()
        if digest == full["sha256"]:
            return [], "approved exact copy", []
        return ["contract copy changed"], "failed", []
    try:
        chunks = clean_chunks(prose(path, raw.decode("utf-8")))
    except (UnicodeDecodeError, json.JSONDecodeError, SyntaxError) as error:
        return [f"could not parse prose: {error}"], "failed", []
    issues = evaluate(chunks, rules)
    return issues, "passed" if not issues else "failed", chunks


def collect(target):
    path = Path(target)
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(item for item in path.rglob("*")
                      if item.is_file() and item.suffix in TEXT_TYPES
                      and "__pycache__" not in item.parts)
    raise FileNotFoundError(target)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="public file or skill folder")
    args = parser.parse_args(argv)
    rules, exceptions = settings()
    try:
        files = collect(args.target)
    except FileNotFoundError as error:
        print(f"error: no such path: {error}", file=sys.stderr)
        return 2
    total = 0
    corpus = []
    for path in files:
        issues, state, chunks = check_file(path, rules, exceptions)
        corpus.extend(chunks)
        if state == "approved exact copy":
            print(f"PASS approved exact copy: {path}")
        for issue in issues:
            print(f"{path}: {issue}")
        total += len(issues)
    corpus_issues = evaluate(corpus, rules)
    for issue in corpus_issues:
        print(f"full public corpus: {issue}")
    total += len(corpus_issues)
    print(f"reading check: {len(files)} files, {total} problems")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
