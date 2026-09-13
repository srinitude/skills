#!/usr/bin/env python3
"""Plan or individually review source-lineage maintenance for named registry skills.

Usage: refresh_registry_lineage.py SKILL... [--plan | --review REQUEST]
Example: mise run refresh-registry-lineage -- clock-anchor --plan
Save the next planned content_base64 bytes unchanged and provide its ordinary
write-file request, or its separate body-revision request for SKILL.md. Each call
applies at most that next file. Replan after every effect, retaining earlier writes;
then run source/domain validation. Exit 0: planned or one file written; 2: invalid
input or failed effect. A successful call does not accept the complete skill.
"""
import argparse
import json
import sys
from pathlib import Path

from registry_lineage_sources import (NAME_RE, FACTORY_SOURCE, SCAFFOLDING_SOURCE, validate_names,
    digest, public_paths, repository_entry, baseline_state, refresh_repository_entry,
    retained_source_state, classify_source_kind, canonical_digest)
from registry_lineage_plan import build_plan
from registry_lineage_review import refresh


def repository_root():
    return Path(__file__).resolve().parents[3]


def refresh_skill(root, skill, review=None):
    return refresh(root, [skill], review)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skills", nargs="+")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--plan", action="store_true")
    modes.add_argument("--review")
    args = parser.parse_args(argv)
    root = repository_root()
    try:
        validate_names(root, args.skills)
        if args.plan:
            result = {"status": "PASS", "mode": "plan", "plan": build_plan(root, args.skills)}
        else:
            result = refresh(root, args.skills, args.review)
    except (OSError, KeyError, ValueError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
