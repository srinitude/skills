"""Validate then promote one reviewed, digest-bound variant candidate."""
import base64
import contextlib
import io
from pathlib import Path

from check_lineage import current_document
from check_target import run_mode
from skill_package import content_files, inventory, real_path, tree_digest
from skill_scope import load_json, read_fields
from variant_plan import opaque_files, validate_plan
from variant_review import check_privacy, check_review, run_behavior
from variant_context import check_current
from scope_placement import check_placement
from agentic_request_contract import read_json
from review_ledger_context import require
from scaffold_review import current_inputs, read_context
from variant_publication_plan import publication_plan
from variant_reviewed_publish import current_sources, publication_review, publish_reviewed


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


def acceptance_inputs(plan, candidate, review):
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
        return target, True
    expected = plan["refresh"]["target_files"] if plan["refresh"] else None
    expected = plan["source"]["files"] if plan["in_place"] else expected
    if target.exists() and inventory(target) != expected:
        raise ValueError("destination collision or changed target")
    return target, False


def future_publication(plan, candidate, review, factory, input_paths):
    record = current_document(candidate)
    record['derivation'] = derivation(plan, review, candidate)
    publication = publication_plan(plan, candidate, factory, input_paths, record)
    parsed = [read_json(base64.b64decode(x['content_base64']).decode('utf-8'))
              for x in publication['inputs']]
    require(parsed == [plan, review], 'variant plan or review changed while loading')
    return publication


def validate_stage(plan, candidate, review):
    result = package_checks(candidate)
    results = run_behavior(plan, candidate, review)
    check_privacy(plan, candidate, review)
    return [result, *results]


def accept(plan, candidate, review, *, input_paths, plan_path=None, ledger_review=None, preview=False):
    require(preview or plan_path and ledger_review, 'variant publication requires --plan-file and --ledger-review')
    require(not preview or not (plan_path or ledger_review), 'preview cannot apply publication review flags')
    candidate = real_path(candidate)
    target, unchanged = acceptance_inputs(plan, candidate, review)
    factory = Path(__file__).resolve().parents[1]
    publication = future_publication(plan, candidate, review, factory, input_paths)
    if preview:
        return {'plan': publication, 'writes': 0, 'execution_acceptance': 'pending'}
    if unchanged:
        ledger, raw, _ = publication_review(plan_path, ledger_review, publication, factory)
        current_sources(plan, publication)
        current_inputs(factory, publication, ledger_review, raw)
        read_context(ledger['context'])
        return operation_report(plan, review, [{'status': 'PASS', 'claim': 'Exact accepted rerun; no writes.'}], True)
    validation, writes = publish_reviewed(plan, publication, factory, plan_path, ledger_review,
        validate_candidate=lambda stage: validate_stage(plan, stage, review))
    return {**operation_report(plan, review, validation), 'writes': writes, 'execution_acceptance': 'pending'}
