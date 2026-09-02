import copy
import json
import pathlib
import sys
import unittest

from test_comparison_support import add_controlled_comparisons


ROOT = pathlib.Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
FIXTURES = ROOT / "evals" / "files"
sys.path.insert(0, str(ROOT / "scripts"))


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def catalogs():
    return {
        "defects": load(ASSETS / "visual-defect-catalog.json"),
        "judgments": load(ASSETS / "judgment-review-catalog.json"),
        "invariants": load(ASSETS / "perceptual-motor-invariant-catalog.json"),
    }


def final_claims(document):
    document["claims"].update(
        {
            "non_slop": True,
            "original_within_scope": True,
            "taste_pass": True,
            "non_ai_slop": True,
            "unique_within_declared_corpus": True,
            "invariants_satisfied": True,
        }
    )
    for check in document["quality_checks"]:
        check["status"] = "pass"
        if check["name"] == "render_integrity":
            check["evidence"] = "Final wide and narrow native visual review found no unresolved veto or major defect."


def final_tracks(review_catalogs):
    return [
        {
            "name": track,
            "status": "pass",
            "obligations_checked": [item["id"] for item in review_catalogs["judgments"]["review_obligations"] if item["track"] == track],
            "evidence": "Located source, token, comparison, and rendered observations support this bounded pass.",
            "counterevidence": "The strongest plausible failure was tested and did not contradict the bounded pass.",
        }
        for track in review_catalogs["judgments"]["tracks"]
    ]


def objective_reviews(review_catalogs):
    return {
        "defect_review": {
            "catalog_version": review_catalogs["defects"]["catalog_version"],
            "status": "pass",
            "reviewed_ids": [item["id"] for item in review_catalogs["defects"]["markers"]],
            "findings": [],
            "unresolved_veto_count": 0,
            "unresolved_major_count": 0,
        },
        "invariant_review": {
            "catalog_version": review_catalogs["invariants"]["catalog_version"],
            "status": "pass",
            "entries": [
                {"id": item["id"], "status": "pass", "reason": "Applied use passed token feasibility and rendered visual review."}
                for item in review_catalogs["invariants"]["invariants"]
            ],
        },
    }


def final_review(review_catalogs):
    gate = review_catalogs["judgments"]["token_quality_gate"]
    review = {
        "status": "pass",
        "vision_executor": {"capability": "strong-native-vision", "mode": "active"},
        "viewports": [
            {"name": "wide", "width": 1440, "height": 1000, "status": "pass", "regions": ["whole-frame", "header", "evidence", "specimens"], "findings": "Hierarchy, evidence, and specimens were inspected at whole-frame and detail scale."},
            {"name": "narrow", "width": 320, "height": 900, "status": "pass", "regions": ["whole-frame", "header", "evidence", "specimens"], "findings": "Reflow, target spacing, legibility, and evidence access were inspected at detail scale."},
        ],
        "judgment_reviews": {
            "catalog_version": review_catalogs["judgments"]["catalog_version"],
            "tracks": final_tracks(review_catalogs),
        },
        "token_quality_gate": {
            "scope": "token_and_proof_only", "status": "pass",
            "diagnosis": "PASS", "whole_product_quality_proved": False,
            "gates": [{"id": gate_id, "status": "pass",
                       "evidence": "Current token paths and rendered proof support this gate."}
                      for gate_id in gate["gate_ids"]],
        },
        "final_readback": {
            "status": "pass",
            "reviewed_surface_sha256": "f" * 64,
            "artifact_locator": "sample.proof.html",
            "reviewed_after_final_assembly": True,
        },
    }
    review.update(objective_reviews(review_catalogs))
    return review


def final_evidence():
    document = load(FIXTURES / "sample.evidence.json")
    add_controlled_comparisons(
        document, load(FIXTURES / "sample.tokens.json"))
    review_catalogs = catalogs()
    final_claims(document)
    document["google_fonts"]["selection_review"] = {"status": "pass", "comparison": "Three eligible candidates were rendered side by side with source-specific operational text."}
    for item in document["google_fonts"]["selected"]:
        item["visual_review"] = {"status": "pass", "specimens": ["wide", "narrow", "small-text", "display"], "rationale": "Final pixels retained the intended hierarchy, source fit, script support, and legibility without fallback."}
    document["artifact_review"] = final_review(review_catalogs)
    return document


class ProofReviewTests(unittest.TestCase):
    def test_final_review_can_pass_only_with_full_catalog_coverage(self):
        from lib.proof import validate_evidence

        self.assertEqual(validate_evidence(final_evidence(), final=True, review_catalogs=catalogs()), [])

    def test_missing_defect_marker_blocks_final(self):
        from lib.proof import validate_evidence

        document = final_evidence()
        document["artifact_review"]["defect_review"]["reviewed_ids"].pop()
        errors = validate_evidence(document, final=True, review_catalogs=catalogs())
        self.assertIn("visual defect catalog coverage mismatch", " | ".join(errors))

    def test_failed_taste_track_blocks_final(self):
        from lib.proof import validate_evidence

        document = final_evidence()
        document["artifact_review"]["judgment_reviews"]["tracks"][0]["status"] = "fail"
        errors = validate_evidence(document, final=True, review_catalogs=catalogs())
        self.assertIn("judgment track taste must pass", " | ".join(errors))

    def test_not_applicable_invariant_needs_reason(self):
        from lib.proof import validate_evidence

        document = final_evidence()
        item = document["artifact_review"]["invariant_review"]["entries"][0]
        item.update({"status": "not_applicable", "reason": ""})
        errors = validate_evidence(document, final=True, review_catalogs=catalogs())
        self.assertIn("needs a reason", " | ".join(errors))

    def test_preliminary_evidence_keeps_judgment_claims_pending(self):
        from lib.proof import validate_evidence

        document = load(FIXTURES / "sample.evidence.json")
        self.assertEqual(validate_evidence(document, final=False, review_catalogs=catalogs()), [])


if __name__ == "__main__":
    unittest.main()
