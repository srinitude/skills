#!/usr/bin/env python3
"""Select fixed rules after a state judgment is recorded.

The task checks order and rule fields. It does not make a design judgment.

Exit codes:
  0  rules were selected
  1  state judgment is not recorded
  2  run data could not be read
"""
import argparse
import json
import sys
from pathlib import Path


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path, data):
    text = json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n"
    path.write_text(text, encoding="utf-8")


def pick_rules(contract, data):
    return [rule["id"] for rule in contract["rules"]
            if rule.get("always") or
            data.get(rule.get("field")) in rule.get("values", [])]


def base_rules(contract):
    return [rule["id"] for rule in contract["rules"] if rule.get("always")]


def select(run_dir):
    out = Path(run_dir)
    try:
        run = load(out / "run.json")
    except (OSError, json.JSONDecodeError) as error:
        print(f"error: run could not be read: {error}", file=sys.stderr)
        return 2
    if not (out / "records" / "state_judgment.json").is_file():
        print("blocked: state_judgment must be recorded first", file=sys.stderr)
        return 1
    if run.get("next") != "select_rules":
        print(f"blocked: next action is {run.get('next')}, not select_rules",
              file=sys.stderr)
        return 1
    root = Path(__file__).resolve().parents[1]
    run["rules"] = pick_rules(
        load(root / "assets" / "simplicity-contract.json"), run["intake"])
    run["rules_selected"] = True
    run["next"] = "atom_judgment"
    dump(out / "run.json", run)
    print(json.dumps({"action": "select_rules", "status": "RECORDED"},
                     sort_keys=True))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    args = parser.parse_args(argv)
    return select(args.run_dir)


if __name__ == "__main__":
    raise SystemExit(main())
