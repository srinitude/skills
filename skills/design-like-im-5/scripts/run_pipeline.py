#!/usr/bin/env python3
"""Build and check one design run.

The tool writes stable run files. It does not judge design work.

Exit codes:
  0  the command passed
  1  the run is blocked
  2  the command input is bad
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

from review_checklist import (ANSWER_FIELDS, REVIEW_DECISIONS,
                              REVIEW_CHECKLIST, REVIEW_INDEX)
from run_scaffold import make_packet, scaffold_files

NEEDED = ["outcome", "audience", "platform", "primary_tasks",
          "source_permissions", "proof_threshold"]
MODEL_ACTIONS = ["source_meaning", "atom_judgment", "part_design",
                 "screen_design", "motion_judgment", "visual_review",
                 "plain_readback", "state_judgment"]
REVIEW_ACTIONS = {"state_judgment", "visual_review"}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(path, data):
    text = json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")


def missing_fields(data):
    return [key for key in NEEDED if not data.get(key)]


def choose_rules(contract, data):
    picked = []
    for rule in contract["rules"]:
        if rule.get("always") or data.get(rule.get("field")) in rule.get("values", []):
            picked.append(rule["id"])
    return picked


def make_scaffold(out, run_id, data):
    for name, value in scaffold_files(run_id, data).items():
        dump(out / name, {"version": "1.0.0", **value})


def start(args):
    try:
        data = load(args.intake)
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: intake could not be read: {error}", file=sys.stderr)
        return 2
    missing = missing_fields(data)
    if missing:
        print("blocked: missing " + ", ".join(missing), file=sys.stderr)
        return 1
    root = Path(__file__).resolve().parents[1]
    contract = load(root / "assets" / "simplicity-contract.json")
    raw = json.dumps(data, sort_keys=True).encode()
    run_id = hashlib.sha256(raw).hexdigest()[:16]
    rules = choose_rules(contract, data)
    out = Path(args.run_dir)
    run = {"version": "1.0.0", "run_id": run_id, "status": "READY",
           "intake": data, "rules": rules, "next": "source_meaning"}
    dump(out / "run.json", run)
    make_scaffold(out, run_id, data)
    print(json.dumps({"run_id": run_id, "status": "READY",
                      "next_action": "source_meaning"}, sort_keys=True))
    return 0


def packet(args):
    if args.action not in MODEL_ACTIONS:
        print(f"error: unknown model action: {args.action}", file=sys.stderr)
        return 2
    out = Path(args.run_dir)
    try:
        run = load(out / "run.json")
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: run could not be read: {error}", file=sys.stderr)
        return 2
    data = make_packet(args.action, run["run_id"], run["intake"], run["rules"],
                       args.item_id)
    item = re.sub(r"[^a-zA-Z0-9_-]+", "-", args.item_id or "").strip("-")
    name = args.action + (f"--{item}" if item else "") + ".json"
    target = out / "packets" / name
    dump(target, data)
    print(json.dumps({"action": args.action, "status": "PACKET_READY"},
                     sort_keys=True))
    return 0


def valid_record(record, packet):
    needed = ["action", "decision", "evidence", "reason",
              "counterevidence", "uncertainty", "affected"]
    missing = [key for key in needed if key not in record]
    if record.get("action") != packet.get("action"):
        missing.append("matching action")
    if record.get("decision") not in packet["allowed_decisions"]:
        missing.append("allowed decision")
    if not isinstance(record.get("evidence"), list) or not record.get("evidence"):
        missing.append("evidence item")
    if packet.get("action") == "state_judgment":
        missing.extend(valid_state_record(record))
        for item in record.get("state_items", []):
            missing.extend(valid_model_reviews(item))
    if packet.get("action") == "visual_review":
        missing.extend(valid_model_reviews(record))
    if packet.get("exploration_contract"):
        missing.extend(valid_exploration(record, packet))
    return sorted(set(missing))


def valid_state_record(record):
    missing = []
    if record.get("open_world") is not True or record.get("exhaustive") is not False:
        missing.append("open state set")
    items = record.get("state_items")
    if not isinstance(items, list) or not items:
        return missing + ["state item"]
    needed = ["id", "scope", "context", "causes", "transitions",
              "model_reviews", "negative_reviews", "best_response",
              "alternatives", "evidence", "uncertainty"]
    for item in items:
        missing.extend(key for key in needed if not item.get(key))
    return missing


def valid_model_reviews(record):
    return (valid_review_groups(record, "model_reviews", "lenses") +
            valid_review_groups(record, "negative_reviews", "negative_checks"))


def valid_review_groups(record, record_key, checklist_key):
    missing = []
    reviews = record.get(record_key, {})
    for lens, checks in REVIEW_CHECKLIST[checklist_key].items():
        answers = reviews.get(lens, [])
        by_id = {answer.get("id"): answer for answer in answers
                 if isinstance(answer, dict)}
        expected = {item["id"] for item in checks}
        if len(answers) != len(checks) or set(by_id) != expected:
            missing.append(f"{lens} review checklist")
        for check in checks:
            answer = by_id.get(check["id"])
            if not answer:
                missing.append(f"{check['id']} model review")
                continue
            missing.extend(f"{check['id']} {key}" for key in ANSWER_FIELDS
                           if not answer.get(key))
            if answer.get("decision") not in REVIEW_DECISIONS:
                missing.append(f"{check['id']} decision")
    return missing


def valid_exploration(record, packet):
    missing = []
    options = record.get("options")
    if not isinstance(options, list) or len(options) < 4:
        return ["four design options", "model choice"]
    needed = packet["exploration_contract"]["required_option_fields"]
    for option in options:
        missing.extend(f"option {key}" for key in needed if not option.get(key))
    ids = [option.get("id") for option in options]
    if len(set(ids)) != len(ids):
        missing.append("unique option ids")
    chosen = record.get("chosen_direction")
    if not isinstance(chosen, dict) or not chosen.get("reason"):
        missing.append("model choice")
    elif not set(chosen.get("source_option_ids", [])) <= set(ids):
        missing.append("chosen source option ids")
    return missing


def record(args):
    out = Path(args.run_dir)
    try:
        result = load(args.result)
        packet = load(out / "packets" / f"{result.get('action', '')}.json")
        checklist = load(out / "review-checklist.json")
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: record input could not be read: {error}", file=sys.stderr)
        return 2
    if checklist != REVIEW_INDEX:
        print("blocked: missing canonical review checklist", file=sys.stderr)
        return 1
    missing = valid_record(result, packet)
    if missing:
        print("blocked: missing " + ", ".join(missing), file=sys.stderr)
        return 1
    dump(out / "records" / f"{result['action']}.json", result)
    print(json.dumps({"action": result["action"], "status": "RECORDED"},
                     sort_keys=True))
    return 0


def check(args):
    out = Path(args.run_dir)
    missing = [name for name in MODEL_ACTIONS
               if not (out / "records" / f"{name}.json").is_file()]
    state = "PASS" if not missing else "BLOCKED"
    print(json.dumps({"status": state, "missing_records": missing},
                     sort_keys=True))
    return 0 if not missing else 1


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
