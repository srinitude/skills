"""Build factory policy assets for one registry skill."""
import datetime
import tomllib
from standardization_seed import json_bytes

from agentic_request_contract import read_json
from agentic_context import audience_record, declaration_order
from standardization_rewrites import safe_target
from standardization_profile import DIMENSIONS, PHASES, PRIMITIVES
from check_decision_records import problems as decision_problems
from check_primitive_lifecycle import validate as lifecycle_problems
from check_mise_primitives import configured_fields, validate as primitive_problems


def existing_asset(root, name):
    path = root / "assets" / name
    if not path.exists() and not path.is_symlink():
        return None
    data = read_json(safe_target(root, "assets/" + name).read_bytes().decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"existing {name} must be an object")
    return data


def existing_use_case(root):
    return existing_asset(root, "use-case-contract.json")


def validate_policy_assets(root):
    for name in ["primitive-lifecycle.json", "decision-records.json",
                 "invocation-receipt-template.json", "mise-primitives.json"]:
        record = existing_asset(root, name)
        if record is None or record.get("skill") != root.name:
            raise ValueError(f"existing {name} must name the current skill")
    contract = existing_use_case(root)
    decisions = existing_asset(root, "decision-records.json")
    try:
        found = decision_problems(decisions, contract.get("domain_terms", []), root.name)
        found += lifecycle_problems(root) + primitive_problems(root)
    except (AttributeError, KeyError, TypeError) as error:
        raise ValueError(f"policy record shape needs explicit reconciliation: {error}") from error
    if found:
        raise ValueError("policy records need explicit reconciliation: " + "; ".join(found))


def resolved_initial_profile(root, profile):
    """Preserve existing declarations; supplied changes need prior adaptation."""
    previous = existing_use_case(root) or {}
    resolved = dict(profile)
    for field in ["audience", "initial_context"]:
        if field in previous:
            if field in profile and profile[field] != previous[field]:
                raise ValueError(f"{field} conflicts with the existing use-case; reconcile its adaptation first")
            resolved[field] = previous[field]
    audience_record(resolved, accept=True)
    declaration_order(resolved.get("initial_context"))
    return resolved


def motivations(profile):
    term = profile["primary_term"]
    return [
        {"constraint": f"Preserve the accepted {term} behavior.",
         "reason": f"The {term} outcome depends on stable domain semantics.",
         "failure_prevented": f"A {term} update that changes user-visible meaning."},
        {"constraint": f"Route repeatable {term} checks through Mise.",
         "reason": f"The {term} judgment needs fresh deterministic evidence.",
         "failure_prevented": f"A {term} claim backed only by prose or intent."},
    ]


def research(profile, stamp):
    records = []
    for source in profile["sources"]:
        item = dict(source)
        item.update({"disposition": source.get("disposition", "bounded"),
                     "checked_at": stamp, "dimensions": DIMENSIONS})
        records.append(item)
    return records


def primitive_roles(profile):
    term = profile["primary_term"]
    return {name: {
        "ownership": "domain_specific", "role": f"Own {term} {name} behavior.",
        "outcome": f"Keep {term} {name} aligned with the accepted result.",
        "motivation": f"The {term} package needs one {name} owner.",
        "value": f"Expose current {term} {name} progress.",
        "failure_prevented": f"Stale or generic {term} {name} behavior.",
        "proof": f"Fresh {term} {name} validation and behavioral evidence.",
    } for name in PRIMITIVES}


def task_records(profile, tasks):
    term = profile["primary_term"]
    return {name: {
        "outcome": f"Advance the {term} result through {name}.",
        "motivation": f"The {term} package needs the {name} gate.",
        "value": f"Produce current {term} evidence from {name}.",
        "proof": f"The {term} {name} task exits zero with readable output.",
        "applicability": f"Use {name} for its declared {term} responsibility.",
    } for name in tasks}


def operations(profile, tasks):
    candidates = [profile["main_task"], "invocation-policy", "agentic-request",
                  "improvement-policy", "mise-primitives-update", "ledger"]
    candidates += profile.get("public_tasks", [])
    candidates = list(dict.fromkeys(candidates))
    term = profile["primary_term"]
    return [{"task": name, "outcome": f"Produce the named {term} {name} result.",
             "motivation": f"The {term} workflow needs one {name} entry.",
             "why_default_path": f"This is the single declared {term} {name} route.",
             "proof": f"Fresh {term} {name} output and exit status."}
            for name in candidates if name in tasks]


def use_case(profile, tasks, stamp=None):
    stamp = stamp or datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    term = profile["primary_term"]
    dimensions = {name: [f"The {term} contract owns {name} decisions."]
                  for name in DIMENSIONS}
    questions = {name: f"What can change the {term} {name} decision?"
                 for name in DIMENSIONS}
    return {"version": "1.0.0", "skill": profile["skill"],
            "outcome": profile["outcome"], "motivations": motivations(profile),
            "audience": profile["audience"], "initial_context": profile["initial_context"],
            "domain_terms": profile["domain_terms"],
            "domain_failures": [f"The {term} result changes without proof.",
                                f"The {term} package reports a false pass."],
            "domain_evidence": [f"Fresh {term} task output and saved receipts.",
                                f"Current {term} behavior and counterexample checks."],
            "domain_dimensions": dimensions, "research_questions": questions,
            "research_receipts": research(profile, stamp),
            "disconfirmation": [{"question": f"Can structure alone prove the {term} result?",
                "source": profile["sources"][0]["source"], "checked_at": stamp,
                "result": f"No. The {term} behavior still needs direct evaluation.",
                "disposition": f"Keep structure and {term} behavior as separate gates."}],
            "task_graph": {"ci_task": "ci", "public_operations": operations(profile, tasks),
                           "tasks": task_records(profile, tasks)},
            "primitive_roles": primitive_roles(profile)}


def lifecycle(profile):
    term = profile["primary_term"]
    main = profile["main_task"]
    values = [main, "domain-research-policy", "improvement-policy", "decision-policy",
              main, "validate", main, "ci", "ci", "improvement-policy",
              "decision-policy", "decision-policy"]
    profile_name = f"{profile['skill']}-lifecycle"
    aspects = {name: {"profile": profile_name,
        "outcome": f"Keep {term} {name} aligned.",
        "motivation": f"The {term} result depends on {name} ownership.",
        "proof": f"Fresh {term} {name} evidence."} for name in DIMENSIONS}
    return {"version": "1.0.0", "skill": profile["skill"],
            "required_phases": PHASES, "profiles": {profile_name: dict(zip(PHASES, values))},
            "aspects": aspects,
            "primitives": {name: {"profile": profile_name} for name in PRIMITIVES}}


def decisions(profile):
    term = profile["primary_term"]
    specs = [("deterministic-gates", "deterministic", "mise"),
             ("semantic-judgment", "model_owned", "model"),
             ("side-effect-authority", "human_owned", "human")]
    records = []
    for identifier, kind, owner in specs:
        records.append({"id": identifier, "kind": kind,
            "outcome": f"Protect the accepted {term} result.",
            "motivation": f"The {term} decision needs its correct owner.",
            "why_this_path": f"The {term} responsibility belongs to {owner}.",
            "owner": owner, "inputs": [f"current {term} contract"],
            "expected_effect": f"Make the {term} decision testable.",
            "proof": f"Fresh {term} evidence from the named owner.",
            "falsifier": f"Current {term} evidence contradicts the decision.",
            "failure_branch": f"Block the {term} result and restore the accepted state."})
    return {"version": "1.0.0", "skill": profile["skill"], "records": records}


def invocation(profile):
    return {"version": "1.0.0", "skill": profile["skill"],
            "operation": f"Name the current {profile['primary_term']} operation.",
            "entries": [], "entry_rule": "Account for every declared Mise task.",
            "proof_rule": f"Tie each entry to fresh {profile['primary_term']} evidence."}


def primitive_decisions(actual, profile, catalog):
    term, groups = profile["primary_term"], {}
    for name, available in catalog["groups"].items():
        groups[name] = {"used": sorted(actual[name]),
            "not_applicable": sorted(set(available) - actual[name]),
            "used_reason": f"The {term} graph uses these {name} primitives.",
            "nonuse_reason": f"Other {term} {name} primitives add no proved value.",
            "creative_use": f"The {term} graph uses {name} primitives on one proof path.",
            "evidence": f"Current {term} Mise configuration and task output."}
    return {"version": "1.0.0", "skill": profile["skill"],
            "catalog_version": catalog["version"], "groups": groups}


def asset_files(files, profile, tasks, stamp):
    path = 'assets/use-case-contract.json'
    previous = read_json(files[path].decode('utf-8')) if path in files else None
    if previous is not None and not isinstance(previous, dict):
        raise ValueError('existing use-case-contract.json must be an object')
    current = dict(previous) if previous is not None else use_case(profile, tasks, stamp)
    current.update({field: profile[field] for field in ['audience', 'initial_context']})
    if current != previous:
        files[path] = json_bytes(current)
    catalog = read_json(files['assets/mise-primitives-catalog.json'].decode('utf-8'))
    config = tomllib.loads(files['mise.toml'].decode('utf-8'))
    for name, seed in [
        ('primitive-lifecycle.json', lambda: lifecycle(profile)),
        ('decision-records.json', lambda: decisions(profile)),
        ('invocation-receipt-template.json', lambda: invocation(profile)),
        ('mise-primitives.json', lambda: primitive_decisions(configured_fields(config, catalog), profile, catalog)),
    ]:
        path = 'assets/' + name
        if path not in files:
            files[path] = json_bytes(seed())
        else:
            value = read_json(files[path].decode('utf-8'))
            if not isinstance(value, dict) or value.get('skill') != profile['skill']:
                raise ValueError('existing policy asset needs reconciliation: ' + name)
