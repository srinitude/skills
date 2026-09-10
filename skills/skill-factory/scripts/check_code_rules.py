#!/usr/bin/env python3
"""Size and nesting limits for code files.

Rules for owned Python, shell, JavaScript and TypeScript source files:
  max 200 lines of code per file (blank and comment lines excluded)
  max 30 lines of code per function or class, own lines only
  max block nesting depth of 3 inside any function
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
               "ClassDef"]
BLOCKS = tuple(getattr(ast, n) for n in BLOCK_NAMES if hasattr(ast, n))
DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
FUNCS = (ast.FunctionDef, ast.AsyncFunctionDef)


def loc(lines):
    stripped = (line.strip() for line in lines)
    return sum(1 for line in stripped if line and not line.startswith("#"))


def segment_loc(node, lines):
    return loc(lines[node.lineno - 1:node.end_lineno])


def own_loc(node, lines):
    total = segment_loc(node, lines)
    for child in node.body:
        if isinstance(child, DEFS):
            total -= segment_loc(child, lines)
    return total


def block_depth(node):
    deepest, pending = 0, [(node, 0)]
    while pending:
        parent, depth = pending.pop()
        for child in ast.iter_child_nodes(parent):
            level = depth + int(isinstance(child, BLOCKS))
            deepest = max(deepest, level)
            pending.append((child, level))
    return deepest


def check_construct(node, lines, path, problems):
    size = own_loc(node, lines)
    if size > MAX_CONSTRUCT:
        problems.append(f"{path}:{node.lineno}: {node.name} has {size} "
                        f"lines of code; cap is {MAX_CONSTRUCT}")
    if isinstance(node, FUNCS) and (depth := block_depth(node)) > MAX_DEPTH:
        problems.append(f"{path}:{node.lineno}: {node.name} nesting is "
                        f"{depth}; cap is {MAX_DEPTH}")


def check_markers(path, text, problems):
    for number, line in enumerate(text.splitlines(), start=1):
        for marker in MARKERS:
            if marker in line:
                problems.append(f"{path}:{number}: work marker {marker}")


def check_python(path, text, problems):
    lines = text.splitlines()
    if loc(lines) > MAX_FILE:
        problems.append(f"{path}: {loc(lines)} lines of code; cap is 200")
    try:
        tree = ast.parse(text)
    except (SyntaxError, RecursionError) as error:
        problems.append(f"{path}: does not parse: {error}")
        return
    for node in ast.walk(tree):
        if isinstance(node, DEFS):
            check_construct(node, lines, path, problems)


def check_shell(path, text, problems):
    lines = text.splitlines()
    if loc(lines) > MAX_FILE:
        problems.append(f"{path}: {loc(lines)} lines of code; cap is 200")


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
