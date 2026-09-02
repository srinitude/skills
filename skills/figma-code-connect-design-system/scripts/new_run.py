#!/usr/bin/env python3
"""Create a design-system run ledger without product mutations.

Exit codes:
  0  ledger written
  1  output already exists or cannot be written
  2  invalid arguments
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "assets" / "run-contract.json"


def parser():
    tool = argparse.ArgumentParser(description=__doc__)
    tool.add_argument("--output", required=True, help="new run JSON path")
    tool.add_argument("--mode", required=True, choices=["create", "update"])
    tool.add_argument("--platform", required=True)
    tool.add_argument("--ui-scope", required=True)
    tool.add_argument("--source", action="append", required=True,
                      help="TYPE=LOCATION; repeat for each source")
    tool.add_argument("--run-id", help="stable run identifier")
    return tool


def slug(value):
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "ui"


def load_contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def parse_sources(values, allowed):
    sources = []
    for index, value in enumerate(values, start=1):
        kind, separator, location = value.partition("=")
        if not separator or kind not in allowed or not location.strip():
            raise ValueError(f"invalid --source {value!r}")
        sources.append({
            "id": f"source-{index:02d}",
            "type": kind,
            "location": location,
            "authority": "unresolved",
            "status": "available",
        })
    return sources


def make_record(args, contract, sources):
    run_id = args.run_id or f"ds-{args.mode}-{slug(args.ui_scope)}"
    stages = [{"id": name, "status": "planned", "proof": []}
              for name in contract["stage_order"]]
    return {
        "schema_version": contract["schema_version"],
        "run_id": run_id,
        "mode": args.mode,
        "target": {"platform": args.platform, "ui_scope": args.ui_scope},
        "sources": sources,
        "hierarchy": contract["hierarchy"],
        "template_kinds": contract["template_kinds"],
        "stages": stages,
        "capabilities": [],
        "requirements": [], "quality_evidence": {},
        "property_kind_dispositions": [], "property_parity": [],
        "governance": [],
        "comparison_inventory": [], "controlled_comparisons": {},
        "lineage": [],
        "permissions": {
            "repository_write": "not_granted",
            "figma_write": "not_granted",
            "publish": "not_granted",
            "unpublish": "not_granted",
            "delete": "not_granted"
        },
        "mutations": [],
        "unknowns": [],
        "completion": "planned"
    }


def write_new(path, record):
    if path.exists():
        raise FileExistsError(f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def main(argv=None):
    args = parser().parse_args(argv)
    contract = load_contract()
    try:
        sources = parse_sources(args.source, contract["source_types"])
        record = make_record(args, contract, sources)
        write_new(Path(args.output), record)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"created": str(Path(args.output)),
                      "run_id": record["run_id"],
                      "status": "planned"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
