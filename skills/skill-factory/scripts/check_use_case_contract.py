#!/usr/bin/env python3
"""Reject generic skill primitives without a domain role and proof.

Usage:
  python3 scripts/check_use_case_contract.py [skill-root]

Exit codes:
  0  the use-case contract passes
  1  the contract is missing, generic, or invalid
  2  bad usage

Example:
  python3 scripts/check_use_case_contract.py .
"""
import argparse
import json
import sys
from pathlib import Path

from domain_text import uses_generic_task_template, uses_term, words

KINDS = {"skill_body", "references", "assets", "scripts", "tests",
         "mise_tasks", "examples", "evals", "policies", "schemas",
         "records"}
DIMENSIONS = {"actors", "objects", "actions", "states", "invariants",
              "variants", "interfaces", "authorities", "failures",
              "recoveries", "evidence", "time", "resources", "quality",
              "terminology", "exclusions"}
ROLE_FIELDS = {"ownership", "role", "outcome", "motivation", "value",
               "failure_prevented", "proof"}
OWNERSHIP = {"domain_specific", "shared_invariant"}
SENTINEL = "SCAFFOLD-" + "PLACEHOLDER"


def load(root):
    path = root / "assets" / "use-case-contract.json"
    if not path.is_file():
        raise ValueError(f"missing {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON: {error}") from error


def text_uses_term(text, terms):
    return uses_term(text, terms)


def append_text_problem(found, label, text, terms):
    if not text_uses_term(text, terms):
        found.append(f"{label} needs a package domain term")
    elif uses_generic_task_template(text):
        found.append(f"{label} uses generic scaffold language")


def term_problems(terms):
    found, normalized = [], []
    for index, term in enumerate(terms):
        tokens = words(term)
        phrase = " ".join(tokens)
        if len(phrase.replace(" ", "")) < 3 or max(map(len, tokens), default=0) < 2:
            found.append(f"domain_terms.{index} must be a specific phrase")
        normalized.append(phrase)
    if len(normalized) != len(set(normalized)):
        found.append("domain_terms must be unique after normalization")
    return found


def check_motivations(data, found):
    motivations = data.get("motivations", [])
    if not isinstance(motivations, list) or len(motivations) < 2:
        found.append("motivations must hold at least two use-case reasons")
        return
    fields = {"constraint", "reason", "failure_prevented"}
    for index, item in enumerate(motivations):
        if not isinstance(item, dict) or not fields <= set(item):
            found.append(f"motivations.{index} needs constraint, reason, and failure_prevented")
            continue
        for field in sorted(fields):
            append_text_problem(found, f"motivations.{index}.{field}",
                                item[field], data.get("domain_terms", []))


def check_domain(data, found):
    terms = data.get("domain_terms", [])
    if not isinstance(terms, list) or len(terms) < 3:
        found.append("domain_terms must hold at least three specific terms")
        terms = []
    else:
        found.extend(term_problems(terms))
    for key in ["outcome", "domain_failures", "domain_evidence"]:
        value = data.get(key)
        if not value or key != "outcome" and len(value) < 2:
            found.append(f"{key} must state package-specific content")
    if terms and not text_uses_term(data.get("outcome", ""), terms):
        found.append("outcome must use a package domain term")
    for key in ["domain_failures", "domain_evidence"]:
        for index, item in enumerate(data.get(key, [])):
            append_text_problem(found, f"{key}.{index}", item, terms)
    return terms


def check_dimensions(data, terms, found):
    dimensions = data.get("domain_dimensions", {})
    if not isinstance(dimensions, dict):
        found.append("domain_dimensions must be an object")
        return
    for name in sorted(DIMENSIONS):
        values = dimensions.get(name, [])
        if not isinstance(values, list) or not values:
            found.append(f"domain_dimensions.{name} needs package-specific content")
            continue
        for item in values:
            append_text_problem(found, f"domain_dimensions.{name}", item, terms)


def check_roles(data, terms, found):
    roles = data.get("primitive_roles", {})
    if not isinstance(roles, dict):
        found.append("primitive_roles must be an object")
        return
    for kind in sorted(KINDS):
        item = roles.get(kind)
        if not isinstance(item, dict) or not ROLE_FIELDS <= set(item):
            found.append(f"primitive_roles.{kind} needs every primitive field")
            continue
        if item["ownership"] not in OWNERSHIP:
            found.append(f"primitive_roles.{kind}.ownership is invalid")
        for field in ["role", "outcome", "motivation", "value",
                      "failure_prevented", "proof"]:
            append_text_problem(found, f"primitive_roles.{kind}.{field}",
                                item[field], terms)


def problems(data, root):
    found = []
    if data.get("skill") != root.name:
        found.append(f"skill must equal directory name {root.name}")
    if SENTINEL in json.dumps(data):
        found.append("scaffold placeholder remains in use-case contract")
    check_motivations(data, found)
    terms = check_domain(data, found)
    check_dimensions(data, terms, found)
    check_roles(data, terms, found)
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill_root", nargs="?", default=".")
    args = parser.parse_args(argv)
    root = Path(args.skill_root).resolve()
    try:
        data = load(root)
    except ValueError as error:
        print(f"FAIL {error}")
        return 1
    found = problems(data, root)
    for problem in found:
        print(f"FAIL {problem}")
    print(f"use-case contract: {len(found)} problems")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
