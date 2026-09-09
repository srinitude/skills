"""Stage standardization, then consume evidence at its delivery boundary."""
from pathlib import Path

from skill_package import copy_owned, inventory, promote, real_path, staged, tree_digest
from skill_scope import read_fields, scoped_text
from source_coverage import load_json, require
from invocation_acceptance import bindings, guard


def prepare_path(value, root):
    output = real_path(value)
    require(output.name == root.name, "prepared candidate must keep the skill name")
    require(not output.is_relative_to(root) and not root.is_relative_to(output),
            "prepared candidate must be outside the original skill")
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def stage_candidate(candidate, root, profile, scope, audience, args):
    from standardization_baseline import restore_tracked_text
    from standardize_registry_skill import apply
    if args.candidate:
        require(not args.rebase_tracked_text, "rebase must occur before candidate review")
        prepared = real_path(args.candidate)
        require(not prepared.is_relative_to(root) and not root.is_relative_to(prepared),
                "candidate must be separate from the original skill")
        copy_owned(prepared, candidate)
    else:
        copy_owned(root, candidate)
        if args.rebase_tracked_text:
            restore_tracked_text(root, candidate)
        apply(candidate, profile, audience=audience)
        file = candidate / "SKILL.md"
        file.write_text(scoped_text(file.read_text(), scope), encoding="utf-8")
    fields = read_fields(candidate)
    require(fields["name"] == root.name and fields["metadata"].get("scope") == scope,
            "candidate identity or scope differs from standardization intent")
    require(load_json(candidate / "assets/use-case-contract.json")["audience"]["primary"] == audience,
            "candidate audience differs from standardization intent")


def execute(root, profile, scope, audience, args):
    from standardize_registry_skill import digest
    require(sum(bool(value) for value in [args.prepare, args.apply, args.check_candidate]) == 1,
            "prepare, check and apply are separate operations")
    require(not args.candidate or args.apply or args.check_candidate, "a reviewed candidate is for check or apply")
    require(not args.check_candidate or args.candidate, "checking requires a reviewed candidate")
    before = inventory(root)
    expected = {"route": "standardize-target", "inputs": {
        "source": tree_digest(before), "profile": digest(Path(args.profile)),
        "scope": scope, "audience": audience}}
    with staged(root.parent, root.name) as candidate:
        stage_candidate(candidate, root, profile, scope, audience, args)
        if args.check_candidate:
            guard(candidate, root, expected, bindings(args))
            return {"acceptance": "pending", "evidence_readiness": "passed",
                    "limit": "Read-only prospective check. The actual promotion must revalidate."}
        if args.prepare:
            output = prepare_path(args.prepare, root.resolve())
            promote(candidate, output, draft=True)
            return {"acceptance": "pending", "prepared": str(output),
                    "consumer_inputs": expected["inputs"], "sha256": tree_digest(inventory(output))}
        promote(candidate, root, before, acceptance=(expected, bindings(args)))
    return {"acceptance": "passed", "limit": "Only the host-bound claims for this standardization."}
