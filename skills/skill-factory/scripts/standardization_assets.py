"""Build factory policy assets for one registry skill."""
import datetime
import json
from pathlib import Path

from standardization_profile import DIMENSIONS, PHASES, PRIMITIVES


def phrase(profile, subject):
    return f"{profile['primary_term']} {subject}"


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
                  "improvement-policy", "mise-primitives-update"]
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


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
