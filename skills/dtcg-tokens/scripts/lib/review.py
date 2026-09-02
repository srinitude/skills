"""Final artifact review checks for proof evidence."""
import re


def valid_hash(value):
    return re.fullmatch(r"[a-f0-9]{64}", str(value or "")) is not None


def check_viewports(review, errors, final):
    viewports = review.get("viewports", [])
    if not final:
        return
    names = {item.get("name") for item in viewports if isinstance(item, dict)}
    if not {"wide", "narrow"} <= names:
        errors.append("artifact review needs wide and narrow viewports")
    for index, item in enumerate(viewports):
        path = f"evidence.artifact_review.viewports[{index}]"
        if item.get("status") != "pass":
            errors.append(f"{path} must pass")
        if not isinstance(item.get("width"), int) or not isinstance(item.get("height"), int):
            errors.append(f"{path} needs integer width and height")
        if not isinstance(item.get("regions"), list) or len(item.get("regions", [])) < 3:
            errors.append(f"{path} needs whole-frame and detail regions")
        if len(str(item.get("findings", ""))) < 30:
            errors.append(f"{path} needs located visual findings")


def check_defect_review(review, catalog, errors, final):
    section = review.get("defect_review", {})
    if section.get("catalog_version") != catalog.get("catalog_version"):
        errors.append("visual defect catalog version mismatch")
    if not final:
        return
    expected = {item["id"] for item in catalog.get("markers", [])}
    actual = section.get("reviewed_ids", [])
    if len(actual) != len(set(actual)) or set(actual) != expected:
        errors.append("visual defect catalog coverage mismatch")
    if section.get("status") != "pass":
        errors.append("visual defect review must pass")
    if section.get("unresolved_veto_count") != 0 or section.get("unresolved_major_count") != 0:
        errors.append("visual defect review has unresolved veto or major findings")
    for index, item in enumerate(section.get("findings", [])):
        if item.get("marker_id") not in expected or not item.get("region") or not item.get("status"):
            errors.append(f"visual defect finding {index} needs marker, region, and status")


def check_invariant_review(review, catalog, errors, final):
    section = review.get("invariant_review", {})
    if section.get("catalog_version") != catalog.get("catalog_version"):
        errors.append("perceptual-motor invariant catalog version mismatch")
    if not final:
        return
    expected = {item["id"] for item in catalog.get("invariants", [])}
    entries = section.get("entries", [])
    ids = [item.get("id") for item in entries if isinstance(item, dict)]
    if len(ids) != len(set(ids)) or set(ids) != expected:
        errors.append("perceptual-motor invariant coverage mismatch")
    if section.get("status") != "pass":
        errors.append("perceptual-motor invariant review must pass")
    for item in entries:
        if item.get("status") not in {"pass", "not_applicable", "not_used_experimental"}:
            errors.append(f"invariant {item.get('id')} has invalid final status")
        if len(str(item.get("reason", ""))) < 15:
            errors.append(f"invariant {item.get('id')} needs a reason")


def check_judgment_reviews(review, catalog, errors, final):
    section = review.get("judgment_reviews", {})
    if section.get("catalog_version") != catalog.get("catalog_version"):
        errors.append("judgment review catalog version mismatch")
    if not final:
        return
    expected_tracks = set(catalog.get("tracks", []))
    tracks = section.get("tracks", [])
    names = [item.get("name") for item in tracks if isinstance(item, dict)]
    if len(names) != len(set(names)) or set(names) != expected_tracks:
        errors.append("judgment review track coverage mismatch")
    obligations = catalog.get("review_obligations", [])
    for track in tracks:
        name = track.get("name")
        expected = {item["id"] for item in obligations if item.get("track") == name}
        actual = track.get("obligations_checked", [])
        if track.get("status") != "pass":
            errors.append(f"judgment track {name} must pass")
        if len(actual) != len(set(actual)) or set(actual) != expected:
            errors.append(f"judgment track {name} obligation coverage mismatch")
        if len(str(track.get("evidence", ""))) < 30:
            errors.append(f"judgment track {name} needs located evidence")
        if len(str(track.get("counterevidence", ""))) < 30:
            errors.append(f"judgment track {name} needs counterevidence")


def check_token_quality_gate(record, contract, errors, final):
    if record.get("scope") != "token_and_proof_only":
        errors.append("token quality gate must stay token and proof only")
    if record.get("whole_product_quality_proved") is not False:
        errors.append("token quality gate cannot prove whole-product quality")
    allowed = {"pass"} if final else {"pass", "pending_visual_review"}
    if record.get("status") not in allowed:
        errors.append("token quality gate status is not allowed")
    gates = record.get("gates", [])
    ids = [item.get("id") for item in gates if isinstance(item, dict)]
    if final and ids != contract.get("gate_ids"):
        errors.append("token quality gate coverage mismatch")
    for item in gates:
        if final and item.get("status") != "pass":
            errors.append(f"token quality gate {item.get('id')} must pass")
        if final and len(str(item.get("evidence", ""))) < 15:
            errors.append(f"token quality gate {item.get('id')} needs current evidence")
    if final and record.get("diagnosis") != "PASS":
        errors.append("token quality gate final diagnosis must be PASS")


def check_readback(review, errors, final):
    if not final:
        return
    readback = review.get("final_readback", {})
    if readback.get("status") != "pass" or readback.get("reviewed_after_final_assembly") is not True:
        errors.append("final artifact readback must pass after final assembly")
    if not valid_hash(readback.get("reviewed_surface_sha256")):
        errors.append("final artifact readback needs a reviewed surface hash")
    if not readback.get("artifact_locator"):
        errors.append("final artifact readback needs an artifact locator")


def check_artifact_review(evidence, catalogs, errors, final):
    review = evidence.get("artifact_review", {})
    if not isinstance(review, dict) or not review:
        errors.append("evidence.artifact_review is required")
        return
    executor = review.get("vision_executor", {})
    if executor.get("capability") != "strong-native-vision" or executor.get("mode") not in {"active", "delegated"}:
        errors.append("artifact review requires an active or delegated strong-native-vision executor")
    if review.get("status") not in ({"pass"} if final else {"pending_visual_review", "pass"}):
        errors.append("artifact review status is not allowed")
    if not isinstance(catalogs, dict):
        errors.append("review catalogs are required")
        return
    check_token_quality_gate(
        review.get("token_quality_gate", {}),
        catalogs.get("judgments", {}).get("token_quality_gate", {}),
        errors, final)
    check_viewports(review, errors, final)
    check_defect_review(review, catalogs.get("defects", {}), errors, final)
    check_invariant_review(review, catalogs.get("invariants", {}), errors, final)
    check_judgment_reviews(review, catalogs.get("judgments", {}), errors, final)
    check_readback(review, errors, final)
