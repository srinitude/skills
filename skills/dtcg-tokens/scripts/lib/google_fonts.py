"""Pure helpers for live Google Font rarity checks and offline CSS."""
import base64
import hashlib
import math
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


FONT_URL_RE = re.compile(r"url\((['\"]?)(https://fonts\.gstatic\.com/[^)'\"]+)\1\)\s*format\((['\"]?)woff2\3\)", re.IGNORECASE)
FACE_RE = re.compile(r"@font-face\s*\{.*?\}", re.IGNORECASE | re.DOTALL)


def validate_catalog_response_date(response_date, run_date, now=None, maximum_age_seconds=600):
    try:
        response = parsedate_to_datetime(response_date)
        declared = datetime.strptime(run_date, "%Y-%m-%d").date()
    except (TypeError, ValueError) as error:
        raise ValueError(f"E_FONT_CURRENT invalid catalog or run date: {error}") from error
    if response.tzinfo is None:
        response = response.replace(tzinfo=timezone.utc)
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    if current.astimezone().date() != declared:
        raise ValueError("E_FONT_CURRENT run date is not the current local date")
    age = abs((current.astimezone(timezone.utc) - response.astimezone(timezone.utc)).total_seconds())
    if age > maximum_age_seconds:
        raise ValueError(f"E_FONT_CURRENT catalog response is {int(age)} seconds from the current clock")
    return run_date


def family_records(catalog):
    records = catalog.get("familyMetadataList") if isinstance(catalog, dict) else None
    if not isinstance(records, list) or not records:
        raise ValueError("E_FONT_CURRENT catalog needs familyMetadataList")
    return records


def candidate_record(item, total, cutoff, required_subsets):
    rank = item.get("popularity")
    if not isinstance(rank, int) or rank < 1:
        raise ValueError(f"E_FONT_CURRENT invalid popularity rank for {item.get('family')}")
    subsets = set(item.get("subsets", []))
    reasons = []
    if rank <= cutoff:
        reasons.append("inside-most-popular-50-percent")
    if item.get("isOpenSource") is not True:
        reasons.append("not-open-source")
    if item.get("isBrandFont") is True:
        reasons.append("brand-font")
    if not set(required_subsets) <= subsets:
        reasons.append("missing-required-subset")
    percentile = (rank - 1) / (total - 1) if total > 1 else 0.0
    return {
        "family": item["family"], "popularity_rank": rank,
        "popularity_percentile": round(percentile, 6), "eligible": not reasons,
        "reasons": reasons, "category": item.get("category"),
        "subsets": item.get("subsets", []), "fonts": item.get("fonts", {}),
        "axes": item.get("axes", []),
    }


def evaluate_candidates(catalog, candidates, selected, threshold, required_subsets):
    records = family_records(catalog)
    total = len(records)
    fraction = threshold["excluded_top_fraction"]
    cutoff = math.floor(total * fraction)
    index = {item.get("family"): item for item in records}
    missing = [family for family in candidates if family not in index]
    if missing:
        raise ValueError("E_FONT_CURRENT unknown families: " + ", ".join(missing))
    evaluated = [candidate_record(index[name], total, cutoff, required_subsets) for name in candidates]
    return {
        "total_families": total, "cutoff_rank": cutoff,
        "excluded_top_fraction": fraction, "candidates": evaluated,
        "selected_families": list(selected),
    }


def validate_selection(result, minimum_candidates=3):
    candidates = result["candidates"]
    names = [item["family"] for item in candidates]
    errors = []
    if len(set(names)) < minimum_candidates:
        errors.append(f"E_FONT_RARITY needs at least {minimum_candidates} unique candidates")
    errors.extend(f"E_FONT_RARITY {item['family']}: {', '.join(item['reasons'])}" for item in candidates if not item["eligible"])
    if not result["selected_families"]:
        errors.append("E_FONT_RARITY needs at least one selected family")
    unknown = sorted(set(result["selected_families"]) - set(names))
    if unknown:
        errors.append("E_FONT_RARITY selected families were not candidates: " + ", ".join(unknown))
    return errors


def face_value(block, name, default=""):
    match = re.search(rf"{name}\s*:\s*(['\"]?)([^;'\"}}]+)\1\s*;?", block, re.IGNORECASE)
    return match.group(2).strip() if match else default


def inline_face(block, font_bytes, records):
    family = face_value(block, "font-family")
    style = face_value(block, "font-style", "normal")
    weight = face_value(block, "font-weight", "400")
    rendered = block
    for match in list(FONT_URL_RE.finditer(block)):
        url = match.group(2)
        data = font_bytes.get(url)
        if data is None or len(data) < 64 or not data.startswith(b"wOF2"):
            raise ValueError(f"E_FONT_ASSET invalid or missing WOFF2: {url}")
        encoded = base64.b64encode(data).decode("ascii")
        rendered = rendered.replace(url, "data:font/woff2;base64," + encoded)
        records.append({"family": family, "style": style, "weight": weight, "format": "woff2", "source_url": url, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    return rendered


def inline_font_css(css, font_bytes):
    records = []
    rendered = css
    faces = FACE_RE.findall(css)
    if not faces:
        raise ValueError("E_FONT_ASSET CSS contains no @font-face blocks")
    for face in faces:
        rendered = rendered.replace(face, inline_face(face, font_bytes, records), 1)
    if not records or "https://fonts.gstatic.com/" in rendered:
        raise ValueError("E_FONT_ASSET CSS did not become self-contained")
    return rendered, records
