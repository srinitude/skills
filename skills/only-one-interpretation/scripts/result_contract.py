#!/usr/bin/env python3
"""Provide pure checks used by validate_result.py.

Exit codes:
  0  module information displayed
  2  usage error

Example:
  python3 scripts/result_contract.py --help
"""
import argparse
import re

LEDGER_FIELDS = {
    "objective", "actors", "objects", "references", "inputs", "outputs",
    "definitions", "authority", "permissions", "scope", "priorities",
    "fixed_methods", "candidate_methods", "quantities", "units", "dates",
    "time_zones", "ordering", "side_effects", "error_handling",
    "acceptance_evidence", "forbidden_results",
}
AMBIGUITY_CLASSES = {
    "lexical", "syntactic", "referential", "attachment", "scope",
    "quantifier", "modality", "temporal", "unit", "actor", "authority",
    "method-versus-outcome", "side-effect", "output-format",
    "success-criteria", "contradiction", "missing-context", "priority",
}
LEVELS = {"required", "prohibited", "optional", "context"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def check_ledger(value, label, problems):
    if not isinstance(value, dict):
        problems.append(f"{label} must be an object")
        return
    missing = sorted(LEDGER_FIELDS - set(value))
    extra = sorted(set(value) - LEDGER_FIELDS)
    if missing:
        problems.append(f"{label} is missing fields: {', '.join(missing)}")
    if extra:
        problems.append(f"{label} has unknown fields: {', '.join(extra)}")


def check_metadata(record, problems):
    if record.get("schema_version") != 1:
        problems.append("schema_version must be 1")
    for name in ["case_id", "source_prompt", "visible_reply"]:
        if not nonempty(record.get(name)):
            problems.append(f"{name} must be a non-empty string")
    if record.get("execution_attempted") is not False:
        problems.append("execution attempted must be false")
    if record.get("external_transmission") is not False:
        problems.append("external transmission must be false")
    check_ledger(record.get("intended_ledger"), "intended_ledger", problems)


def check_finding(finding, index, seen, problems):
    label = f"ambiguity {index}"
    if not isinstance(finding, dict):
        problems.append(f"{label} must be an object")
        return
    finding_id = finding.get("id")
    if not nonempty(finding_id) or finding_id in seen:
        problems.append(f"{label} needs a unique id")
    seen.add(finding_id)
    if finding.get("class") not in AMBIGUITY_CLASSES:
        problems.append(f"{label} has an unknown class")
    if finding.get("material") is not True:
        problems.append(f"{label} must be material or be omitted")
    if finding.get("status") not in {"resolved", "unresolved"}:
        problems.append(f"{label} status must be resolved or unresolved")
    if finding.get("status") == "resolved" and not nonempty(finding.get("resolved_by")):
        problems.append(f"{label} needs source-backed resolved_by")


def check_ambiguities(record, problems):
    ambiguities = record.get("ambiguities")
    if not isinstance(ambiguities, list):
        problems.append("ambiguities must be a list")
        return []
    seen = set()
    for index, finding in enumerate(ambiguities, 1):
        check_finding(finding, index, seen, problems)
    return ambiguities


def clause_sets(record, problems):
    sources = record.get("source_requirements")
    clauses = record.get("rewrite_clauses")
    if not isinstance(sources, list) or not sources:
        problems.append("READY needs source_requirements")
        return set(), set()
    if not isinstance(clauses, list) or not clauses:
        problems.append("READY needs rewrite_clauses")
        return set(), set()
    return {item.get("id") for item in sources}, clauses


def check_trace(record, problems):
    source_ids, clauses = clause_sets(record, problems)
    clause_ids, mapped = set(), set()
    for clause in clauses:
        if not isinstance(clause, dict):
            problems.append("rewrite clause must be an object")
            continue
        clause_id, links = clause.get("id"), clause.get("source_ids")
        clause_ids.add(clause_id)
        if clause.get("level") not in LEVELS:
            problems.append(f"rewrite clause {clause_id} has an invalid level")
        if not isinstance(links, list) or not links:
            problems.append(f"rewrite clause {clause_id} has no source authority")
            continue
        if set(links) - source_ids:
            problems.append(f"rewrite clause {clause_id} invents source authority")
        mapped.update(links)
    if mapped != source_ids:
        problems.append("constraint trace does not map every source requirement")
    return clause_ids


def check_attacks(record, ambiguities, clause_ids, problems):
    attacks = record.get("alternate_readings")
    if not isinstance(attacks, list):
        problems.append("alternate_readings must be a list")
        return
    attacked = {item.get("ambiguity_id") for item in attacks if isinstance(item, dict)}
    for finding in ambiguities:
        if finding.get("id") not in attacked:
            problems.append(f"alternate reading attack missing for {finding.get('id')}")
    for attack in attacks:
        clause = attack.get("ruling_clause_id") if isinstance(attack, dict) else None
        if clause not in clause_ids:
            problems.append("alternate reading has no ruling rewrite clause")


def check_methods(record, problems):
    levels = {item.get("id"): item.get("level") for item in record["rewrite_clauses"]}
    for method in record.get("method_classification", []):
        clause_id = method.get("rewrite_clause_id")
        if method.get("kind") == "fixed" and levels.get(clause_id) != "required":
            problems.append("fixed method is not retained as required")
        if method.get("kind") == "candidate" and clause_id is not None:
            problems.append("candidate method was promoted into the rewrite")


def check_secrets(record, problems):
    reply = record.get("visible_reply", "")
    for entry in record.get("secret_replacements", []):
        value = entry.get("value") if isinstance(entry, dict) else None
        placeholder = entry.get("placeholder") if isinstance(entry, dict) else None
        if nonempty(value) and value in reply:
            problems.append("visible reply repeats a secret value")
        if not nonempty(placeholder) or placeholder not in reply:
            problems.append("secret replacement placeholder is missing")


def check_ready(record, ambiguities, problems):
    reply = record.get("visible_reply", "")
    if not re.fullmatch(r"```\n[^`]+\n```", reply, flags=re.DOTALL):
        problems.append("READY visible reply must be exactly one fenced block")
    if any(item.get("status") == "unresolved" for item in ambiguities):
        problems.append("READY has an unresolved material ambiguity")
    check_ledger(record.get("rewrite_ledger"), "rewrite_ledger", problems)
    if record.get("rewrite_ledger") != record.get("intended_ledger"):
        problems.append("semantic round trip differs from the intended ledger")
    clause_ids = check_trace(record, problems)
    check_attacks(record, ambiguities, clause_ids, problems)
    check_methods(record, problems)
    check_secrets(record, problems)


def question_coverage(questions, problems):
    if not isinstance(questions, list) or not questions:
        problems.append("NEEDS_CLARIFICATION needs questions")
        return set()
    covered = set()
    for question in questions:
        if not isinstance(question, dict) or not nonempty(question.get("text")):
            problems.append("each clarification question needs text")
        else:
            covered.update(question.get("finding_ids", []))
    return covered


def check_clarification(record, ambiguities, problems):
    reply = record.get("visible_reply", "")
    if not reply.startswith("NEEDS_CLARIFICATION\n") or "```" in reply:
        problems.append("clarification must be one unfenced NEEDS_CLARIFICATION turn")
    unresolved = {item.get("id") for item in ambiguities if item.get("status") == "unresolved"}
    if not unresolved:
        problems.append("NEEDS_CLARIFICATION needs an unresolved material ambiguity")
    if question_coverage(record.get("questions"), problems) != unresolved:
        problems.append("clarification does not cover every gating unknown exactly")
    forbidden = {"rewrite_ledger", "source_requirements", "rewrite_clauses",
                 "alternate_readings", "method_classification", "secret_replacements"}
    if forbidden & set(record):
        problems.append("clarification must stop without rewrite artifacts")


def validate(record):
    problems = []
    if not isinstance(record, dict):
        return ["root must be an object"]
    check_metadata(record, problems)
    ambiguities = check_ambiguities(record, problems)
    if record.get("status") == "READY":
        check_ready(record, ambiguities, problems)
    elif record.get("status") == "NEEDS_CLARIFICATION":
        check_clarification(record, ambiguities, problems)
    else:
        problems.append("status must be READY or NEEDS_CLARIFICATION")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
