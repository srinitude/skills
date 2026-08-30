"""Read run proof and set the end state."""
import hashlib
import json
from pathlib import Path

from lib.run_contract import MODEL_ACTIONS
from lib.run_io import load


def read_run_requirements(out):
    try:
        run = load(out / "run.json")
    except (OSError, json.JSONDecodeError):
        return {}, ["run.json"]
    missing = []
    if not run.get("rules_selected"):
        missing.append("select_rules")
    if run.get("next") != "final_check":
        missing.append(f"next_action:{run.get('next')}")
    return run, missing


def lineage_missing(out):
    try:
        lineage = load(out / "lineage-check.json")
        manifest = Path(lineage["manifest"])
        current_hash = hashlib.sha256(manifest.read_bytes()).hexdigest()
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return ["check_lineage"]
    if lineage.get("status") != "PASS":
        return ["check_lineage"]
    if lineage.get("manifest_sha256") != current_hash:
        return ["check_lineage"]
    return []


def read_decisions(out):
    decisions = {}
    for name in MODEL_ACTIONS:
        try:
            decisions[name] = load(
                out / "records" / f"{name}.json").get("decision")
        except (OSError, json.JSONDecodeError):
            continue
    return decisions


def completion_payload(run_dir):
    out = Path(run_dir)
    missing = [name for name in MODEL_ACTIONS
               if not (out / "records" / f"{name}.json").is_file()]
    _, run_missing = read_run_requirements(out)
    missing.extend(run_missing)
    missing.extend(lineage_missing(out))
    decisions = read_decisions(out)
    blocked = sorted(name for name, value in decisions.items()
                     if value == "BLOCKED")
    stale = sorted(name for name, value in decisions.items()
                   if value == "REVISE")
    invalid = sorted(name for name, value in decisions.items()
                     if value not in {"PASS", "REVISE", "BLOCKED"})
    missing.extend(f"invalid_decision:{name}" for name in invalid)
    status = "BLOCKED" if missing or blocked else "STALE" if stale else "PASS"
    return {"status": status, "missing_records": sorted(set(missing)),
            "blocked_records": blocked, "stale_records": stale}
