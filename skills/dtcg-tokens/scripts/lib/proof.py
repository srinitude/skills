"""Evidence checks for input-specific token proof reports."""
import re

from lib.review import check_artifact_review

VISUAL_KINDS = {"image", "screenshot", "video", "pdf-page", "live-site"}
CHECKS = {
    "audience_relation", "visual_identity", "hierarchy", "cohesion",
    "non_genericity", "render_integrity", "possibility_accounting",
    "context_coverage", "coverage_integrity", "temporal_currency",
    "font_selection",
    "taste", "originality", "corpus_uniqueness", "non_ai_slop",
    "perceptual_motor_invariants", "objective_visual_defects",
    "experimental_output",
}
SHA256_RE = re.compile(r"[a-f0-9]{64}")


def required(document, key, kind, errors):
    value = document.get(key)
    if not isinstance(value, kind) or not value:
        errors.append(f"evidence.{key} must be a nonempty {kind.__name__}")
    return value


def check_sources(evidence, errors):
    sources = required(evidence, "sources", list, errors) or []
    ids = set()
    for index, source in enumerate(sources):
        path = f"evidence.sources[{index}]"
        if not isinstance(source, dict) or not source.get("id") or source.get("id") in ids:
            errors.append(f"{path} needs a unique id")
            continue
        ids.add(source["id"])
        if not re.fullmatch(r"[a-f0-9]{64}", str(source.get("sha256", ""))):
            errors.append(f"{path}.sha256 must hold 64 lowercase hex characters")
        if source.get("kind") in VISUAL_KINDS and source.get("vision_inspected") is not True:
            errors.append(f"{path} requires native vision inspection")
        passes = source.get("vision_passes", [])
        if source.get("kind") in VISUAL_KINDS and not {"whole-frame", "detail", "comparative"} <= set(passes):
            errors.append(f"{path} requires whole-frame, detail, and comparative vision passes")
    return ids


def check_observations(evidence, ids, errors):
    observations = required(evidence, "observations", list, errors) or []
    if len(observations) < 3:
        errors.append("evidence.observations needs at least three source-linked facts")
    for index, item in enumerate(observations):
        path = f"evidence.observations[{index}]"
        if not isinstance(item, dict) or item.get("source_id") not in ids:
            errors.append(f"{path}.source_id must match a source")
        if not isinstance(item, dict) or item.get("confidence") not in {"high", "moderate", "low"}:
            errors.append(f"{path}.confidence must be high, moderate, or low")
        if not isinstance(item, dict) or len(str(item.get("fact", ""))) < 20:
            errors.append(f"{path}.fact must state visible evidence")
        if not isinstance(item, dict) or item.get("basis") not in {"observed", "inferred", "assumed"}:
            errors.append(f"{path}.basis must be observed, inferred, or assumed")
        if not isinstance(item, dict) or not item.get("locator") or not item.get("region"):
            errors.append(f"{path} needs locator and region")


def check_signatures(evidence, errors):
    decisions = required(evidence, "signature_decisions", list, errors) or []
    if len(decisions) < 5:
        errors.append("evidence.signature_decisions needs at least five input-specific decisions")
    for index, item in enumerate(decisions):
        if not isinstance(item, dict) or len(str(item.get("evidence", ""))) < 10:
            errors.append(f"evidence.signature_decisions[{index}] needs supporting evidence")
        if not isinstance(item, dict) or not isinstance(item.get("tokens"), list) or not item.get("tokens"):
            errors.append(f"evidence.signature_decisions[{index}] needs token paths")


def check_quality(evidence, errors, final):
    checks = required(evidence, "quality_checks", list, errors) or []
    names = {item.get("name") for item in checks if isinstance(item, dict)}
    missing = CHECKS - names
    if missing:
        errors.append(f"evidence.quality_checks missing: {', '.join(sorted(missing))}")
    allowed = {"pass"} if final else {"pass", "pending_visual_review"}
    for item in checks:
        if item.get("name") in CHECKS and (item.get("status") not in allowed or len(str(item.get("evidence", ""))) < 15):
            errors.append(f"quality check {item.get('name')} needs an allowed status plus observed evidence")


def check_claims(evidence, errors, final):
    claims = evidence.get("claims", {})
    comparison = evidence.get("comparison", {})
    if claims.get("globally_unique") or comparison.get("scope") == "global":
        errors.append("global uniqueness is not a provable claim")
    if claims.get("dtcg_conformant") is not True:
        errors.append("evidence.claims.dtcg_conformant must be true after validation")
    allowed = {True} if final else {True, "pending_visual_review"}
    for key in (
        "non_slop",
        "original_within_scope",
        "taste_pass",
        "non_ai_slop",
        "unique_within_declared_corpus",
        "invariants_satisfied",
    ):
        if claims.get(key) not in allowed:
            errors.append(f"evidence.claims.{key} must wait for or pass visual review")
    if comparison.get("scope") != "declared-corpus" or not comparison.get("corpus_name"):
        errors.append("evidence.comparison must name a declared comparison corpus")
    if not isinstance(comparison.get("items_compared"), int) or comparison.get("items_compared", 0) < 1:
        errors.append("evidence.comparison.items_compared must be positive")
    limits = evidence.get("limits", [])
    if not any("Global uniqueness is outside this skill's valid claim scope" in str(item) for item in limits):
        errors.append("evidence.limits must state the global uniqueness limit")


def check_font_candidate(item, cutoff, required_subsets, errors):
    family = item.get("family") if isinstance(item, dict) else None
    rank = item.get("popularity_rank") if isinstance(item, dict) else None
    if not family or not isinstance(rank, int) or rank <= cutoff:
        errors.append(f"google font candidate {family} must rank outside the most popular 50%")
    if not isinstance(item, dict) or item.get("eligible") is not True or item.get("reasons"):
        errors.append(f"google font candidate {family} must have a clean eligibility result")
    elif not set(required_subsets) <= set(item.get("subsets", [])):
        errors.append(f"google font candidate {family} lacks a required subset")


def check_selected_font(item, candidates, errors, final):
    family = item.get("family") if isinstance(item, dict) else None
    if not isinstance(item, dict):
        errors.append(f"selected Google Font {family} must be an object")
        return
    if family not in candidates or not item.get("token_paths"):
        errors.append(f"selected Google Font {family} needs candidate and token-path evidence")
    license_record = item.get("license", {})
    if not SHA256_RE.fullmatch(str(license_record.get("sha256", ""))) or not license_record.get("text"):
        errors.append(f"selected Google Font {family} needs a hashed license record")
    assets = item.get("assets", [])
    if not assets:
        errors.append(f"selected Google Font {family} needs WOFF2 assets")
    for asset in assets:
        if asset.get("format") != "woff2" or not SHA256_RE.fullmatch(str(asset.get("sha256", ""))):
            errors.append(f"selected Google Font {family} has an invalid WOFF2 record")
    review = item.get("visual_review", {})
    allowed = {"pass"} if final else {"pass", "pending_visual_review"}
    if review.get("status") not in allowed or final and len(str(review.get("rationale", ""))) < 20:
        errors.append(f"selected Google Font {family} needs comparative visual review")


def check_google_fonts(evidence, errors, final):
    record = evidence.get("google_fonts")
    if not isinstance(record, dict):
        errors.append("evidence.google_fonts must be an object")
        return
    total, cutoff = record.get("total_families"), record.get("cutoff_rank")
    if not isinstance(total, int) or total < 3 or cutoff != total // 2 or record.get("excluded_top_fraction") != 0.5:
        errors.append("evidence.google_fonts needs the exact live popular-half cutoff")
        cutoff = total // 2 if isinstance(total, int) else 0
    if record.get("catalog_url") != "https://fonts.google.com/metadata/fonts" or not SHA256_RE.fullmatch(str(record.get("catalog_sha256", ""))) or not record.get("catalog_response_date") or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(record.get("run_date", ""))):
        errors.append("evidence.google_fonts needs a dated and hashed live catalog capture")
    required_subsets = record.get("required_subsets", [])
    if not isinstance(required_subsets, list) or not required_subsets or not all(isinstance(item, str) and item for item in required_subsets):
        errors.append("evidence.google_fonts needs required source subsets")
        required_subsets = []
    candidates = record.get("candidates", [])
    if len({item.get("family") for item in candidates if isinstance(item, dict)}) < 3:
        errors.append("evidence.google_fonts needs at least three unique candidates")
    for item in candidates:
        check_font_candidate(item, cutoff, required_subsets, errors)
    candidate_names = {item.get("family") for item in candidates if isinstance(item, dict)}
    selected = record.get("selected", [])
    if not selected or set(record.get("selected_families", [])) != {item.get("family") for item in selected if isinstance(item, dict)}:
        errors.append("evidence.google_fonts selected family records must agree")
    for item in selected:
        check_selected_font(item, candidate_names, errors, final)
    review = record.get("selection_review", {})
    allowed = {"pass"} if final else {"pass", "pending_visual_review"}
    if review.get("status") not in allowed or final and len(str(review.get("comparison", ""))) < 20:
        errors.append("evidence.google_fonts needs final comparative selection review")


def validate_evidence(evidence, final=False, review_catalogs=None):
    errors = []
    if not isinstance(evidence, dict):
        return ["evidence root must be an object"]
    ids = check_sources(evidence, errors)
    check_observations(evidence, ids, errors)
    check_signatures(evidence, errors)
    check_quality(evidence, errors, final)
    check_claims(evidence, errors, final)
    check_google_fonts(evidence, errors, final)
    check_artifact_review(evidence, review_catalogs, errors, final)
    if len(str(evidence.get("identity_thesis", ""))) < 30:
        errors.append("evidence.identity_thesis must state the audience and visual idea")
    return errors
