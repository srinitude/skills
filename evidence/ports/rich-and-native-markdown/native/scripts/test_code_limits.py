#!/usr/bin/env python3
"""Use Python's parser to check this folder's code size and nesting limits."""

import ast
import json
from pathlib import Path


BLOCKS = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith,
          ast.Try, ast.TryStar, ast.Match)
CONSTRUCTS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def block_depth(node, depth=0):
    """Count nested control blocks; each function or class starts a new scope."""
    if isinstance(node, CONSTRUCTS):
        depth = 0
    current = depth + int(isinstance(node, BLOCKS))
    return max([current] + [block_depth(child, current) for child in ast.iter_child_nodes(node)])


def inspect_file(path):
    text = path.read_text()
    tree = ast.parse(text, filename=str(path))
    constructs = [(n.name, n.end_lineno - n.lineno + 1)
                  for n in ast.walk(tree) if isinstance(n, CONSTRUCTS)]
    return {"path": str(path), "lines": len(text.splitlines()),
            "max_construct_lines": max((n for _, n in constructs), default=0),
            "max_nesting": block_depth(tree), "constructs": dict(constructs)}


def main():
    rows = [inspect_file(path) for path in sorted(Path(__file__).parent.glob("*.py"))]
    failures = [row for row in rows if row["lines"] > 200 or
                row["max_construct_lines"] > 30 or row["max_nesting"] > 3]
    print(json.dumps({"status": "failed" if failures else "passed", "files": rows}, indent=2))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
