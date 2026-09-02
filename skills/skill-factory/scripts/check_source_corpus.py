#!/usr/bin/env python3
"""Validate or apply the factory source-shape corpus.

Usage:
  python3 scripts/check_source_corpus.py [SOURCE_REPOSITORY]

Exit codes:
  0  corpus or repository audit passes
  1  corpus or repository audit fails
  2  bad usage

Example:
  python3 scripts/check_source_corpus.py /path/to/source
"""
import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
CORPUS = SKILL_DIR / "assets" / "source-shape-corpus.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def load_corpus():
    try:
        return json.loads(CORPUS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read corpus: {error}") from error


def corpus_problems(data):
    found = []
    source = data.get("source", {})
    if source.get("url") != "https://github.com/srinitude/skills":
        found.append("source.url is not the current corpus owner")
    if not SHA_RE.fullmatch(source.get("commit", "")):
        found.append("source.commit must be a full Git commit")
    if data.get("unknown_shape") != "BLOCKED":
        found.append("unknown_shape must equal BLOCKED")
    groups = data.get("clients", []) + data.get("package_formats", [])
    ids = [item.get("id") for item in groups]
    if not ids or len(ids) != len(set(ids)):
        found.append("client ids must be present and unique")
    for item in groups:
        if not item.get("markers"):
            found.append(f"{item.get('id')} has no markers")
    return found


def all_files(root):
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink() and ".git" not in path.parts
    }


def symlink_files(root):
    return sorted(path.relative_to(root).as_posix()
                  for path in root.rglob("*") if path.is_symlink())


def detected(files, groups):
    return [item["id"] for item in groups
            if set(item["markers"]) <= files]


def unknown_host_files(files, data):
    known = set(data["hidden_owner_roots"])
    neutral = set(data["neutral_hidden_roots"])
    terms = tuple(data["unknown_root_terms"])
    found = set()
    for path in files:
        root = Path(path).parts[0]
        candidate = root.startswith(".") and any(term in root for term in terms)
        if candidate and root not in known and root not in neutral:
            found.add(path)
    return found


def audit(root, data):
    files = all_files(root)
    clients = detected(files, data["clients"])
    formats = detected(files, data["package_formats"])
    groups = data["clients"] + data["package_formats"]
    claimed = {path for item in groups for path in item["markers"]}
    candidates = {path for path in files for pattern in data["candidate_patterns"]
                  if fnmatch.fnmatch(path, pattern)}
    unknown = unknown_host_files(files, data)
    return (clients, formats, sorted((candidates - claimed) | unknown),
            symlink_files(root))


def report(data, root=None):
    problems = corpus_problems(data)
    detected_clients, detected_formats, unclassified, symlinks = [], [], [], []
    if root is not None and not problems:
        detected_clients, detected_formats, unclassified, symlinks = audit(root, data)
        if not detected_clients and not detected_formats:
            problems.append("source has no recognized client or package format")
    client_ids = [item.get("id") for item in data.get("clients", [])]
    format_ids = [item.get("id") for item in data.get("package_formats", [])]
    missing_clients = sorted(set(client_ids) - set(detected_clients)) if root else []
    missing_formats = sorted(set(format_ids) - set(detected_formats)) if root else []
    passed = not problems and not unclassified and not symlinks
    return {"status": "PASS" if passed else "FAIL",
            "source": data.get("source"),
            "clients": client_ids, "package_formats": format_ids,
            "detected_clients": detected_clients,
            "detected_package_formats": detected_formats,
            "missing_clients": missing_clients,
            "missing_package_formats": missing_formats,
            "problems": problems,
            "unclassified": unclassified,
            "symlinks": symlinks}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("repository", nargs="?")
    args = parser.parse_args(argv)
    try:
        data = load_corpus()
    except ValueError as error:
        print(json.dumps({"status": "FAIL", "problems": [str(error)]}))
        return 1
    candidate = Path(args.repository) if args.repository else None
    if candidate is not None and candidate.is_symlink():
        result = {"status": "FAIL",
                  "problems": ["repository root is a symlink"]}
        print(json.dumps(result, sort_keys=True))
        return 1
    root = candidate.resolve() if candidate is not None else None
    if root is not None and not root.is_dir():
        print(json.dumps({"status": "FAIL",
                          "problems": [f"not a directory: {root}"]}))
        return 1
    result = report(data, root)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
