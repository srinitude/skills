#!/usr/bin/env python3
"""Check or refresh this skill's source-lineage record.

Usage:
  python3 scripts/check_lineage.py [SKILL_DIR] [--write]

Exit codes:
  0  lineage is current, or refresh succeeded
  1  lineage is stale or invalid
  2  bad usage

Example:
  python3 scripts/check_lineage.py . --write
"""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from validate_skill import parse_header, split_frontmatter

SELF = Path(__file__).resolve().parents[1]
LINEAGE = "evals/source-lineage.json"
SKIP_PARTS = {".git", ".mise", "__pycache__", "node_modules",
              ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SKIP_NAMES = {".DS_Store"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def files(root):
    found = []
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if path.is_file() and not path.is_symlink() and relative != LINEAGE:
            if (not SKIP_PARTS.intersection(path.parts)
                    and path.name not in SKIP_NAMES
                    and path.suffix not in {".pyc", ".pyo"}):
                found.append(relative)
    return sorted(found)


def symlink_paths(root):
    return sorted(path.relative_to(root).as_posix()
                  for path in root.rglob("*") if path.is_symlink())


def metadata(root):
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    header, _, error = split_frontmatter(text)
    if error:
        raise ValueError(error)
    fields, error = parse_header(header)
    if error or not isinstance(fields.get("metadata"), dict):
        raise ValueError(error or "SKILL.md metadata must be a mapping")
    return fields["metadata"]


def version(root):
    value = metadata(root).get("version")
    if not isinstance(value, str) or not value:
        raise ValueError("SKILL.md has no string metadata version")
    return value


def case_ids(root):
    data = json.loads((root / "evals/cases.json").read_text(encoding="utf-8"))
    return [item["source_id"] for item in data["cases"]]


def current_document(root):
    paths = files(root)
    sources = [{"path": path, "sha256": digest((root / path).read_bytes())}
               for path in paths]
    packet = "".join(f"{x['path']}\0{x['sha256']}\n" for x in sources)
    release = version(root)
    document = {"schema_version": 1, "public_version": release,
            "native_version": release,
            "native_manifest_sha256": digest(packet.encode()),
            "public_files": [{"path": path, "source_paths": [path]}
                             for path in paths],
            "source_files": sources, "source_case_ids": case_ids(root)}
    prior = root / LINEAGE
    if prior.is_file():
        recorded = json.loads(prior.read_text(encoding="utf-8"))
        if "derivation" in recorded:
            check_derivation(recorded["derivation"])
            check_scope_binding(root, recorded["derivation"])
            document["derivation"] = recorded["derivation"]
    return document


def check_derivation(record):
    if not isinstance(record, dict) or record.get("schema_version") != 1:
        raise ValueError("invalid derivation schema")
    source = record.get("source", {})
    if source.get("scope") not in ("user", "project") or record.get("target_scope") not in ("user", "project"):
        raise ValueError("invalid derivation scopes")
    if source["scope"] == record["target_scope"]:
        raise ValueError("derivation scopes must differ")
    for key in ["identity", "version"]:
        if not isinstance(source.get(key), str) or not source[key]:
            raise ValueError(f"derivation source needs {key}")
    hashes = [source.get("digest"), record.get("candidate_digest"), record.get("plan_digest")]
    for mapping in [source.get("baseline"), record.get("target_baseline")]:
        if not isinstance(mapping, dict) or not mapping:
            raise ValueError("derivation needs complete source and target baselines")
        hashes.extend(mapping.values())
    if any(not isinstance(value, str) or not re.fullmatch(r"[a-f0-9]{64}", value) for value in hashes):
        raise ValueError("invalid derivation digest")
    for key in ["adaptations", "requirements"]:
        if not isinstance(record.get(key), list) or not record[key] or not all(isinstance(x, str) and x for x in record[key]):
            raise ValueError(f"derivation needs {key}")
    if not isinstance(record.get("compatibility"), str) or not record["compatibility"]:
        raise ValueError("derivation needs compatibility limits")
    if record["target_scope"] == "project" and not record.get("target_project"):
        raise ValueError("project derivation needs a target project identity")


def check_scope_binding(root, record):
    if metadata(root).get("scope") != record["target_scope"]:
        raise ValueError("derivation target scope differs from SKILL.md metadata.scope")
    if record["target_scope"] == "user" and record.get("target_project") is not None:
        raise ValueError("a user variant must not bind a target project")
    if any(not re.fullmatch(r"[a-f0-9]{64}", key) for key in record["source"]["baseline"]):
        raise ValueError("source baseline must use opaque path digests")


def write_atomic(path, document):
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(document, indent=2) + "\n"
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False,
                                     encoding="utf-8") as handle:
        handle.write(payload)
        temporary = handle.name
    os.replace(temporary, path)


def report(root, write=False):
    path = root / LINEAGE
    links = symlink_paths(root)
    if links:
        return {"status": "FAIL", "mode": "write" if write else "check",
                "files": len(files(root)),
                "problems": ["symlinks are not portable: " + ", ".join(links)]}
    expected = current_document(root)
    if write:
        write_atomic(path, expected)
        return {"status": "PASS", "mode": "write", "files": len(files(root))}
    try:
        actual = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {"status": "FAIL", "problems": [str(error)]}
    problems = [] if actual == expected else ["source-lineage.json is stale"]
    if actual.get("public_version") != expected["public_version"]:
        problems.append("public_version differs from SKILL.md")
    return {"status": "PASS" if not problems else "FAIL",
            "mode": "check", "files": len(files(root)), "problems": problems}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill_dir", nargs="?", default=str(SELF))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    candidate = Path(args.skill_dir)
    if candidate.is_symlink():
        result = {"status": "FAIL", "problems": ["skill root is a symlink"]}
        print(json.dumps(result, sort_keys=True))
        return 1
    root = candidate.resolve()
    if not root.is_dir():
        print(json.dumps({"status": "FAIL", "problems": ["not a directory"]}))
        return 1
    try:
        result = report(root, args.write)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        result = {"status": "FAIL", "problems": [str(error)]}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
