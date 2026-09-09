#!/usr/bin/env python3
"""Validate source-backed domain research coverage and receipts.

Usage:
  python3 scripts/check_domain_research.py [skill-root]

Exit codes:
  0  research receipts pass
  1  research is missing, stale, narrow, or invalid
  2  bad usage

Example:
  python3 scripts/check_domain_research.py .
"""
import argparse
import datetime
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

DIMENSIONS = {"actors", "objects", "actions", "states", "invariants",
              "variants", "interfaces", "authorities", "failures",
              "recoveries", "evidence", "time", "resources", "quality",
              "terminology", "exclusions"}
RECEIPT_FIELDS = {"source", "source_class", "claim", "disposition",
                  "checked_at", "limitations", "dimensions"}
DISCONFIRM_FIELDS = {"question", "source", "checked_at", "result",
                     "disposition"}
SOURCE_CLASSES = {"first_party", "standard", "research", "practitioner",
                  "live_owner"}
DISPOSITIONS = {"retained", "adapted", "bounded", "rejected"}
SENTINEL = "SCAFFOLD-" + "PLACEHOLDER"
MAX_RECEIPT_AGE = datetime.timedelta(days=31)
FUTURE_TOLERANCE = datetime.timedelta(minutes=5)


def load(root):
    path = root / "assets" / "use-case-contract.json"
    if not path.is_file():
        raise ValueError(f"missing {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON: {error}") from error


def valid_time(value):
    try:
        parsed = datetime.datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return False
    return parsed.tzinfo is not None


def current_time_problem(value, label, now):
    try:
        parsed = datetime.datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        return None
    checked = parsed.astimezone(datetime.timezone.utc)
    if checked > now + FUTURE_TOLERANCE:
        return f"{label}.checked_at is in the future"
    if now - checked > MAX_RECEIPT_AGE:
        return f"{label}.checked_at is not current"
    return None


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def web_url(value):
    parsed = urlparse(value) if isinstance(value, str) else None
    return bool(parsed and parsed.scheme in {"http", "https"} and parsed.netloc)


def receipt_item_problems(index, item, now):
    label, found = f"research_receipts.{index}", []
    if not isinstance(item, dict) or not RECEIPT_FIELDS <= set(item):
        return [f"{label} is incomplete"]
    if not web_url(item["source"]):
        found.append(f"{label}.source must be a web URL")
    dimensions = item["dimensions"]
    valid_dimensions = (isinstance(dimensions, list) and dimensions
                        and all(isinstance(value, str) for value in dimensions))
    if not valid_dimensions or not set(dimensions) <= DIMENSIONS:
        found.append(f"{label}.dimensions are invalid")
    if item["source_class"] not in SOURCE_CLASSES:
        found.append(f"{label}.source_class is invalid")
    for field in ["claim", "limitations"]:
        if not nonempty(item[field]):
            found.append(f"{label}.{field} is empty")
    if item["disposition"] not in DISPOSITIONS:
        found.append(f"{label}.disposition is invalid")
    if not valid_time(item["checked_at"]):
        found.append(f"{label}.checked_at needs a timezone")
    else:
        problem = current_time_problem(item["checked_at"], label, now)
        if problem:
            found.append(problem)
    return found


def receipt_problems(receipts, now):
    found, hosts, sources, classes, covered = [], set(), set(), set(), set()
    for index, item in enumerate(receipts):
        found.extend(receipt_item_problems(index, item, now))
        if not isinstance(item, dict) or not RECEIPT_FIELDS <= set(item):
            continue
        source = item["source"]
        parsed = urlparse(source) if isinstance(source, str) else urlparse("")
        hosts.add(parsed.netloc)
        sources.add(source)
        classes.add(item["source_class"])
        dimensions = item["dimensions"]
        valid = (isinstance(dimensions, list)
                 and all(isinstance(value, str) for value in dimensions))
        if valid and set(dimensions) <= DIMENSIONS:
            covered.update(dimensions)
    if len(sources) < 4:
        found.append("research_receipts need four distinct web sources")
    if len(hosts) < 2:
        found.append("research_receipts need at least two web hosts")
    if len(classes) < 2:
        found.append("research_receipts need at least two source classes")
    if not DIMENSIONS <= covered:
        found.append("research_receipts dimension coverage is incomplete")
    return found


def question_problems(data, now):
    found = []
    questions = data.get("research_questions", {})
    if not isinstance(questions, dict) or not DIMENSIONS <= set(questions):
        found.append("research_questions must cover every domain dimension")
    evidence = data.get("disconfirmation", [])
    if not isinstance(evidence, list) or not evidence:
        found.append("disconfirmation needs at least one current search")
        return found
    for index, item in enumerate(evidence):
        if not isinstance(item, dict) or not DISCONFIRM_FIELDS <= set(item):
            found.append(f"disconfirmation.{index} is incomplete")
            continue
        if not web_url(item["source"]):
            found.append(f"disconfirmation.{index}.source must be a web URL")
        for field in ["question", "result", "disposition"]:
            if not nonempty(item[field]):
                found.append(f"disconfirmation.{index}.{field} is empty")
        if not valid_time(item["checked_at"]):
            found.append(f"disconfirmation.{index}.checked_at needs a timezone")
        else:
            problem = current_time_problem(
                item["checked_at"], f"disconfirmation.{index}", now)
            if problem:
                found.append(problem)
    return found


def problems(data):
    found = []
    now = datetime.datetime.now(datetime.timezone.utc)
    if SENTINEL in json.dumps(data):
        found.append("scaffold placeholder remains in domain research")
    receipts = data.get("research_receipts", [])
    if not isinstance(receipts, list):
        found.append("research_receipts must be an array")
        receipts = []
    found.extend(receipt_problems(receipts, now))
    found.extend(question_problems(data, now))
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill_root", nargs="?", default=".")
    args = parser.parse_args(argv)
    try:
        data = load(Path(args.skill_root).resolve())
    except ValueError as error:
        print(f"FAIL {error}")
        return 1
    found = problems(data)
    for problem in found:
        print(f"FAIL {problem}")
    print(f"domain research: {len(found)} problems")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
