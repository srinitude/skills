#!/usr/bin/env python3
"""Build product-design factory policy assets from current owners."""
import argparse
import json
import tomllib
from pathlib import Path

ASPECTS = ["actors", "objects", "actions", "states", "invariants", "variants",
           "interfaces", "authorities", "failures", "recoveries", "evidence",
           "time", "resources", "quality", "terminology", "exclusions"]
PRIMITIVES = ["skill_body", "references", "assets", "scripts", "tests",
              "mise_tasks", "examples", "evals", "policies", "schemas",
              "records"]
PHASES = ["discover", "research", "experiment", "decide", "create", "inspect",
          "update", "validate", "accept", "restore", "deprecate", "retire"]
TERMS = ["product design", "human eye", "human brain", "human touch",
         "material design experiment", "Mise task graph"]
STAMP = "2026-09-02T07:26:49-04:00"


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def research_receipts():
    return [
        {"source": "https://www.w3.org/TR/WCAG22/", "source_class": "standard",
         "claim": "WCAG 2.2 sets access rules for product design.",
         "disposition": "retained", "checked_at": STAMP,
         "limitations": "It cannot judge product design fit or visual quality.",
         "dimensions": ["actors", "states", "invariants", "interfaces", "authorities", "failures", "recoveries", "evidence", "quality", "exclusions"]},
        {"source": "https://developer.apple.com/design/human-interface-guidelines/accessibility", "source_class": "first_party",
         "claim": "Apple links product design size and space to ease of use.",
         "disposition": "adapted", "checked_at": STAMP,
         "limitations": "It does not set each product design choice.",
         "dimensions": ["actors", "objects", "actions", "states", "variants", "interfaces", "failures", "recoveries", "evidence", "resources", "quality"]},
        {"source": "https://developer.apple.com/design/human-interface-guidelines/focus-and-selection/", "source_class": "first_party",
         "claim": "Apple keeps product design focus apart from selection when an act changes context.",
         "disposition": "retained", "checked_at": STAMP,
         "limitations": "It does not set one product design style.",
         "dimensions": ["actions", "states", "invariants", "variants", "interfaces", "terminology", "quality"]},
        {"source": "https://design-system.service.gov.uk/styles/spacing/", "source_class": "practitioner",
         "claim": "GOV.UK gives product design space a clear role.",
         "disposition": "adapted", "checked_at": STAMP,
         "limitations": "Its scale is not product design truth for all work.",
         "dimensions": ["objects", "actions", "invariants", "variants", "interfaces", "time", "resources", "quality", "terminology"]},
        {"source": "https://agentskills.io/specification", "source_class": "standard",
         "claim": "Agent Skills give product design work a portable file form.",
         "disposition": "adapted", "checked_at": STAMP,
         "limitations": "The form does not supply product design judgment or sight.",
         "dimensions": ["actors", "objects", "actions", "interfaces", "authorities", "evidence", "time", "resources", "terminology", "exclusions"]},
    ]


def primitive_roles():
    found = {}
    for name in PRIMITIVES:
        label = name.replace("_", " ")
        found[name] = {
            "ownership": "domain_specific",
            "role": f"The human eye uses this {label} owner.",
            "outcome": f"The human eye can check {label} work.",
            "motivation": f"The human eye needs one {label} owner.",
            "value": f"The human eye gets fresh {label} proof.",
            "failure_prevented": f"The human eye avoids stale {label} work.",
            "proof": f"The human eye gets a fresh {label} task pass.",
        }
    return found


def task_records(tasks):
    found = {}
    for name, task in tasks.items():
        description = task.get("description", name)
        found[name] = {
            "outcome": f"The human eye uses {name}. {description}.",
            "motivation": f"The human eye needs {name}. It stops skipped work.",
            "value": f"The human eye gets fresh proof from {name}.",
            "proof": f"The human eye gets a zero exit from {name}.",
            "applicability": f"Use {name} for its human eye gate.",
        }
    return found


def operations():
    names = ["complete", "invocation-policy", "agentic-request", "factory-assets-write", "skill-info",
             "run-help", "run-scaffold", "review-checklist", "human-sweep", "lineage-file",
             "run-start", "run-packet", "run-record", "run-select-rules",
             "run-check", "generate", "mise-primitives-update"]
    return [{"task": name,
             "outcome": f"The human eye gets the named {name} result.",
             "motivation": f"The human eye uses one public {name} path.",
             "why_default_path": f"The human eye has one {name} route.",
             "proof": f"The human eye gets fresh {name} output and an exit code."}
            for name in names]


def use_case_motivations():
    return [{
        "constraint": "Every product design choice needs current human eye, human brain, and human touch proof.",
        "reason": "Product design metrics and valid files cannot establish visual quality or product fit.",
        "failure_prevented": "Product design acceptance from unseen pixels or a numeric average.",
    }, {
        "constraint": "Every repeatable product design mechanic uses one Mise task graph path.",
        "reason": "Product design judgment works better when deterministic checks expose current evidence and failures.",
        "failure_prevented": "Product design work that bypasses experiments, lower-owner locks, or package proof.",
    }]


def use_case(tasks):
    questions = {name: f"How can {name} change product design proof or repair?" for name in ASPECTS}
    dimensions = {name: [f"The human eye record must name {name}."] for name in ASPECTS}
    return {"version": "1.0.0", "skill": "design-like-im-5",
            "outcome": "Produce clear, usable, distinctive product design with current direct visual proof.",
            "motivations": use_case_motivations(),
            "domain_failures": [
                "Product design passes structure checks but remains generic, confusing, inaccessible, or visually weak.",
                "Product design claims quality from metadata, hashes, or unviewed captures instead of current human eye proof.",
            ],
            "domain_evidence": [
                "Product design experiments, state records, rendered views, interaction paths, and same-executor vision receipts.",
                "Human brain and human touch judgments with counterevidence, uncertainty, scope, and accepting owners.",
            ],
            "domain_terms": TERMS, "research_questions": questions,
            "research_receipts": research_receipts(),
            "disconfirmation": [{"question": "Can product design standards or metrics alone prove visual quality?",
                "source": "https://www.w3.org/TR/WCAG22/", "checked_at": STAMP,
                "result": "No. Access rules cannot replace current product design sight.",
                "disposition": "Keep product design measures and direct sight as two gates."}],
            "domain_dimensions": dimensions, "primitive_roles": primitive_roles(),
            "task_graph": {"ci_task": "ci", "public_operations": operations(),
                           "tasks": task_records(tasks)}}


def lifecycle():
    profile = dict(zip(PHASES, ["run-scaffold", "domain-research-policy", "run-packet",
        "run-select-rules", "run-record", "review-checklist", "generate", "complete",
        "run-check", "improvement-policy", "decision-policy", "directories"]))
    aspects = {name: {"profile": "product-design-lifecycle",
        "outcome": f"The human eye can see {name}.",
        "motivation": f"The human eye needs one owner for {name}.",
        "proof": f"The human eye sees the {name} owner and gate."} for name in ASPECTS}
    primitives = {name: {"profile": "product-design-lifecycle"} for name in PRIMITIVES}
    return {"version": "1.0.0", "skill": "design-like-im-5",
            "required_phases": PHASES, "profiles": {"product-design-lifecycle": profile},
            "aspects": aspects, "primitives": primitives}


def decisions():
    specs = [("mise-envelope", "deterministic", "mise"),
             ("direct-vision-owner", "model_owned", "model"),
             ("material-experiment-lock", "model_owned", "model"),
             ("human-authority", "human_owned", "human"),
             ("nonregressing-improvement", "deterministic", "mise")]
    records = []
    for identifier, kind, owner in specs:
        records.append({"id": identifier, "kind": kind,
            "outcome": "The human eye can guard this choice.",
            "motivation": "The human eye needs this guard.",
            "why_this_path": f"The human eye gives this check to {owner}.",
            "owner": owner, "inputs": ["product design contract", "current evidence"],
            "expected_effect": "The human eye can test it.",
            "proof": "The human eye has fresh proof.",
            "falsifier": "The human eye sees no proof.",
            "failure_branch": f"The human eye blocks it. Go back to {identifier}."})
    return {"version": "1.0.0", "skill": "design-like-im-5", "records": records}


def invocation_template():
    return {
        "version": "1.0.0",
        "skill": "design-like-im-5",
        "operation": "Name the real product design work.",
        "entries": [],
        "entry_rule": "Add each used Mise task once after real work.",
        "proof_rule": "Tie each task to fresh product design proof.",
    }


def primitive_dispositions(root, config, catalog):
    groups = {"config": set(config) & set(catalog["groups"]["config"])}
    groups["task"] = {key for task in config["tasks"].values()
                      for key in task if key in catalog["groups"]["task"]}
    groups["task_config"] = set(config.get("task_config", {}))
    groups["tool"] = {"version"} if config.get("tools") else set()
    records = {}
    for name, available in catalog["groups"].items():
        used = sorted(groups[name])
        records[name] = {"used": used, "not_applicable": sorted(set(available) - set(used)),
            "used_reason": f"Product design uses these {name} parts for task proof.",
            "nonuse_reason": f"Other product design {name} parts add no proved value.",
            "creative_use": f"Product design puts these {name} parts on one proof path.",
            "evidence": "Current product design task file and checks."}
    return {"version": "1.0.0", "skill": "design-like-im-5",
            "catalog_version": catalog["version"], "groups": records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    with (root / "mise.toml").open("rb") as handle:
        config = tomllib.load(handle)
    catalog = json.loads((root / "assets/mise-primitives-catalog.json").read_text())
    write(root / "assets/use-case-contract.json", use_case(config["tasks"]))
    write(root / "assets/primitive-lifecycle.json", lifecycle())
    write(root / "assets/decision-records.json", decisions())
    write(root / "assets/invocation-receipt-template.json", invocation_template())
    write(root / "assets/mise-primitives.json", primitive_dispositions(root, config, catalog))
    print("product-design factory assets: updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
