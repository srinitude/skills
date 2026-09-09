#!/usr/bin/env python3
"""Create a read-only baseline for standardizing one skill.

Usage:
  python3 scripts/plan_standardize.py SKILL_ROOT

Exit codes:
  0  baseline report written to stdout
  1  target is not a skill directory
  2  bad usage

Example:
  python3 scripts/plan_standardize.py ../example-skill
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
CORPUS = SKILL_DIR / "assets" / "source-shape-corpus.json"
REQUIRED = [
    "SKILL.md", "mise.toml", ".github/workflows/ci.yml",
    "references/generation-contract.md",
    "references/resource-and-experiment-design.md", "references/decisions.md",
    "references/use-case-specificity.md", "assets/improvement-contract.json",
    "assets/use-case-contract.json", "examples",
    "assets/decision-records.json", "assets/invocation-receipt-template.json",
    "scripts", "scripts/tests", "evals/evals.json",
    "evals/trigger-queries.json",
]
IGNORED_PARTS = {".git", ".mise", "__pycache__", "node_modules",
                 ".pytest_cache", ".mypy_cache", ".ruff_cache"}
IGNORED_NAMES = {".DS_Store"}


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def owned_source(path):
    return (path.name not in IGNORED_NAMES
            and not (set(path.parts) & IGNORED_PARTS)
            and path.suffix not in {".pyc", ".pyo"})


def file_records(root):
    records = []
    files = (item for item in root.rglob("*")
             if item.is_file() and not item.is_symlink()
             and owned_source(item.relative_to(root)))
    for path in sorted(files):
        data = path.read_bytes()
        records.append({"path": path.relative_to(root).as_posix(),
                        "sha256": digest_bytes(data), "bytes": len(data)})
    return records


def baseline_digest(records):
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return "sha256:" + digest_bytes(canonical.encode("utf-8"))


def load_portability_rules():
    return json.loads(CORPUS.read_text(encoding="utf-8"))


def portable_destination(path, rules):
    parts = Path(path).parts
    if path in rules["portable_path_map"]:
        return rules["portable_path_map"][path]
    if parts and parts[0] in rules["hidden_owner_roots"]:
        return Path(".agents", *parts[1:]).as_posix()
    return None


def portable_paths(records, rules):
    mapped = [{"source": item["path"],
               "destination": portable_destination(item["path"], rules)}
              for item in records
              if portable_destination(item["path"], rules)]
    by_destination = {}
    for item in mapped:
        by_destination.setdefault(item["destination"], []).append(item["source"])
    collisions = [sources for sources in by_destination.values()
                  if len(sources) > 1]
    return mapped, collisions


def unclassified_host_paths(records, rules):
    known = set(rules["hidden_owner_roots"])
    neutral = set(rules["neutral_hidden_roots"])
    terms = rules["unknown_root_terms"]
    found = []
    for item in records:
        root = Path(item["path"]).parts[0]
        candidate = root.startswith(".") and any(term in root for term in terms)
        if candidate and root not in known and root not in neutral:
            found.append(item["path"])
    return found


def symlink_paths(root):
    return sorted(item.relative_to(root).as_posix()
                  for item in root.rglob("*") if item.is_symlink())


def build_report(root):
    rules = load_portability_rules()
    records = file_records(root)
    path_map, collisions = portable_paths(records, rules)
    present = [name for name in REQUIRED if (root / name).exists()]
    missing = [name for name in REQUIRED if name not in present]
    return {"target": str(root), "baseline_digest": baseline_digest(records),
            "files": records, "present_required": present,
            "missing_required": missing, "portable_path_map": path_map,
            "path_collisions": collisions,
            "unknown_shape_policy": rules["unknown_shape"],
            "unclassified_host_paths": unclassified_host_paths(records, rules),
            "symlinks": symlink_paths(root),
            "writes": 0}


def is_blocked(report):
    return bool(report["path_collisions"]
                or report["unclassified_host_paths"]
                or report["symlinks"])


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill_root")
    args = parser.parse_args(argv)
    candidate = Path(args.skill_root)
    if candidate.is_symlink():
        print(json.dumps({"target": str(candidate), "writes": 0,
                          "problems": ["skill root is a symlink"]}, indent=2))
        return 1
    root = candidate.resolve()
    if not (root / "SKILL.md").is_file():
        print(f"FAIL not a skill directory: {root}")
        return 1
    report = build_report(root)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if is_blocked(report) else 0


if __name__ == "__main__":
    sys.exit(main())
