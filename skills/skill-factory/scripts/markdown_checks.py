"""Read Markdown and report bounded checks; the model owns meaning and clarity."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import sys
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, epilog="Example: --root /path/to/skill")
    parser.add_argument("--root", action="append", required=True)
    args = parser.parse_args()

from markdown_it import MarkdownIt
from textstat import textstat

VERSIONS = {"textstat": "0.7.8", "markdown-it-py": "4.0.0", "cmudict": "1.1.3",
            "pyphen": "0.18.1", "mdurl": "0.1.2", "importlib_resources": "7.1.0",
            "importlib_metadata": "9.0.1", "zipp": "4.1.0", "setuptools": "84.0.0"}
PARSER = MarkdownIt("commonmark", {"html": True}).enable(["table", "strikethrough"])
IGNORED = {".git", "node_modules", ".venv", "__pycache__"}


def runtime():
    actual = {name: importlib.metadata.version(name) for name in VERSIONS}
    if actual != VERSIONS:
        raise ValueError("Reading-check packages differ from the pinned method")
    textstat.set_lang("en_US")
    return {"packages": actual, "python": sys.version, "policy": "markdown-reading-v2",
            "paragraph_words": {"maximum_exclusive": 150, "method": "textstat.lexicon_count; extracted paragraph prose"},
            "owner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "method": "Flesch-Kincaid; textstat English CMU dictionary with Pyphen fallback",
            "limit": "Estimated reading grade; not proof of meaning or reader performance"}


def score(text):
    words = textstat.lexicon_count(text, removepunct=True)
    return textstat.flesch_kincaid_grade(text) if words >= 10 else None


def inline_text(children):
    parts = []
    for child in children or []:
        if child.type in {"text", "softbreak", "hardbreak"}:
            parts.append(child.content if child.type == "text" else " ")
        elif child.type == "image":
            parts.append(inline_text(child.children))
    return "".join(parts)


def frontmatter(text):
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text, []
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ValueError("Front matter has no closing line")
    kept = "".join("\n" for _ in lines[:end + 1]) + "".join(lines[end + 1:])
    return kept, [{"kind": "frontmatter", "start": 1, "end": end + 1}]


def token_proof(tokens, excluded):
    blocks, failures, heading = [], [], 0
    for index, token in enumerate(tokens):
        line = (token.map or [0])[0] + 1
        if token.type == "heading_open" and int(token.tag[1:]) > heading + 1:
            failures.append({"rule": "heading-order", "line": line})
        if token.type == "heading_open":
            heading = int(token.tag[1:])
        if token.type in {"fence", "code_block", "html_block"}:
            excluded.append({"kind": token.type, "start": line, "end": (token.map or [0, 0])[1]})
        if token.type != "inline":
            continue
        prose = inline_text(token.children)
        words = textstat.lexicon_count(prose, removepunct=True)
        if tokens[index - 1].type == "paragraph_open" and words >= 150:
            failures.append({"rule": "paragraph-words", "line": line,
                             "words": words, "maximum_exclusive": 150})
        blocks.append({"line": line, "text": prose, "grade": score(prose)})
        failures.extend(inline_findings(token.children, line, excluded))
    return blocks, failures


def inline_findings(children, line, excluded):
    failures = []
    for child in children or []:
        if child.type in {"code_inline", "html_inline"}:
            excluded.append({"kind": child.type, "start": line, "text": child.content})
        if child.type == "image" and not inline_text(child.children).strip():
            failures.append({"rule": "image-alt", "line": line})
    return failures


def check_text(text):
    parsed, excluded = frontmatter(text)
    environment = {}
    tokens = PARSER.parse(parsed, environment)
    blocks, failures = token_proof(tokens, excluded)
    prose = "\n".join(x["text"] for x in blocks if x["text"].strip())
    grade = score(prose)
    if grade is not None and grade > 6:
        failures.append({"rule": "grade", "line": 1, "grade": grade})
    failures.extend({"rule": "block-grade", "line": x["line"], "grade": x["grade"]}
                    for x in blocks if x["grade"] is not None and x["grade"] > 6)
    if len(text.splitlines()) > 200:
        failures.append({"rule": "lines", "line": 201})
    return {"text": text, "prose": prose, "grade": grade, "blocks": blocks,
            "score_state": "scored" if grade is not None else "short-text-review",
            "excluded": excluded, "failures": failures, "html": PARSER.renderer.render(tokens, PARSER.options, environment),
            "syntax": {"tokens": [token.as_dict() for token in tokens],
                       "references": environment.get("references", {}), "rules": PARSER.get_active_rules(),
                       "line_maps": "zero-based start inclusive, end exclusive; inline children inherit block location",
                       "limit": "Parsed structure only; not full target conformance or proof of sound form choices."},
            "pending": ["meaning", "rendered clarity", "links and anchors",
                        "first-load rules", "protected spans and exclusions", "graph and body fit"]}


def capture(path):
    path = Path(path)
    if not path.is_absolute() or path.is_symlink() or path.resolve() != path:
        raise ValueError("Use a real absolute file path")
    if not path.is_file() or path.stat().st_nlink != 1:
        raise ValueError("Use one regular input file")
    raw = path.read_bytes()
    return {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
            "text": raw.decode("utf-8")}


def files(roots):
    found = set()
    for name in roots:
        root = Path(name)
        if not root.is_absolute() or root.resolve() != root or not root.is_dir():
            raise ValueError("Use real absolute Markdown roots")
        found.update(walk_markdown(root))
    if not found:
        raise ValueError("The Markdown inventory is empty")
    return [capture(path) for path in sorted(found)]


def walk_markdown(root):
    found = []
    for base, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(x for x in dirs if x not in IGNORED)
        if any((Path(base) / x).is_symlink() for x in dirs):
            raise ValueError("A Markdown root contains a linked directory")
        found.extend(str(Path(base) / x) for x in names if x.lower().endswith(".md"))
    return found


def main(roots):
    try:
        report = {"runtime": runtime(), "files": [{**item, **check_text(item["text"])} for item in files(roots)],
                  "execution_acceptance": "pending"}
        print(json.dumps(report, ensure_ascii=False))
        return 1 if any(item["failures"] for item in report["files"]) else 0
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(args.root))
