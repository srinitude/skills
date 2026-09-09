"""Validate then promote one reviewed, digest-bound variant candidate."""
import contextlib
import io
from pathlib import Path

from check_lineage import current_document, write_atomic
from check_target import run_mode
from skill_package import content_files, copy_owned, inventory, promote, real_path, staged, tree_digest
from skill_scope import load_json, read_fields
from variant_plan import opaque_files, validate_plan
from variant_review import check_privacy, check_review, run_behavior
from variant_context import check_current
from scope_placement import check_placement
from invocation_acceptance import guard


def existing_rerun(plan, review, target):
    if not target.exists() or plan["in_place"] or plan["refresh"]:
        return False
    try:
        prior = load_json(target / "evals/source-lineage.json")["derivation"]
        return (prior["plan_digest"] == tree_digest(plan)
                and prior["candidate_digest"] == review["candidate_digest"]
                and prior["target_baseline"] == content_files(target))
    except (KeyError, ValueError, OSError):
        return False


def package_checks(candidate):
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        failed = run_mode("validate", candidate) or run_mode("eval", candidate)
    if failed:
        raise ValueError("candidate package validation failed:\n" + output.getvalue())
    return {"status": "PASS", "evidence": output.getvalue(),
            "claim": "Factory structure, scope, writing, code, policies, and eval schemas pass."}


def derivation(plan, review, stage):
    source = plan["source"]
    result = {"schema_version": 1, "source": {key: source[key] for key in ["identity", "scope", "version", "digest"]},
              "target_scope": plan["target"]["scope"],
              "target_project": plan["project"]["identity"] if plan["project"] else None,
              "adaptations": review["adaptations"], "requirements": review["requirements"],
              "compatibility": review["compatibility"], "plan_digest": tree_digest(plan),
              "candidate_digest": review["candidate_digest"], "target_baseline": content_files(stage)}
    result["source"]["baseline"] = opaque_files(source["files"])
    result["adaptations"] = material_adaptations(review)
    return result


def material_adaptations(review):
    return [*review["adaptations"], *[f"Metadata {key}: {reason}" for key, reason
            in sorted(review.get("metadata_changes", {}).items())]]


def operation_report(plan, review, validation, unchanged=False):
    return {"status": "PASS", "operation": plan["operation"], "unchanged": unchanged,
            "source": {key: plan["source"][key] for key in ["identity", "name", "scope", "digest"]},
            "target": plan["target"], "material_adaptations": material_adaptations(review),
            "source_preserved": not plan["in_place"], "source_change_explicit": plan["in_place"],
            "validation": validation}


def accept(plan, candidate, review, bindings=None, prepare=None):
    validate_plan(plan)
    target = real_path(plan["target"]["path"])
    candidate = real_path(candidate)
    if any(candidate == p or candidate.is_relative_to(p) or p.is_relative_to(candidate)
           for p in [target, Path(plan["source"]["root"]) ]):
        raise ValueError("candidate must be separate from source and destination")
    check_current(plan)
    if plan["placement"]["kind"] == "installation":
        check_placement(plan["placement"], plan["target"]["scope"], target)
    check_review(plan, candidate, review)
    if existing_rerun(plan, review, target):
        if prepare:
            return prepared_report(target)
        guard(target, target, consumer(plan, review), bindings)
        return operation_report(plan, review, [{"status": "PASS", "claim": "Exact accepted rerun; no writes."}], True)
    expected = plan["refresh"]["target_files"] if plan["refresh"] else None
    expected = plan["source"]["files"] if plan["in_place"] else expected
    if target.exists() and inventory(target) != expected:
        raise ValueError("destination collision or changed target")
    return publish(plan, candidate, review, target, expected, bindings, prepare)


def publish(plan, candidate, review, target, expected, bindings=None, prepare=None):
    with staged(target.parent, target.name) as stage:
        copy_owned(candidate, stage)
        if tree_digest(inventory(stage)) != review["candidate_digest"]:
            raise ValueError("staged bytes differ from the reviewed candidate")
        package_result = package_checks(stage)
        results = run_behavior(plan, stage, review)
        if (tree_digest(inventory(stage)) != review["candidate_digest"]
                or inventory(stage) != inventory(candidate)):
            raise ValueError("behavior checks modified the candidate package")
        check_current(plan, stage.parent)
        record = current_document(stage)
        record["derivation"] = derivation(plan, review, stage)
        write_atomic(stage / "evals/source-lineage.json", record)
        check_privacy(plan, stage, review)
        if prepare:
            return prepare_stage(stage, prepare, plan, candidate)
        promote(stage, target, expected, acceptance=(consumer(plan, review), bindings))
    return operation_report(plan, review, [package_result, *results])


def consumer(plan, review):
    return {"route": "variant", "inputs": {"plan": tree_digest(plan), "review": tree_digest(review)}}


def prepare_stage(stage, destination, plan, candidate):
    output = real_path(destination)
    roots = [real_path(plan["source"]["root"]), real_path(plan["target"]["path"]), candidate]
    if plan["project"]:
        roots.append(real_path(plan["project"]["root"]))
    if output.name != stage.name or any(output.is_relative_to(p) or p.is_relative_to(output) for p in roots):
        raise ValueError("prepared candidate must keep its name outside source, target, candidate and project")
    output.parent.mkdir(parents=True, exist_ok=True)
    promote(stage, output, draft=True)
    return prepared_report(output)


def prepared_report(output):
    return {"status": "PENDING", "operation": "prepare", "prepared": str(output),
            "sha256": tree_digest(inventory(output)), "promoted": False,
            "claim": "Unaccepted candidate only; host-bound evidence is required before destination promotion."}
