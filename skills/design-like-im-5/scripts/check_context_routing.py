#!/usr/bin/env python3
"""Check context routes and build action context bundles.

Exit codes:
  0  every route passed
  1  one or more routes failed
  2  route data could not be read

Example:
  python3 scripts/check_context_routing.py .
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

SUPPORT_CLASSES = {"references", "scripts", "assets", "examples", "evals"}
FORBIDDEN_ROUTE_FIELDS = {"decision", "rank", "score", "chosen_direction"}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def routing_path(root):
    return Path(root) / "assets" / "context-routing.json"


def routing_digest(root):
    return hashlib.sha256(routing_path(root).read_bytes()).hexdigest()


def support_paths(route):
    return sorted({row["path"] for rows in route["support"].values()
                   for row in rows})


def build_context_bundle(root, action):
    root = Path(root)
    routes = [row for row in load(routing_path(root))["routes"]
              if row.get("action") == action]
    if len(routes) != 1:
        raise ValueError(f"action needs one context route: {action}")
    route = routes[0]
    return {
        "route_id": route["id"],
        "route_sha256": routing_digest(root),
        "load_when": route["load_when"],
        "support": route["support"],
        "required_paths": support_paths(route),
        "produce": route["produce"],
        "do_not_substitute": route["do_not_substitute"],
    }


def record_context_issues(record, bundle):
    acknowledgements = record.get("context_acknowledgements")
    if not isinstance(acknowledgements, list):
        return ["context acknowledgement"]
    missing_context = record.get("missing_context")
    if not isinstance(missing_context, list):
        return ["missing context list"]
    if not all(isinstance(path, str) and path for path in
               acknowledgements + missing_context):
        return ["valid context path"]
    required = set(bundle.get("required_paths", []))
    used = set(acknowledgements)
    missing = set(missing_context)
    accounted = used | missing
    issues = [f"context acknowledgement for {path}"
              for path in sorted(required - accounted)]
    issues.extend(f"unrouted context path {path}"
                  for path in sorted(accounted - required))
    issues.extend(f"context path both used and missing {path}"
                  for path in sorted(used & missing))
    if len(used) != len(acknowledgements):
        issues.append("duplicate context acknowledgement")
    if len(missing) != len(missing_context):
        issues.append("duplicate missing context path")
    if missing_context and record.get("decision") != "BLOCKED":
        issues.append("BLOCKED decision for missing context")
    return issues


def route_shape_issues(root, route):
    route_id = route.get("id", "missing route id")
    needed = ["id", "action", "source_text", "meaning", "strength",
              "judgment_owner", "load_when", "support", "produce",
              "do_not_substitute"]
    issues = [f"{route_id}: missing {key}" for key in needed
              if not route.get(key)]
    if set(route.get("support", {})) != SUPPORT_CLASSES:
        issues.append(f"{route_id}: needs all five support classes")
    if route.get("judgment_owner") != "model":
        issues.append(f"{route_id}: model must own design judgment")
    if FORBIDDEN_ROUTE_FIELDS & set(route):
        issues.append(f"{route_id}: route claims a design verdict")
    return issues + support_issues(root, route)


def support_issues(root, route):
    issues = []
    for kind, rows in route.get("support", {}).items():
        if not rows:
            issues.append(f"{route.get('id')}: empty {kind}")
        for row in rows:
            path = row.get("path", "")
            if not path or not (root / path).is_file():
                issues.append(f"{route.get('id')}: missing path {path}")
            if not row.get("contribution"):
                issues.append(f"{route.get('id')}: {path} needs contribution")
    return issues


def body_issues(root, routes):
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    issues = []
    for route in routes:
        token = f"[{route.get('id')}]"
        if text.count(token) != 1:
            issues.append(f"{route.get('id')}: body anchor count is not one")
    return issues


def workflow_issues(root, routes):
    actions = [row["action"] for row in load(root / "assets/workflow.json")["steps"]]
    route_actions = [row.get("action") for row in routes]
    issues = []
    for action in actions:
        if route_actions.count(action) != 1:
            issues.append(f"{action}: needs one context route")
    return issues


def context_case_issues(root, routes):
    cases = load(root / "evals" / "context-cases.json").get("cases", [])
    actions = [row.get("action") for row in cases]
    ids = [row.get("id") for row in cases]
    issues = []
    for action in [row.get("action") for row in routes]:
        if actions.count(action) != 1:
            issues.append(f"{action}: needs one context eval case")
    if len(ids) != len(set(ids)):
        issues.append("context eval ids must be unique")
    for case in cases:
        for key in ["id", "action", "risk", "expected"]:
            if not case.get(key):
                issues.append(f"context eval needs {key}")
    return issues


def check(root):
    doc = load(routing_path(root))
    routes = doc.get("routes", [])
    ids = [row.get("id") for row in routes]
    issues = []
    if set(doc.get("support_classes", [])) != SUPPORT_CLASSES:
        issues.append("support_classes must name all five classes")
    if len(ids) != len(set(ids)):
        issues.append("context route ids must be unique")
    for route in routes:
        issues.extend(route_shape_issues(root, route))
    return (issues + body_issues(root, routes) + workflow_issues(root, routes) +
            context_case_issues(root, routes))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", nargs="?", default=".")
    args = parser.parse_args(argv)
    root = Path(args.skill_dir).resolve()
    try:
        issues = check(root)
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"error: context routes could not be read: {error}", file=sys.stderr)
        return 2
    for issue in issues:
        print(issue)
    print(f"context route check: {len(issues)} problems")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
