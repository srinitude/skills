#!/usr/bin/env python3
"""Verify and retrieve the uncompressed YAML image prompt corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MANIFEST = ASSETS / "prompt-manifest.json"
FIELD_ORDER = ("id", "path", "domain", "lane", "perspective", "sha256", "bytes", "prompt")


def digest(data: bytes) -> str:
    """Return a SHA-256 hex digest."""
    return hashlib.sha256(data).hexdigest()


def load_manifest() -> dict:
    """Load the YAML corpus manifest."""
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def scalar(text: str) -> object:
    """Parse one scalar from the package's deterministic YAML subset."""
    value = text.strip()
    if value.startswith('"'):
        return json.loads(value)
    if value.isdigit():
        return int(value)
    return value


def parse_record(lines: list[str], start: int) -> tuple[dict, int]:
    """Parse one fixed-order prompt record."""
    row: dict = {}
    for offset, field in enumerate(FIELD_ORDER):
        line = lines[start + offset]
        prefix = "- " if offset == 0 else "  "
        expected = f"{prefix}{field}: "
        if not line.startswith(expected):
            raise ValueError(f"schema:{start + offset + 1}")
        row[field] = scalar(line[len(expected):])
    return row, start + len(FIELD_ORDER)


def parse_shard(raw: bytes) -> tuple[dict, list[dict]]:
    """Parse one deterministic YAML shard without an external dependency."""
    lines = raw.decode("utf-8").splitlines()
    if len(lines) < 8 or lines[0] != "schema: image-prompt-yaml-shard/v1":
        raise ValueError("schema")
    header = {
        "source_commit": scalar(lines[1].split(": ", 1)[1]),
        "first": scalar(lines[3].split(": ", 1)[1]),
        "last": scalar(lines[4].split(": ", 1)[1]),
        "count": scalar(lines[5].split(": ", 1)[1]),
    }
    if lines[2] != "range:" or lines[6] != "prompts:":
        raise ValueError("schema")
    rows: list[dict] = []
    index = 7
    while index < len(lines):
        row, index = parse_record(lines, index)
        rows.append(row)
    return header, rows


def load_rows() -> tuple[list[dict], list[str]]:
    """Load all declared YAML shards and return prompt rows and errors."""
    rows: list[dict] = []
    errors: list[str] = []
    for shard in load_manifest()["shards"]:
        path = ASSETS.parent / shard["path"]
        raw = path.read_bytes()
        if len(raw) != shard["bytes"] or digest(raw) != shard["sha256"]:
            errors.append(f"shard:{shard['path']}")
            continue
        try:
            header, entries = parse_shard(raw)
        except (ValueError, IndexError, UnicodeDecodeError, json.JSONDecodeError):
            errors.append(f"schema:{shard['path']}")
            continue
        if len(entries) != shard["count"] or header["count"] != shard["count"]:
            errors.append(f"count:{shard['path']}")
        if entries and (header["first"] != entries[0]["path"] or header["last"] != entries[-1]["path"]):
            errors.append(f"range:{shard['path']}")
        rows.extend(entries)
    return rows, errors


def load_index() -> dict:
    """Return prompt metadata and exact text."""
    rows, errors = load_rows()
    if errors:
        raise ValueError("BLOCKED_PROMPT_HASH")
    return {"prompts": rows}


def verify() -> dict:
    """Validate every YAML shard and exact prompt string."""
    manifest = load_manifest()
    rows, errors = load_rows()
    paths: set[str] = set()
    prior: bytes | None = None
    for row in rows:
        data = row.get("prompt", "").encode("utf-8")
        path_key = row.get("path", "").encode("utf-8")
        if len(data) != row.get("bytes") or digest(data) != row.get("sha256"):
            errors.append(f"prompt:{row.get('path', '')}")
        if row.get("path") in paths or (prior is not None and path_key <= prior):
            errors.append(f"order:{row.get('path', '')}")
        paths.add(row.get("path"))
        prior = path_key
    if len(rows) != manifest["count"] or len(paths) != manifest["count"]:
        errors.append("count")
    ordered = sorted(set(errors))
    return {"status": "PASS" if not ordered else "BLOCKED_PROMPT_HASH", "count": len(rows), "shards": len(manifest["shards"]), "errors": ordered}


def select(domain: str, lane: str, perspective: str) -> dict:
    """Select one exact prompt record."""
    rows = [row for row in load_index()["prompts"] if row["domain"] == domain and row["lane"] == lane and row["perspective"] == perspective]
    if len(rows) != 1:
        raise KeyError("NO_MATCH")
    return {key: value for key, value in rows[0].items() if key != "prompt"}


def get(member_path: str) -> bytes:
    """Return exact prompt bytes for a canonical path."""
    rows = [row for row in load_index()["prompts"] if row["path"] == member_path]
    if len(rows) != 1:
        raise KeyError("NO_MATCH")
    return rows[0]["prompt"].encode("utf-8")


def main() -> int:
    """Run the corpus CLI."""
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify")
    pick = commands.add_parser("select")
    pick.add_argument("domain")
    pick.add_argument("lane")
    pick.add_argument("perspective")
    fetch = commands.add_parser("get")
    fetch.add_argument("member_path")
    args = parser.parse_args()
    if args.command == "verify":
        result = verify()
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0 if result["status"] == "PASS" else 1
    if args.command == "select":
        print(json.dumps(select(args.domain, args.lane, args.perspective), sort_keys=True, separators=(",", ":")))
        return 0
    sys.stdout.buffer.write(get(args.member_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
