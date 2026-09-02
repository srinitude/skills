#!/usr/bin/env python3
"""Build Figma factory policy records from current owners."""
import argparse
import json
import tomllib
from pathlib import Path

from lib.factory_improvement import improvement_contract
from lib.factory_records import decision_records, primitive_roles

ASPECTS = ["actors", "objects", "actions", "states", "invariants", "variants",
           "interfaces", "authorities", "failures", "recoveries", "evidence",
           "time", "resources", "quality", "terminology", "exclusions"]
PRIMITIVES = ["skill_body", "references", "assets", "scripts", "tests",
              "mise_tasks", "examples", "evals", "policies", "schemas", "records"]
PHASES = ["discover", "research", "experiment", "decide", "create", "inspect",
          "update", "validate", "accept", "restore", "deprecate", "retire"]
TERMS = ["Figma design system", "Code Connect", "TypeScript React API",
         "direct visual audit", "component property parity", "Mise task graph"]
STAMP = "2026-09-02T07:26:49-04:00"


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def receipts():
    common = {"checked_at": STAMP, "disposition": "retained"}
    return [
        {**common, "source": "https://developers.figma.com/docs/code-connect/react/",
         "source_class": "first_party", "claim": "Code Connect maps Figma props to React code.",
         "limitations": "It cannot prove the TypeScript React API or rendered use.",
         "dimensions": ASPECTS},
        {**common, "source": "https://developers.figma.com/docs/plugins/api/ComponentPropertyType/",
         "source_class": "first_party", "claim": "Figma defines five native component property kinds.",
         "limitations": "A property kind does not prove a needed product control.",
         "dimensions": ASPECTS[:10]},
        {**common, "source": "https://developers.figma.com/docs/code-connect/template-files/",
         "source_class": "first_party", "claim": "Code Connect template files map nested parts and slots.",
         "limitations": "A valid template does not prove component property parity.",
         "dimensions": ASPECTS[3:]},
        {**common, "source": "https://developers.figma.com/docs/rest-api/files/",
         "source_class": "first_party", "claim": "A Figma design system file is a page and node tree.",
         "limitations": "Node data does not replace a direct visual audit.",
         "dimensions": ASPECTS},
        {**common, "source": "https://agentskills.io/specification",
         "source_class": "standard", "claim": "Agent Skills give this Code Connect skill a portable form.",
         "limitations": "The form cannot supply Figma design system judgment.",
         "dimensions": ASPECTS},
    ]


def task_records(tasks):
    return {name: {
        "outcome": f"The Figma design system gets the {name} result.",
        "motivation": f"Code Connect needs the {name} gate.",
        "value": f"Component property parity gains fresh {name} proof.",
        "proof": f"The Mise task graph records the {name} exit.",
        "applicability": f"Use {name} for its TypeScript React API check."}
        for name in tasks}


def operations():
    names = ["complete", "new-run", "validate-run", "invocation-policy",
             "agentic-request", "factory-assets-write", "generate", "skill-info",
             "mise-catalog-bootstrap", "mise-primitives-update"]
    return [{"task": name,
             "outcome": f"The Figma design system gets one {name} result.",
             "motivation": f"Code Connect uses one public {name} path.",
             "why_default_path": f"The Mise task graph owns the {name} route.",
             "proof": f"Component property parity keeps fresh {name} output."}
            for name in names]


def use_case(tasks):
    dimensions = {name: [f"The Figma design system record must name {name}."]
                  for name in ASPECTS}
    questions = {name: f"How can {name} change Code Connect proof?" for name in ASPECTS}
    return {"version": "1.0.0", "skill": "figma-code-connect-design-system",
        "outcome": "Create a Figma design system with TypeScript React API and Code Connect parity.",
        "motivations": [
            {"constraint": "Each Figma design system claim needs current readback and direct visual audit.",
             "reason": "Code Connect structure cannot prove current pixels or product fit.",
             "failure_prevented": "A Figma design system PASS from stale or unseen output."},
            {"constraint": "Each component property parity claim must reach a real TypeScript React API.",
             "reason": "Code Connect can map only real design and code contracts.",
             "failure_prevented": "A Code Connect map with fake props or missing nested parts."}],
        "domain_failures": [
            "A Figma design system passes file checks but has wrong pages or weak rendered design.",
            "Code Connect claims parity while text, boolean, enum, swap, slot, or nested use is missing."],
        "domain_evidence": [
            "Figma design system node readback, page ancestry, rendered states, and direct visual audit.",
            "Code Connect templates, TypeScript React API tests, property parity, and nested render proof."],
        "domain_terms": TERMS, "research_questions": questions,
        "research_receipts": receipts(),
        "disconfirmation": [{"question": "Can Code Connect alone prove design and code are the same?",
            "source": "https://developers.figma.com/docs/code-connect/",
            "checked_at": STAMP, "result": "No. Code Connect shows code in Figma but does not sync owners.",
            "disposition": "Keep Figma, TypeScript React API, mapping, and visual proof separate."}],
        "domain_dimensions": dimensions, "primitive_roles": primitive_roles(),
        "task_graph": {"ci_task": "ci", "public_operations": operations(),
                       "tasks": task_records(tasks)}}


def lifecycle():
    path = dict(zip(PHASES, ["new-run", "domain-research-policy", "test",
        "decision-policy", "new-run", "validate-run", "factory-assets-write",
        "complete", "package-records", "improvement-policy", "decision-policy",
        "package-records"]))
    aspects = {name: {"profile": "figma-code-lifecycle",
        "outcome": f"The Figma design system can trace {name}.",
        "motivation": f"Code Connect needs an owner for {name}.",
        "proof": f"Component property parity records the {name} gate."} for name in ASPECTS}
    primitives = {name: {"profile": "figma-code-lifecycle"} for name in PRIMITIVES}
    return {"version": "1.0.0", "skill": "figma-code-connect-design-system",
            "required_phases": PHASES, "profiles": {"figma-code-lifecycle": path},
            "aspects": aspects, "primitives": primitives}


def dispositions(config, catalog):
    groups = {"config": set(config) & set(catalog["groups"]["config"])}
    groups["task"] = {key for task in config["tasks"].values()
                      for key in task if key in catalog["groups"]["task"]}
    groups["task_config"] = set(config.get("task_config", {}))
    groups["tool"] = {"version"} if config.get("tools") else set()
    records = {}
    for name, all_names in catalog["groups"].items():
        used = sorted(groups[name])
        records[name] = {"used": used,
            "not_applicable": sorted(set(all_names) - set(used)),
            "used_reason": f"The Figma design system uses these {name} parts for proof.",
            "nonuse_reason": f"Other Code Connect {name} parts add no proved value.",
            "creative_use": f"Component property parity puts these {name} parts on one path.",
            "evidence": "Current Mise task graph and Figma skill checks."}
    return {"version": "1.0.0", "skill": "figma-code-connect-design-system",
            "catalog_version": catalog["version"], "groups": records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    root = Path(parser.parse_args().root).resolve()
    with (root / "mise.toml").open("rb") as handle:
        config = tomllib.load(handle)
    catalog = json.loads((root / "assets/mise-primitives-catalog.json").read_text())
    write(root / "assets/use-case-contract.json", use_case(config["tasks"]))
    write(root / "assets/primitive-lifecycle.json", lifecycle())
    write(root / "assets/decision-records.json", decision_records())
    write(root / "assets/mise-primitives.json", dispositions(config, catalog))
    write(root / "assets/improvement-contract.json", improvement_contract())
    write(root / "assets/invocation-receipt-template.json", {"version": "1.0.0",
        "skill": "figma-code-connect-design-system", "operation": "Name real Figma work.",
        "entries": [], "entry_rule": "Add each used Mise task after real work.",
        "proof_rule": "Tie each task to fresh Figma and Code Connect proof."})
    print("Figma factory policy records: updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
