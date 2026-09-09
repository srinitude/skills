"""Consume host-bound evidence for declared claims, separate from task accounting.

The host supplies trusted digests outside request data after verifying provenance.
This checks captured contents and current bindings. It cannot authenticate a human,
infer semantic sufficiency, or constrain a separately privileged host caller.
"""
import json
import time
from pathlib import Path

from skill_package import inventory, tree_digest
from source_coverage import bound_bytes, load_json, parse_json, require, validate


def document(path, expected, label):
    value = parse_json(bound_bytes(path, expected, label))
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def text(value, label):
    require(isinstance(value, str) and value.strip(), f"{label} needs nonempty text")
    return value


def same(left, right):
    return json.dumps(left, sort_keys=True, allow_nan=False) == json.dumps(right, sort_keys=True, allow_nan=False)


def subject_matches(root, context):
    from skill_scope import read_fields
    subject = context["subject"]
    require(isinstance(subject, dict), "subject must be an object")
    require(subject.get("skill") == root.name, "subject skill differs")
    text(subject.get("revision"), "subject revision")
    require(subject.get("sha256") == tree_digest(inventory(root)), "subject owned bytes changed")
    fields = read_fields(root)
    require(subject.get("scope") in {"user", "project"}, "invalid subject scope")
    require(subject["scope"] == fields.get("metadata", {}).get("scope"), "subject scope differs")
    audience = load_json(root / "assets/use-case-contract.json").get("audience", {})
    require(subject.get("audience") in {"human", "agent"}, "invalid subject audience")
    require(isinstance(audience, dict) and subject["audience"] == audience.get("primary"), "subject audience differs")


def context_requirements(context):
    source, coverage = context["source"], context["coverage"]
    require(isinstance(source, dict) and isinstance(coverage, dict), "source and coverage need bindings")
    validate(source["path"], coverage["path"], source["sha256"], coverage["sha256"])
    data = document(coverage["path"], coverage["sha256"], "coverage")
    obligations = {row["id"]: row for row in data["records"] if row["kind"] == "obligation"}
    requirements = context.get("requirements")
    require(isinstance(requirements, dict) and requirements, "required claims are missing")
    require(set(requirements) == set(obligations), "required claims must cover every source obligation")
    for identifier, rule in requirements.items():
        require(isinstance(rule, dict), "requirement rule must be an object")
        components = [item["id"] for item in obligations[identifier]["clauses"]]
        require(rule.get("components") == components, "required clause coverage differs")
        require(rule.get("applicability") in {"applicable", "inapplicable"}, "unresolved applicability")
        if rule["applicability"] == "inapplicable":
            condition = text(rule.get("source_condition"), "original source condition")
            require(condition in obligations[identifier]["quote"], "non-applicability lacks its source condition")
    return requirements


def context_bindings(context):
    require(type(context.get("version")) is int and context["version"] == 1, "unsupported acceptance context")
    validity = context["validity"]
    require(isinstance(validity, dict), "validity must be an object")
    start, end = validity.get("not_before"), validity.get("expires_at")
    require(type(start) is int and type(end) is int and start < end, "invalid acceptance validity")
    require(start <= time.time() < end, "acceptance context is expired or not yet valid")
    dependencies = context["dependencies"]
    require(isinstance(dependencies, dict) and dependencies, "dependency bindings are missing")
    for name, item in dependencies.items():
        require(isinstance(item, dict), f"dependency {name} needs a binding")
        bound_bytes(item["path"], item["sha256"], "dependency " + name)


def selected_value(data, path):
    require(isinstance(path, list) and path, "predicate needs a nonempty value path")
    for key in path:
        require(isinstance(key, str) or type(key) is int, "invalid predicate path item")
        if isinstance(data, dict):
            require(isinstance(key, str) and key in data, "predicate field missing")
        else:
            require(isinstance(data, list) and type(key) is int and 0 <= key < len(data), "predicate index missing")
        data = data[key]
    return data


def inspect_contents(data, rule):
    criteria = rule.get("criteria")
    require(isinstance(criteria, list) and criteria, "evidence criteria are missing")
    for criterion in criteria:
        require(isinstance(criterion, dict) and "equals" in criterion, "invalid evidence predicate")
        require(same(selected_value(data, criterion.get("path")), criterion["equals"]), "evidence predicate failed")
    judgment = data.get("judgment")
    require(isinstance(judgment, dict), "responsible judgment missing")
    for field in ["basis", "limits"]:
        text(judgment.get(field), "judgment " + field)
    producer = rule.get("producer")
    require(isinstance(producer, dict) and producer.get("kind") in {"mechanical", "model", "human"}, "invalid producer")
    text(producer.get("id"), "producer identity")
    require(same(data.get("producer"), producer), "evidence producer differs from the host-bound owner")
    if producer["kind"] == "mechanical":
        execution = data.get("execution")
        require(isinstance(execution, dict), "mechanical execution missing")
        require(isinstance(rule.get("command"), list) and rule["command"], "frozen command missing")
        require(all(isinstance(arg, str) for arg in rule["command"]), "command arguments must be strings")
        require(execution.get("argv") == rule["command"], "actual command arguments differ")
        require(type(execution.get("exit_code")) is int and type(rule.get("process_exit")) is int, "process exit must be an integer")
        require(execution["exit_code"] == rule["process_exit"], "process result differs")
        require(isinstance(execution.get("stdout"), str) and isinstance(execution.get("stderr"), str), "process output missing")


def inspect_claim(identifier, item, rule, context, context_sha):
    require(isinstance(item, dict), "claim needs an evidence artifact")
    relative = Path(text(item.get("path"), "evidence path"))
    require(not relative.is_absolute() and ".." not in relative.parts, "evidence must stay inside the host-approved root")
    data = document(Path(context["evidence_root"]) / relative, item["sha256"], "evidence artifact")
    require(data.get("context_sha256") == context_sha, "evidence context differs")
    require(data.get("requirement") == identifier, "evidence requirement differs")
    require(data.get("components") == rule["components"], "evidence clause coverage differs")
    expected_state = "passed" if rule["applicability"] == "applicable" else "inapplicable"
    require(data.get("state") == expected_state, "mandatory evidence is not accepted")
    text(data.get("run_id"), "execution identity")
    inspect_contents(data, rule)


def accept(root, receipt, context, context_sha):
    context_bindings(context)
    requirements = context_requirements(context)
    subject_matches(root, context)
    record = receipt.get("acceptance")
    require(isinstance(record, dict), "evidence acceptance record missing")
    require(record.get("context_sha256") == context_sha, "receipt context differs")
    require(same(record.get("subject"), context["subject"]), "receipt subject differs")
    require(receipt.get("operation") == text(context.get("operation"), "operation"), "operation differs")
    claims = record.get("claims")
    require(isinstance(claims, dict) and set(claims) == set(requirements), "receipt must cover every required claim")
    for identifier, rule in requirements.items():
        inspect_claim(identifier, claims[identifier], rule, context, context_sha)
    context_bindings(context)
    subject_matches(root, context)
    return {"requirements": len(requirements), "state": "passed",
            "limit": "Only these host-bound claims; task accounting and structure are separate."}


def check(root, receipt_path, receipt, args):
    values = [args.acceptance_context, args.context_sha256, args.receipt_sha256]
    if not any(values):
        require("acceptance" not in receipt, "acceptance requires host-supplied trust bindings")
        return None
    require(all(values), "acceptance requires all three host-supplied bindings")
    context = document(args.acceptance_context, args.context_sha256, "acceptance context")
    pinned = document(receipt_path, args.receipt_sha256, "invocation receipt")
    require(same(pinned, receipt), "receipt changed during validation")
    return accept(root, pinned, context, args.context_sha256)


def guard(root, target, expected, bindings):
    require(isinstance(bindings, dict), "host-bound acceptance is required before promotion")
    require(all(bindings.get(key) for key in ("context", "context_sha256", "receipt", "receipt_sha256")),
            "all external acceptance bindings are required")
    context = document(bindings["context"], bindings["context_sha256"], "acceptance context")
    receipt = document(bindings["receipt"], bindings["receipt_sha256"], "invocation receipt")
    require(same(context.get("consumer"), {**expected, "target": str(target.resolve())}),
            "acceptance consumer, destination or operation inputs differ")
    return accept(root, receipt, context, bindings["context_sha256"])


def arguments(parser):
    parser.add_argument("--acceptance-context", help="host-reviewed context outside the candidate")
    parser.add_argument("--context-sha256", help="context digest supplied by the trusted host")
    parser.add_argument("--receipt", help="actual evidence receipt outside the candidate")
    parser.add_argument("--receipt-sha256", help="receipt digest supplied by the trusted host")


def bindings(args):
    return {"context": args.acceptance_context, "context_sha256": args.context_sha256,
            "receipt": args.receipt, "receipt_sha256": args.receipt_sha256}
