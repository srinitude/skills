"""Domain-specific policy records for the Figma skill factory path."""

ROLE_PURPOSES = {
    "skill_body": "order the Figma design system and Code Connect workflow",
    "references": "bound current Figma and Code Connect source meaning",
    "assets": "hold component property parity and run contracts",
    "scripts": "perform fixed Figma ledger and package checks",
    "tests": "disprove false Figma and TypeScript React API passes",
    "mise_tasks": "order cached Figma checks on one dependency path",
    "examples": "show real Figma requests, outputs, and blocked branches",
    "evals": "test Figma triggers, behavior, recovery, and speed",
    "policies": "separate Figma authority, model judgment, and fixed checks",
    "schemas": "fix Figma run, property, state, and proof shapes",
    "records": "preserve Figma readback, vision, mapping, and invalidation proof",
}

DECISION_PURPOSES = {
    "mise-envelope": (
        "The Mise task graph fixes every repeatable Figma check.",
        "Code Connect proof needs deterministic ordering and typed receipts.",
        "The Mise task graph owns parsing, task links, hashes, and exit states.",
        "A Figma design system run exposes missing or stale fixed evidence early.",
        "The Mise task graph records each fixed gate and dependency.",
        "The Figma design system leaves a repeatable check to unrecorded model choice.",
    ),
    "direct-vision-owner": (
        "A direct visual audit owns every Figma visual-quality decision.",
        "A direct visual audit cannot be replaced by Figma node structure.",
        "The direct visual audit owner makes current rendered-pixel judgments.",
        "The Figma design system rejects unseen or visually weak output.",
        "Direct visual audit receipts name current pages, views, and findings.",
        "A direct visual audit PASS exists without current rendered pixels or sight.",
    ),
    "property-parity-owner": (
        "Component property parity joins Figma properties to real code APIs.",
        "Code Connect cannot repair a missing TypeScript React API.",
        "Component property parity traces product need across Figma, code, mapping, and render.",
        "Code Connect mappings stop inventing props or hiding nested gaps.",
        "Component property parity records every property kind and owner.",
        "A mapped Figma property lacks a real TypeScript React API or render.",
    ),
    "mutation-authority": (
        "Figma design system mutations stay inside explicit human authority.",
        "The Figma design system separates writes, publication, and deletion.",
        "The Figma design system gives each exact permission to the human owner.",
        "Code Connect work cannot silently publish or overwrite design state.",
        "Figma design system mutation receipts preserve authority and readback.",
        "The Figma design system has a mutation without exact human permission.",
    ),
    "safe-skill-change": (
        "The Mise task graph keeps only nonregressing skill changes.",
        "Code Connect workflow speed cannot trade away correctness or model judgment.",
        "The Mise task graph owns the baseline, measures, comparison, and restore path.",
        "Code Connect skill changes improve one part without harming another.",
        "The Mise task graph records before and after measures and digests.",
        "The Mise task graph finds a changed skill worse than its baseline.",
    ),
}


def primitive_roles():
    records = {}
    for name, purpose in ROLE_PURPOSES.items():
        label = name.replace("_", " ")
        records[name] = {
            "ownership": "domain_specific",
            "role": f"The Figma design system uses the {label} owner to {purpose}.",
            "outcome": f"The Figma design system can trace {label} work.",
            "motivation": f"Code Connect needs {label} evidence at its true owner.",
            "value": f"The TypeScript React API gains current {label} proof.",
            "failure_prevented": f"A direct visual audit rejects stale {label} claims.",
            "proof": f"The Mise task graph checks the {label} output.",
        }
    return records


def decision_records():
    owners = {"mise-envelope": ("deterministic", "mise"),
              "direct-vision-owner": ("model_owned", "model"),
              "property-parity-owner": ("model_owned", "model"),
              "mutation-authority": ("human_owned", "human"),
              "safe-skill-change": ("deterministic", "mise")}
    records = []
    for name, values in DECISION_PURPOSES.items():
        kind, owner = owners[name]
        outcome, motivation, why, effect, proof, falsifier = values
        records.append({"id": name, "kind": kind, "owner": owner,
            "outcome": outcome, "motivation": motivation, "why_this_path": why,
            "inputs": ["current Figma readback", "TypeScript React API proof"],
            "expected_effect": effect, "proof": proof, "falsifier": falsifier,
            "failure_branch": f"Code Connect blocks and returns to {name}."})
    return {"version": "1.0.0", "skill": "figma-code-connect-design-system",
            "records": records}
