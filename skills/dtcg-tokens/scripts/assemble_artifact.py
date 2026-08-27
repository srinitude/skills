#!/usr/bin/env python3
"""Embed validated proof data into a vision-authored HTML candidate.

This script does not design the artifact and does not issue a visual verdict.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from lib.accounting import validate_accounting
from lib.artifact_contract import assemble, check_candidate, check_experimental_specimens, check_visible_coverage, reviewed_surface_sha256
from lib.coverage import analyze_coverage
from lib.dtcg import read_json, validate
from lib.experiments import validate_experimental_output
from lib.proof import validate_evidence


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def arguments(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, help="vision-authored HTML with proof placeholders")
    parser.add_argument("--tokens", required=True, help="DTCG JSON")
    parser.add_argument("--evidence", required=True, help="evidence JSON")
    parser.add_argument("--output", required=True, help="assembled standalone HTML")
    parser.add_argument("--run-id", required=True, help="recorded run identity; never a design seed")
    return parser.parse_args(argv)


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def catalogs(root):
    assets = root / "assets"
    return {
        "possibility": load(assets / "token-possibility-catalog.json"),
        "inputs": load(assets / "multimodal-input-catalog.json"),
        "metrics": load(assets / "quality-metric-catalog.json"),
        "exploration": load(assets / "exploration-strategy-catalog.json"),
        "defects": load(assets / "visual-defect-catalog.json"),
        "judgments": load(assets / "judgment-review-catalog.json"),
        "invariants": load(assets / "perceptual-motor-invariant-catalog.json"),
    }


def evaluate(root, paths, tokens, evidence, source_errors):
    review_catalogs = catalogs(root)
    conformance = validate(paths[1], root / "assets" / "dtcg-format-2025.10.schema.json")
    accounting = validate_accounting(
        evidence,
        review_catalogs["possibility"],
        review_catalogs["inputs"],
        review_catalogs["metrics"],
    )
    coverage, coverage_errors = analyze_coverage(tokens, evidence)
    experiments = validate_experimental_output(tokens, evidence)
    errors = source_errors + conformance["errors"] + validate_evidence(
        evidence,
        review_catalogs={
            "defects": review_catalogs["defects"],
            "judgments": review_catalogs["judgments"],
            "invariants": review_catalogs["invariants"],
        },
    )
    errors += accounting["errors"] + coverage_errors + experiments["errors"]
    return conformance, accounting, coverage, experiments, review_catalogs, errors


def proof_payload(tokens, evidence, paths, conformance, accounting, coverage, experiments, review_catalogs, run_id):
    result = {
        "run_id": run_id,
        "assembly_status": "pending-visual-review",
        "tokens": tokens,
        "evidence": evidence,
        "conformance": conformance,
        "coverage_manifest": coverage,
        "experimental_output_manifest": experiments,
        "exploration_strategy_catalog": review_catalogs["exploration"],
        "quality_metric_catalog": review_catalogs["metrics"],
        "visual_defect_catalog": review_catalogs["defects"],
        "judgment_review_catalog": review_catalogs["judgments"],
        "perceptual_motor_invariant_catalog": review_catalogs["invariants"],
        "hashes": {"tokens": file_hash(paths[1]), "evidence": file_hash(paths[2])},
    }
    for key in ("input_accounting", "intent_accounting", "possibility_accounting", "narrowing_stages", "context_coverage", "temporal_accounting"):
        result[key] = accounting[key]
    return result


def recorded_verdict(tokens, evidence, review_catalogs, surface_sha256):
    catalogs_for_validation = {
        "defects": review_catalogs["defects"],
        "judgments": review_catalogs["judgments"],
        "invariants": review_catalogs["invariants"],
    }
    proof_errors = validate_evidence(evidence, final=True, review_catalogs=catalogs_for_validation)
    experiment_errors = validate_experimental_output(tokens, evidence, final=True)["errors"]
    expected = evidence.get("artifact_review", {}).get("final_readback", {}).get("reviewed_surface_sha256")
    return "recorded-pass" if not proof_errors and not experiment_errors and expected == surface_sha256 else "pending"


def render_artifact(candidate, payload, run_id, tokens, evidence, review_catalogs):
    packed = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    surface = reviewed_surface_sha256(assemble(candidate, packed, run_id, "pending"))
    verdict = recorded_verdict(tokens, evidence, review_catalogs, surface)
    payload["assembly_status"] = "recorded-visual-pass" if verdict == "recorded-pass" else "pending-visual-review"
    packed = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    rendered = assemble(candidate, packed, run_id, verdict)
    return rendered, surface, verdict


def main(argv=None):
    args = arguments(argv)
    paths = [Path(args.candidate), Path(args.tokens), Path(args.evidence)]
    if not all(path.is_file() for path in paths):
        print("error: candidate, tokens, and evidence must exist", file=sys.stderr)
        return 2
    candidate = paths[0].read_text(encoding="utf-8")
    errors = check_candidate(candidate)
    tokens, token_errors = read_json(paths[1])
    evidence, evidence_errors = read_json(paths[2])
    root = Path(__file__).resolve().parents[1]
    conformance, accounting, coverage, experiments, review_catalogs, report_errors = evaluate(root, paths, tokens, evidence, token_errors + evidence_errors)
    errors += report_errors
    errors += check_experimental_specimens(candidate, experiments["token_paths"])
    visible_coverage, visible_errors = check_visible_coverage(candidate, coverage)
    errors += visible_errors
    if errors:
        print("error: " + " | ".join(errors), file=sys.stderr)
        return 1
    coverage["visible_coverage"] = visible_coverage
    coverage["status"] = "pass"
    payload = proof_payload(tokens, evidence, paths, conformance, accounting, coverage, experiments, review_catalogs, args.run_id)
    rendered, surface_sha256, verdict = render_artifact(candidate, payload, args.run_id, tokens, evidence, review_catalogs)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    status = "assembled-recorded-visual-pass" if verdict == "recorded-pass" else "assembled-pending-visual-review"
    print(json.dumps({"status": status, "output": str(output), "sha256": file_hash(output), "reviewed_surface_sha256": surface_sha256, "run_id": args.run_id}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
