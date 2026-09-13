#!/usr/bin/env python3
"""Check or refresh this skill's source-lineage record.

Usage:
  python3 scripts/check_lineage.py [SKILL_DIR] [--plan | --write --review REQUEST]

Exit codes:
  0  lineage is current, or refresh succeeded
  1  lineage is stale or invalid
  2  bad usage

Example:
  mise run lineage -- --plan
  mise run refresh-lineage -- --review /absolute/request.json

Review uses the existing ledger write-file request, current initial_body_review
and the plan's exact content_utf8 text (indent=2 plus newline). Full governing reads,
canonical lineage derivation, a cooperating package lock, current request checks
and conditional restoration guard each effect. Declarations are not acceptance.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from validate_skill import parse_header, split_frontmatter
from skill_package import owned_paths
from agentic_request_contract import read_json
from review_ledger_context import require
from review_ledger_source import read_file
from review_ledger_write import write_file

SELF = Path(__file__).resolve().parents[1]
LINEAGE = "evals/source-lineage.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def files(root):
    root = root.resolve()
    return sorted(path.relative_to(root).as_posix() for path in owned_paths(root)
                  if path.relative_to(root).as_posix() != LINEAGE)


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


def reviewed_refresh(root, review):
    require(review is not None, 'lineage writes require --review with a current write-file request')
    binding = {'path': str(review)}
    raw = read_file(binding)
    request = read_json(raw.decode('utf-8'))
    require(isinstance(request, dict) and isinstance(request.get('change'), dict)
            and request['change'].get('path') == LINEAGE,
            'lineage review must target evals/source-lineage.json')
    def current_inputs():
        require(read_file(binding) == raw, 'lineage review request changed')
        expected = (json.dumps(current_document(root), indent=2) + '\n').encode()
        return read_file(request['change']['new_file']) == expected
    result = write_file(request, root, effect_check=current_inputs)
    return {'status': 'PASS', 'mode': 'write', 'files': len(files(root)), 'change': result}


def report(root, write=False, review=None, plan=False):
    require(not (write and plan) and (review is None or write), 'review belongs only to write mode')
    if write:
        return reviewed_refresh(root, review)
    path = root / LINEAGE
    expected = current_document(root)
    if plan:
        return {'status': 'PASS', 'mode': 'plan', 'content_utf8': json.dumps(expected, indent=2) + '\n'}
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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--plan", action="store_true")
    parser.add_argument("--review")
    args = parser.parse_args(argv)
    if args.review is not None and not args.write:
        parser.error("--review belongs only to --write")
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
        result = report(root, args.write, args.review, args.plan)
    except (OSError, ValueError, KeyError, TypeError) as error:
        result = {"status": "FAIL", "problems": [str(error)]}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
