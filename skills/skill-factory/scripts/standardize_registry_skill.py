#!/usr/bin/env python3
"""Plan or apply one factory-owned registry skill standardization."""
import argparse
import hashlib
import json
import shutil
import sys
import tomllib
from pathlib import Path

from standardization_assets import decisions, invocation, lifecycle, use_case, write_json
from standardization_baseline import restore_tracked_text
from standardization_contracts import repair_contracts
from standardization_discovery import enrich_profile
from standardization_format import format_target
from standardization_markdown import rewrite_markdown, script_task_map
from standardization_mapping import snapshot_public_lines
from standardization_mise import normalize_mise
from standardization_profile import load_profile, validate_profile
from standardization_rewrites import apply_rewrites, apply_section_rewrites
from standardization_seed import create_missing

FACTORY = Path(__file__).resolve().parents[1]
COPIES = [
    ("assets/improvement-contract.json", "assets/improvement-contract.json"),
    ("assets/mise-primitives-catalog.json", "assets/mise-primitives-catalog.json"),
    ("references/resource-and-experiment-design.md", "references/resource-and-experiment-design.md"),
    ("references/use-case-specificity.md", "references/use-case-specificity.md"),
    ("references/generation-contract.md", "references/generation-contract.md"),
]
SCRIPTS = [
    "agentic_request_contract.py", "run_agentic_request.py", "domain_text.py",
    "check_improvement_contract.py", "check_domain_research.py",
    "check_use_case_contract.py", "check_mise_primitives.py",
    "check_primitive_lifecycle.py", "check_task_graph.py",
    "check_decision_records.py", "check_invocation_receipt.py",
    "sync_mise_primitives.py",
]
SCRIPTS += ["validate_skill.py", "lint_writing.py", "check_code_rules.py",
            "check_evals.py", "check_placeholders.py"]
CANONICAL_SCRIPTS = set(SCRIPTS[:12]) | {
    "check_placeholders.py",
    "lint_writing.py",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def planned_paths(root, profile):
    paths = {path for path in root.rglob("*")
             if path.is_file() and "__pycache__" not in path.parts}
    paths.add(root / "evals/source-mapping.json")
    paths.add(root / "scripts/tests/test_package_contract.py")
    paths.update(root / target for _, target in COPIES)
    paths.update(root / "scripts" / name for name in SCRIPTS)
    assets = ["use-case-contract.json", "primitive-lifecycle.json",
              "decision-records.json", "invocation-receipt-template.json",
              "mise-primitives.json"]
    paths.update(root / "assets" / name for name in assets)
    paths.update(root / path for path in profile.get("text_rewrites", {}))
    paths.update(root / rule["path"]
                 for rule in profile.get("section_rewrites", []))
    return sorted(paths)


def copy_support(root):
    for source, target in COPIES:
        destination = root / target
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(FACTORY / source, destination)
    (root / "scripts").mkdir(exist_ok=True)
    for name in SCRIPTS:
        target = root / "scripts" / name
        if not target.exists() or name in CANONICAL_SCRIPTS:
            shutil.copyfile(FACTORY / "scripts" / name, target)


def write_assets(root, profile, tasks):
    contract = root / "assets/use-case-contract.json"
    stamp = existing_research_stamp(contract)
    write_json(contract, use_case(profile, tasks, stamp))
    write_json(root / "assets/primitive-lifecycle.json", lifecycle(profile))
    write_json(root / "assets/decision-records.json", decisions(profile))
    write_json(root / "assets/invocation-receipt-template.json", invocation(profile))
    catalog = json.loads((root / "assets/mise-primitives-catalog.json").read_text())
    write_json(root / "assets/mise-primitives.json", primitive_map(root, profile, catalog))


def existing_research_stamp(path):
    if not path.is_file():
        return None
    try:
        receipts = json.loads(path.read_text()).get("research_receipts", [])
    except json.JSONDecodeError:
        return None
    return receipts[0].get("checked_at") if receipts else None


def primitive_map(root, profile, catalog):
    with (root / "mise.toml").open("rb") as handle:
        config = tomllib.load(handle)
    actual = {"config": set(config) & set(catalog["groups"]["config"]),
              "task_config": set(config.get("task_config", {})), "tool": set()}
    actual["task"] = {key for task in config.get("tasks", {}).values()
                      for key in task if key in catalog["groups"]["task"]}
    actual["tool"] = {"version"} if config.get("tools") else set()
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


def apply(root, profile, rebase=False):
    if rebase:
        restore_tracked_text(root)
    create_missing(root, profile, FACTORY)
    profile = enrich_profile(root, profile)
    snapshots = snapshot_public_lines(root)
    apply_rewrites(root, profile, strict=False)
    apply_section_rewrites(root, profile)
    original = (root / "mise.toml").read_text(encoding="utf-8")
    normalized = normalize_mise(original, profile)
    (root / "mise.toml").write_text(normalized, encoding="utf-8")
    copy_support(root)
    with (root / "mise.toml").open("rb") as handle:
        tasks = tomllib.load(handle)["tasks"]
    owners = script_task_map(tasks)
    for path in root.rglob("*.md"):
        body = path.read_text(encoding="utf-8")
        path.write_text(rewrite_markdown(body, owners, profile,
                        add_contract=path == root / "SKILL.md"), encoding="utf-8")
    apply_rewrites(root, profile)
    repair_contracts(root, tasks, profile, owners, snapshots)
    write_assets(root, profile, tasks)
    format_target(root)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_root")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--rebase-tracked-text", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.skill_root)
    if root.is_symlink() or not (root / "SKILL.md").is_file():
        print("error: target must be a real skill directory", file=sys.stderr)
        return 2
    try:
        profile = validate_profile(load_profile(args.profile, root.name), root.resolve())
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    before = {str(path): digest(path) for path in planned_paths(root, profile)}
    if args.apply:
        apply(root, profile, args.rebase_tracked_text)
    after = {str(path): digest(path) for path in planned_paths(root, profile)}
    changed = [path for path in before if before[path] != after[path]]
    print(json.dumps({"target": str(root.resolve()), "mode": "apply" if args.apply else "plan",
                      "writes": len(changed), "changed": changed}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
