"""Structural contract for one vision-authored standalone proof artifact."""
import re

OBLIGATIONS = {
    "conformance", "inputs", "intent", "possibilities", "narrowing",
    "coverage", "token-specimens", "experiments", "permutations", "metrics",
    "perceptual-motor-invariants", "taste", "originality",
    "corpus-uniqueness", "non-ai-slop", "visual-review", "failures",
    "boundary", "embedded-data",
}
FORBIDDEN_MARKERS = {
    "data-style-fingerprint": "style fingerprints do not prove design quality",
    "data-content-fingerprint": "content fingerprints do not prove source specificity",
    "data-generation-method=\"token-directed\"": "automatic visual generation is prohibited",
}


def obligation_counts(text):
    names = re.findall(r'data-proof-obligation=["\']([^"\']+)["\']', text)
    return {name: names.count(name) for name in set(names)}


def check_obligations(text, errors):
    counts = obligation_counts(text)
    for name in sorted(OBLIGATIONS):
        if counts.get(name) != 1:
            errors.append(f"artifact obligation {name} must appear exactly once")
    unknown = sorted(set(counts) - OBLIGATIONS)
    if unknown:
        errors.append(f"unknown artifact obligations: {', '.join(unknown)}")


def check_external_assets(text, errors):
    tag = r'<(?:script|img|iframe|audio|video|source|link)\b[^>]*(?:src|href)=["\']https?://'
    css = r'url\(\s*["\']?https?://'
    if re.search(tag, text, re.IGNORECASE) or re.search(css, text, re.IGNORECASE):
        errors.append("external runtime asset blocks the standalone artifact")


def check_candidate(text):
    errors = []
    lowered = text.lower()
    if "<!doctype html>" not in lowered:
        errors.append("candidate needs an HTML doctype")
    if 'data-dtcg-proof="2.0"' not in text:
        errors.append("candidate needs data-dtcg-proof 2.0")
    if 'data-artifact-authorship="vision-authored"' not in text:
        errors.append("candidate must declare vision-authored artifact direction")
    if text.count("__DTCG_PROOF_DATA__") != 1 or text.count("__DTCG_RUN_ID__") != 1:
        errors.append("candidate needs one proof-data and one run-id placeholder")
    if text.count("__DTCG_PROOF_VERDICT__") != 1 or text.count("__DTCG_VERDICT_STATE__") != 1:
        errors.append("candidate needs one visible and one machine verdict placeholder")
    for marker, reason in FORBIDDEN_MARKERS.items():
        if marker in text:
            errors.append(reason)
    check_obligations(text, errors)
    check_external_assets(text, errors)
    return errors


def check_experimental_specimens(text, expected_paths):
    actual = re.findall(r'data-experimental-token=["\']([^"\']+)["\']', text)
    if len(actual) != len(set(actual)) or set(actual) != set(expected_paths):
        return ["experimental specimen coverage mismatch"]
    return []


def assemble(text, payload, run_id, verdict="pending"):
    packed = payload.replace("<", "\\u003c")
    result = text.replace("__DTCG_PROOF_DATA__", packed)
    result = result.replace("__DTCG_RUN_ID__", run_id)
    label = "RECORDED VISUAL REVIEW · BOUNDED PASS" if verdict == "recorded-pass" else "PENDING VISUAL REVIEW"
    result = result.replace("__DTCG_VERDICT_STATE__", verdict)
    return result.replace("__DTCG_PROOF_VERDICT__", label)
