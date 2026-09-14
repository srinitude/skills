#!/usr/bin/env python3
"""Size and nesting limits for code files.

Rules for owned Python, shell, JavaScript and TypeScript source files:
  max 200 physical lines per file, including blanks and comments
  max 30 physical lines per whole function or class, including decorators
  max file-wide block nesting depth of 3
  no leftover work markers in any code file

Exit codes:
  0  every file passed
  1  at least one rule broken
  2  usage or input error

Example:
  python3 scripts/check_code_rules.py .
"""
import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

from skill_package import owned_paths

JAVASCRIPT = {".js", ".mjs", ".cjs", ".jsx", ".ts", ".mts", ".cts", ".tsx"}
SUPPORTED = JAVASCRIPT | {".py", ".sh"}

MAX_FILE = 200
MAX_CONSTRUCT = 30
MAX_DEPTH = 3
MARKERS = ("TO" + "DO", "FIX" + "ME", "XX" + "X")
BLOCK_NAMES = ["If", "For", "While", "With", "Try", "TryStar", "Match",
               "AsyncFor", "AsyncWith", "FunctionDef", "AsyncFunctionDef",
               "ClassDef", "Lambda"]
BLOCKS = tuple(getattr(ast, n) for n in BLOCK_NAMES if hasattr(ast, n))
DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)


def loc(lines):
    return len(lines)


def segment_loc(node, lines):
    first = min([node.lineno, *[item.lineno for item in getattr(node, "decorator_list", [])]])
    return len(lines[first - 1:node.end_lineno])



def block_depth(node):
    deepest, pending = 0, [(node, 0)]
    while pending:
        parent, depth = pending.pop()
        for child in ast.iter_child_nodes(parent):
            peer = isinstance(child, ast.If) and isinstance(parent, ast.If) and child.col_offset == parent.col_offset
            level = depth + int(isinstance(child, BLOCKS) and not peer)
            deepest = max(deepest, level)
            pending.append((child, level))
    return deepest


def check_construct(node, lines, path, problems):
    size = segment_loc(node, lines)
    if size > MAX_CONSTRUCT:
        problems.append(f"{path}:{node.lineno}: {getattr(node, 'name', type(node).__name__)} has {size} "
                        f"physical lines; cap is {MAX_CONSTRUCT}")


def check_markers(path, text, problems):
    for number, line in enumerate(text.splitlines(), start=1):
        found = (marker for marker in MARKERS if marker in line)
        problems.extend(f"{path}:{number}: work marker {marker}" for marker in found)


def check_python(path, text, problems):
    lines = text.splitlines()
    if loc(lines) > MAX_FILE:
        problems.append(f"{path}: {loc(lines)} physical lines; cap is 200")
    try:
        tree = ast.parse(text)
    except (SyntaxError, RecursionError) as error:
        problems.append(f"{path}: does not parse: {error}")
        return
    if (depth := block_depth(tree)) > MAX_DEPTH:
        problems.append(f"{path}: file nesting is {depth}; cap is {MAX_DEPTH}")
    for node in ast.walk(tree):
        if isinstance(node, DEFS):
            check_construct(node, lines, path, problems)


def check_shell(path, text, problems):
    lines = text.splitlines()
    if loc(lines) > MAX_FILE:
        problems.append(f"{path}: {loc(lines)} physical lines; cap is 200")


def check_file(path, problems):
    text = path.read_text(encoding="utf-8")
    check_markers(path, text, problems)
    if path.suffix == ".py":
        check_python(path, text, problems)
    elif path.suffix == ".sh":
        check_shell(path, text, problems)


def collect(target):
    path = Path(target)
    if path.is_symlink():
        raise ValueError("symlink code targets are unsupported")
    if not path.exists():
        raise FileNotFoundError(target)
    if not path.is_dir():
        if path.is_file() and path.suffix in SUPPORTED:
            return [path]
        raise ValueError("unsupported code extension: " + path.suffix)
    return [path for path in sorted(owned_paths(path)) if path.suffix in SUPPORTED]


def check_javascript(files, problems):
    selected = [str(path.resolve()) for path in files if path.suffix in JAVASCRIPT]
    if not selected:
        return
    request = {"files": selected, "file": MAX_FILE,
               "construct": MAX_CONSTRUCT, "depth": MAX_DEPTH}
    script = Path(__file__).with_name("check_javascript.ts")
    result = subprocess.run(["node", str(script)], input=json.dumps(request),
                            text=True, capture_output=True, check=False)
    if result.returncode not in (0, 1):
        raise ValueError("JavaScript/TypeScript checker failed: " + result.stderr.strip())
    try:
        entries = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise ValueError("invalid JavaScript/TypeScript checker output: "
                         + result.stderr.strip()) from error
    if not isinstance(entries, list) or not all(isinstance(p, str) for p in entries):
        raise ValueError("invalid JavaScript/TypeScript checker result")
    if bool(entries) != bool(result.returncode):
        raise ValueError("JavaScript/TypeScript checker status mismatch")
    problems.extend(entries)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("target", help="code file or directory to scan")
    args = parser.parse_args(argv)
    try:
        files = collect(args.target)
    except (FileNotFoundError, ValueError) as missing:
        print(f"error: {missing}",
              file=sys.stderr)
        return 2
    problems = []
    for path in files:
        check_file(path, problems)
    try:
        check_javascript(files, problems)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    for problem in problems:
        print(problem)
    print(f"checked {len(files)} files, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
