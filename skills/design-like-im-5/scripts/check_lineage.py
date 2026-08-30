#!/usr/bin/env python3
"""Check the one-way part chain.

Exit codes:
  0  the chain passed
  1  the chain failed
  2  the input could not be read
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

LAYERS = ["tokens", "atoms", "molecules", "organisms", "templates",
          "screens", "interactions"]


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(path, data):
    text = json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n"
    path.write_text(text, encoding="utf-8")


def find_cycle(node, links, seen, active):
    if node in active:
        return True
    if node in seen:
        return False
    active.add(node)
    for child in links.get(node, []):
        if find_cycle(child, links, seen, active):
            return True
    active.remove(node)
    seen.add(node)
    return False


def check(doc):
    issues = []
    parts = doc.get("parts", [])
    by_id = {part.get("id"): part for part in parts}
    if len(by_id) != len(parts):
        issues.append("part ids must be unique")
    if doc.get("dtcg_run", {}).get("status") != "PASS":
        issues.append("the token run did not pass")
    for part in parts:
        check_part(part, by_id, issues)
    links = {key: value.get("deps", []) for key, value in by_id.items()}
    if any(find_cycle(key, links, set(), set()) for key in links):
        issues.append("the chain has a cycle")
    used = {dep for deps in links.values() for dep in deps}
    for part in parts:
        if part.get("layer") != "interactions" and part.get("id") not in used:
            if not part.get("exclusion"):
                issues.append(f"{part.get('id')}: unused part")
    return issues


def check_part(part, by_id, issues):
    name = part.get("id", "missing-id")
    layer = part.get("layer")
    if layer not in LAYERS:
        issues.append(f"{name}: bad layer")
        return
    pos = LAYERS.index(layer)
    deps = part.get("deps", [])
    if pos and not deps:
        issues.append(f"{name}: has no lower part")
    prior = LAYERS[pos - 1] if pos else None
    direct = False
    for dep in deps:
        if dep not in by_id:
            issues.append(f"{name}: missing part {dep}")
            continue
        dep_pos = LAYERS.index(by_id[dep].get("layer"))
        if dep_pos >= pos:
            issues.append(f"{name}: bad link to {dep}")
        if by_id[dep].get("layer") == prior:
            direct = True
        if by_id[dep].get("status") != "PASS":
            issues.append(f"{name}: stale or failed part {dep}")
    if pos and not direct:
        issues.append(f"{name}: skips {prior}")


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", help="part chain JSON file")
    parser.add_argument(
        "--run-dir",
        help="run folder that must be waiting at check_lineage")
    return parser.parse_args(argv)


def record_run_proof(run_dir, manifest_path):
    out = Path(run_dir)
    try:
        run = load(out / "run.json")
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: run could not be read: {error}", file=sys.stderr)
        return 2
    if run.get("next") != "check_lineage":
        print(f"blocked: next action is {run.get('next')}, not check_lineage",
              file=sys.stderr)
        return 1
    manifest = Path(manifest_path).resolve()
    dump(out / "lineage-check.json", {
        "action": "check_lineage", "manifest": str(manifest),
        "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "status": "PASS", "version": "1.0.0",
    })
    run["next"] = "final_check"
    dump(out / "run.json", run)
    return 0


def main(argv=None):
    args = parse_args(argv)
    try:
        issues = check(load(args.manifest))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"error: could not read the part chain: {error}", file=sys.stderr)
        return 2
    for issue in issues:
        print(issue)
    print(f"lineage check: {len(issues)} problems")
    if issues:
        return 1
    return record_run_proof(args.run_dir, args.manifest) if args.run_dir else 0


if __name__ == "__main__":
    sys.exit(main())
