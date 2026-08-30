#!/usr/bin/env python3
"""Build and check one design run.

The tool writes stable run files. It does not judge design work.

Exit codes:
  0  the command passed
  1  the run is blocked
  2  the command input is bad
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from check_context_routing import build_context_bundle, routing_digest
from lib.run_completion import completion_payload
from lib.run_contract import MODEL_ACTIONS, NEEDED, NEXT_AFTER_RECORD
from lib.run_io import dump, load
from lib.run_validation import valid_record
from review_checklist import REVIEW_INDEX
from run_scaffold import make_packet, scaffold_files
from select_rules import base_rules


def read_intake(path):
    try:
        return load(path)
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: intake could not be read: {error}", file=sys.stderr)
        return None


def write_scaffold(out, run_id, data):
    for name, value in scaffold_files(run_id, data).items():
        dump(out / name, {"version": "1.0.0", **value})


def report_start(run_id, status, next_action):
    print(json.dumps({"run_id": run_id, "status": status,
                      "next_action": next_action}, sort_keys=True))


def resume_run(run_path, out, run_id, data, root):
    try:
        existing = load(run_path)
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: existing run could not be read: {error}", file=sys.stderr)
        return 2
    if existing.get("run_id") != run_id or existing.get("intake") != data:
        print("blocked: run directory belongs to a different intake",
              file=sys.stderr)
        return 1
    if existing.get("context_routing_sha256") != routing_digest(root):
        print("blocked: context routes changed after start", file=sys.stderr)
        return 1
    write_scaffold(out, run_id, data)
    report_start(run_id, existing.get("status", "READY"),
                 existing.get("next"))
    return 0


def start(args):
    data = read_intake(args.intake)
    if data is None:
        return 2
    missing = [key for key in NEEDED if not data.get(key)]
    if missing:
        print("blocked: missing " + ", ".join(missing), file=sys.stderr)
        return 1
    root = Path(__file__).resolve().parents[1]
    raw = json.dumps(data, sort_keys=True).encode()
    run_id = hashlib.sha256(raw).hexdigest()[:16]
    out = Path(args.run_dir)
    run_path = out / "run.json"
    if run_path.is_file():
        return resume_run(run_path, out, run_id, data, root)
    rules = base_rules(load(root / "assets" / "simplicity-contract.json"))
    run = {"version": "1.0.0", "run_id": run_id, "status": "READY",
           "intake": data, "rules": rules, "rules_selected": False,
           "context_routing_sha256": routing_digest(root),
           "next": "source_meaning"}
    dump(run_path, run)
    write_scaffold(out, run_id, data)
    report_start(run_id, "READY", "source_meaning")
    return 0


def read_run(out):
    try:
        return load(out / "run.json")
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: run could not be read: {error}", file=sys.stderr)
        return None


def packet(args):
    if args.action not in MODEL_ACTIONS:
        print(f"error: unknown model action: {args.action}", file=sys.stderr)
        return 2
    out = Path(args.run_dir)
    run = read_run(out)
    if run is None:
        return 2
    root = Path(__file__).resolve().parents[1]
    if run.get("context_routing_sha256") != routing_digest(root):
        print("blocked: context routes changed after start", file=sys.stderr)
        return 1
    if run.get("next") != args.action:
        print(f"blocked: next action is {run.get('next')}, not {args.action}",
              file=sys.stderr)
        return 1
    try:
        context = build_context_bundle(root, args.action)
    except ValueError as error:
        print(f"blocked: {error}", file=sys.stderr)
        return 1
    data = make_packet(args.action, run["run_id"], run["intake"],
                       run["rules"], args.item_id)
    data["context_bundle"] = context
    item = re.sub(r"[^a-zA-Z0-9_-]+", "-", args.item_id or "").strip("-")
    name = args.action + (f"--{item}" if item else "") + ".json"
    dump(out / "packets" / name, data)
    print(json.dumps({"action": args.action, "status": "PACKET_READY"},
                     sort_keys=True))
    return 0


def read_record_inputs(args, out):
    try:
        result = load(args.result)
        packet = load(out / "packets" / f"{result.get('action', '')}.json")
        checklist = load(out / "review-checklist.json")
        run = load(out / "run.json")
        return result, packet, checklist, run
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: record input could not be read: {error}", file=sys.stderr)
        return None


def save_record(out, result, run):
    dump(out / "records" / f"{result['action']}.json", result)
    run.setdefault("action_results", {})[result["action"]] = result["decision"]
    run["next"] = NEXT_AFTER_RECORD[result["action"]]
    if result["decision"] == "BLOCKED":
        run["status"] = "BLOCKED"
    elif result["decision"] == "REVISE" and run.get("status") != "BLOCKED":
        run["status"] = "STALE"
    dump(out / "run.json", run)


def record(args):
    out = Path(args.run_dir)
    inputs = read_record_inputs(args, out)
    if inputs is None:
        return 2
    result, packet, checklist, run = inputs
    if checklist != REVIEW_INDEX:
        print("blocked: missing canonical review checklist", file=sys.stderr)
        return 1
    if run.get("next") != result.get("action"):
        print(f"blocked: next action is {run.get('next')}, not "
              f"{result.get('action')}", file=sys.stderr)
        return 1
    missing = valid_record(result, packet)
    if missing:
        print("blocked: missing " + ", ".join(missing), file=sys.stderr)
        return 1
    save_record(out, result, run)
    print(json.dumps({"action": result["action"], "status": "RECORDED"},
                     sort_keys=True))
    return 0


def check(args):
    payload = completion_payload(args.run_dir)
    print(json.dumps(payload, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


def parser():
    top = argparse.ArgumentParser(description=__doc__)
    sub = top.add_subparsers(dest="command", required=True)
    begin = sub.add_parser("start", help="make a stable run folder")
    begin.add_argument("--intake", required=True)
    begin.add_argument("--run-dir", required=True)
    make = sub.add_parser("packet", help="make one model work packet")
    make.add_argument("--run-dir", required=True)
    make.add_argument("--action", required=True)
    make.add_argument("--item-id")
    save = sub.add_parser("record", help="check and save one model result")
    save.add_argument("--run-dir", required=True)
    save.add_argument("--result", required=True)
    done = sub.add_parser("check", help="check all model records")
    done.add_argument("--run-dir", required=True)
    return top


def main(argv=None):
    args = parser().parse_args(argv)
    return {"start": start, "packet": packet, "record": record,
            "check": check}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
