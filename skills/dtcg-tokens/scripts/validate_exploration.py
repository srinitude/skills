#!/usr/bin/env python3
"""Validate the source frontier and exploration contracts.

Exit codes:
  0  contract assets pass
  1  one or more contract checks fail
  2  usage or input data is invalid
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def read_json(path, errors):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{path}: {error}")
        return {}


def validate(skill):
    errors = []
    frontier = read_json(skill / "assets/creative-source-frontier.json", errors)
    experiment = read_json(skill / "assets/experiment-contract.json", errors)
    manifest = read_json(skill / "assets/exploration-corpus/manifest.json", errors)
    synthesis = read_json(skill / "assets/exploration-corpus/synthesis-contract.json", errors)
    if len(frontier.get("mechanism_families", [])) < 6:
        errors.append("frontier needs six mechanism families")
    if frontier.get("coverage", {}).get("minimum_distant_domains") != 3:
        errors.append("frontier needs three distant domains")
    retention = experiment.get("retention", {})
    if retention.get("minimum_tokens") != 3 or retention.get("minimum_mechanism_families") != 3:
        errors.append("experiment retention must be three tokens from three mechanism families")
    if not retention.get("require_inversion_or_antithesis"):
        errors.append("experiment retention needs inversion or antithesis")
    for name, record in manifest.get("shards", {}).items():
        path = skill / record.get("path", "")
        if not path.is_file():
            errors.append(f"missing corpus shard {name}: {path}")
        else:
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            if record.get("sha256") != actual_hash:
                errors.append(f"corpus shard hash mismatch {name}: {path}")
            read_json(path, errors)
    if synthesis.get("minimum_candidates") != 12 or synthesis.get("minimum_per_lane") != 3:
        errors.append("synthesis needs twelve candidates with three per lane")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", nargs="?", default=".", help="skill directory")
    args = parser.parse_args(argv)
    skill = Path(args.skill_dir).resolve()
    if not (skill / "SKILL.md").is_file():
        print(f"error: no SKILL.md inside {skill}", file=sys.stderr)
        return 2
    errors = validate(skill)
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "errors": errors}, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
