#!/usr/bin/env python3
"""Build or check every Figma skill file hash."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "evals/source-lineage.json"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def files():
    return sorted(path for path in ROOT.rglob("*") if path.is_file()
                  and "__pycache__" not in path.parts and path != TARGET)


def version():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"(?m)^\s*version:\s*[\"']?([^\"'\s]+)", text)
    if not match:
        raise ValueError("SKILL.md needs a version")
    return match.group(1)


def source_case_ids():
    cases = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))
    return [item["source_id"] for item in cases["cases"]]


def record():
    source = [{"path": path.relative_to(ROOT).as_posix(),
               "sha256": digest(path)} for path in files()]
    public = [{"path": item["path"], "source_paths": [item["path"]]}
              for item in source]
    native = ROOT / "assets/source-manifest.json"
    return {"schema_version": 1, "public_version": version(),
            "native_version": "2026-09-02",
            "native_manifest_sha256": digest(native),
            "public_files": public, "source_files": source,
            "source_case_ids": source_case_ids()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        expected = record()
        if args.write:
            TARGET.write_text(json.dumps(expected, indent=2) + "\n")
            print(f"Figma skill hashes: wrote {len(expected['source_files'])}")
            return 0
        current = json.loads(TARGET.read_text())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"FAIL {error}")
        return 2
    same = current == expected
    print(f"Figma skill hashes: {'current' if same else 'old'}")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
