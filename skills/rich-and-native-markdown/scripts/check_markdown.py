#!/usr/bin/env python3
"""Check Markdown files, local links, and a declared reading graph.

Requires markdown-it-py. See references/checks.md for scope and manual checks.
"""

import argparse
from functools import partial
import json
from pathlib import Path
import sys

from markdown_graph import check_reachability, required_cycles
from markdown_links import check_link, read_parts
from markdown_manifest import declared_routes, manifest_options
from markdown_parse import physical_lines
from markdown_structure import check_structures


def check_file(path, read, reasons, result, routes):
    parts = read(path)
    if parts is None:
        return
    text, (links, anchors, warnings), digest = parts
    count = physical_lines(text)
    result["files"].append({"path": str(path), "lines": count, "sha256": digest})
    if count >= 200:
        result["errors"].append(f"{path}: {count} physical lines; maximum is 199")
    if count >= 150 and path not in reasons:
        result["errors"].append(f"{path}: {count} lines need a reviewed core_reasons entry")
    result["needs_review"].extend(f"{path}: {w}" for w in warnings)
    for destination in links:
        check_link(path, destination, read, result, routes)


def finish_review(result):
    result["needs_review"].append(
        "Read all prose dependencies and external dependencies through their full closure; "
        "confirm the manifest has every required edge and that navigation labels are true")
    if any(item["lines"] >= 150 for item in result["files"]):
        result["needs_review"].append("Check that each core reason is true and no clear split was missed")
    result["needs_review"].append(
        "Verify syntax, anchors, readability, and preserved meaning in the actual target renderer")


def check_tree(root, data, supplied, parser, result):
    files = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() == ".md")
    actual = {p.resolve() for p in files}
    try:
        reasons, heading_ids, anchors, starts = manifest_options(
            root, data, actual, result["errors"], supplied)
    except (ValueError, OSError) as exc:
        result["errors"].append(f"Invalid manifest: {exc}")
        return result
    read = partial(read_parts, cache={}, parser=parser, heading_ids=heading_ids,
                   extra_anchors=anchors, errors=result["errors"])
    routes = []
    for path in files:
        check_file(path.resolve(), read, reasons, result, routes)
    check_structures(root, data, files, read, result)
    required = declared_routes(root, data, result["errors"], routes)
    result["cycles"] = required_cycles(required)
    result["errors"].extend("Required-read cycle: " + " -> ".join(c) for c in result["cycles"])
    check_reachability(starts, actual, routes, result)
    finish_review(result)
    return result


def check(root, manifest=None):
    result = {"scope": "mechanical checks only", "errors": [], "needs_review": [],
              "files": [], "cycles": []}
    try:
        from markdown_it import MarkdownIt
    except ImportError:
        result["errors"].append("markdown-it-py is missing; use an environment where it is installed")
        return result
    root = Path(root).resolve()
    if not root.is_dir():
        result["errors"].append(f"Root is not a directory: {root}")
        return result
    data = manifest if manifest is not None else {}
    if not isinstance(data, dict):
        result["errors"].append("Manifest must be a JSON object")
        return result
    return check_tree(root, data, manifest is not None, MarkdownIt("commonmark"), result)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("root")
    cli.add_argument("--manifest", type=Path)
    args = cli.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text()) if args.manifest else None
        result = check(args.root, manifest)
    except (OSError, UnicodeError, ValueError) as exc:
        result = {"scope": "mechanical checks only", "errors": [str(exc)], "needs_review": []}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return int(bool(result["errors"]))


if __name__ == "__main__":
    sys.exit(main())
