"""Font rules for extraction YAML.

Two rules govern every typeface an extraction names. It must be a Google
Fonts family whose rarity was measured against the live catalog at the
time of the run, and it must fit the reference well enough to read at the
sizes the document uses. Fit and legibility come first: each entry records
its fit score and its legibility score, and rarity only settles a tie
between faces that already clear both bars. The faces the system uses are
also checked as a set, so a pair that clashes or a pair too similar to
tell apart fails with the failing dimension named.

An overexposed default is rejected unless the entry records
common_face_reason, which must name the visual evidence that makes the
common face the true match rather than a convenient one.
"""
from __future__ import annotations

import font_fit
import font_pairing
from extraction_schema import CONFIDENCE_VALUES, FONT_RULES, is_string_list, is_text

FEED_URL = FONT_RULES["feed_url"]
DEFAULT_MIN_PERCENTILE = float(FONT_RULES["min_rarity_percentile"])
COMMON_UI_FAMILIES = {name.casefold() for name in FONT_RULES["rejected_families"]}
BASE_FIELDS = tuple(FONT_RULES["base_fields"])
ENTRY_FIELDS = tuple(FONT_RULES["entry_fields"])
CANDIDATE_FIELDS = tuple(FONT_RULES["candidate_fields"])
TEXT_FIELDS = tuple(FONT_RULES["text_fields"])
LIST_FIELDS = tuple(FONT_RULES["list_fields"])
RARITY_INTS = tuple(FONT_RULES["rarity_integer_fields"])
RARITY_TEXT = tuple(FONT_RULES["rarity_text_fields"])


def required_fields(is_candidate):
    """Return every field an entry must carry."""
    fields = BASE_FIELDS + ENTRY_FIELDS
    return fields + CANDIDATE_FIELDS if is_candidate else fields


def collect_entries(font_families):
    """Return every selected family entry. Observed families are excluded.

    observed_or_implied records what the reference shows, which may be a
    licensed or custom face. Only families the system selects for use are
    bound by the Google Fonts rarity rule.
    """
    entries = []
    for key in ("primary", "supporting"):
        value = font_families.get(key)
        if isinstance(value, dict) and "family" in value:
            entries.append((f"typography.font_families.{key}", value, False))
    items = font_families.get("rare_unique_candidates")
    if isinstance(items, list):
        entries.extend(index_entries("rare_unique_candidates", items))
    return entries


def index_entries(name, items):
    """Return path and mapping tuples for one list of font entries."""
    base = f"typography.font_families.{name}"
    return [(f"{base}[{index}]", item, True)
            for index, item in enumerate(items) if isinstance(item, dict)]


def check_presence(path, entry, is_candidate, errors):
    """Record a problem for each required field the entry omits."""
    for field in required_fields(is_candidate):
        if field not in entry:
            errors.append(f"{path} missing required field: {field}")


def check_types(path, entry, errors):
    """Record a problem for each present field holding the wrong shape."""
    for field in TEXT_FIELDS:
        if field in entry and not is_text(entry[field]):
            errors.append(f"{path}.{field} must be a non-empty string.")
    for field in LIST_FIELDS:
        if field in entry and not is_string_list(entry[field]):
            errors.append(f"{path}.{field} must be a non-empty list of strings.")
    if "confidence" in entry and entry["confidence"] not in CONFIDENCE_VALUES:
        errors.append(f"{path}.confidence must be low, medium, or high.")


def has_common_exception(entry):
    """Return True when the entry states why a common face is the true fit."""
    return is_text(entry.get("common_face_reason"))


def check_google_flag(path, entry, errors):
    """Require the family to be declared and named as a Google Fonts family."""
    if entry.get("google_fonts_family") is not True:
        errors.append(f"{path}.google_fonts_family must be true; only Google Fonts "
                      "families verified against the live catalog are allowed.")
    family = entry.get("family")
    if not is_text(family) or not font_fit.is_common(family):
        return
    if not has_common_exception(entry):
        errors.append(f"{path}.family is an overexposed default. Record "
                      "common_face_reason naming the visual evidence that makes "
                      "it the true fit, or select a rarer family that fits.")


def role_of(entry):
    """Return the role the entry plays, defaulting to text."""
    role = str(entry.get("set_role") or entry.get("role") or "").strip().casefold()
    return role if role in font_fit.ROLE_FLOORS else "text"


def check_fit(path, entry, errors):
    """Require recorded fit and legibility scores that clear their bars."""
    fit = entry.get("fit")
    if not isinstance(fit, dict):
        errors.append(f"{path}.fit must record fit_score, legibility_score, and "
                      "evidence, since fit ranks ahead of rarity.")
        return
    if not is_text(fit.get("evidence")):
        errors.append(f"{path}.fit.evidence must name the visual traits matched.")
    check_bar(path, fit, "fit_score", font_fit.DEFAULT_MIN_FIT, errors)
    check_bar(path, fit, "legibility_score", font_fit.floor_for(role_of(entry)),
              errors)


def check_bar(path, fit, field, bar, errors):
    """Require one recorded score to be a number at or above its bar."""
    value = fit.get(field)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        errors.append(f"{path}.fit.{field} must be a number from 0.0 to 1.0.")
        return
    if value < bar:
        errors.append(f"{path}.fit.{field} is {value}; the bar is {bar}. Rarity "
                      "cannot buy a place past this bar.")


def check_rarity(path, entry, floor, errors):
    """Require a complete rarity record that clears the popularity floor."""
    if has_common_exception(entry):
        return
    rarity = entry.get("rarity")
    if not isinstance(rarity, dict):
        errors.append(f"{path}.rarity must be a mapping recorded from the live catalog.")
        return
    for field in RARITY_INTS:
        if not isinstance(rarity.get(field), int):
            errors.append(f"{path}.rarity.{field} must be an integer from the live feed.")
    for field in RARITY_TEXT:
        if not is_text(rarity.get(field)):
            errors.append(f"{path}.rarity.{field} must be a non-empty string.")
    if rarity.get("source") != FEED_URL:
        errors.append(f"{path}.rarity.source must be {FEED_URL}.")
    check_percentile(path, rarity, floor, errors)


def check_percentile(path, rarity, floor, errors):
    """Require a numeric percentile at or above the floor."""
    percentile = rarity.get("rarity_percentile")
    if not isinstance(percentile, (int, float)) or isinstance(percentile, bool):
        errors.append(f"{path}.rarity.rarity_percentile must be a number.")
        return
    if percentile < floor:
        errors.append(f"{path}.rarity.rarity_percentile is {percentile}; the floor "
                      f"is {floor}. Pick a family the live catalog ranks as rarer.")


def check_entry(path, entry, is_candidate, floor, errors):
    """Run every static font rule against one entry."""
    check_presence(path, entry, is_candidate, errors)
    check_types(path, entry, errors)
    check_google_flag(path, entry, errors)
    check_fit(path, entry, errors)
    check_rarity(path, entry, floor, errors)


def check_font_families(typography, floor, errors):
    """Run the font rules across the whole typography section."""
    font_families = typography.get("font_families")
    if not isinstance(font_families, dict):
        errors.append("typography.font_families must be a mapping.")
        return []
    candidates = font_families.get("rare_unique_candidates")
    if not isinstance(candidates, list) or not candidates:
        errors.append("typography.font_families.rare_unique_candidates must be a "
                      "non-empty list.")
    entries = collect_entries(font_families)
    for path, entry, is_candidate in entries:
        check_entry(path, entry, is_candidate, floor, errors)
    return entries


def verify_live(entries, catalog, floor, errors):
    """Compare each recorded family and rank against the live catalog."""
    from google_fonts_api import find

    for path, entry, _ in entries:
        family = entry.get("family")
        if not is_text(family):
            continue
        item = find(catalog, family)
        if item is None:
            errors.append(f"{path}.family {family!r} is absent from the live catalog.")
            continue
        compare_live(path, entry, item, floor, errors)


def set_members(font_families, catalog):
    """Return the faces the system uses, with their live records."""
    from google_fonts_api import find

    members = []
    for key, fallback in (("primary", "display"), ("supporting", "text")):
        entry = font_families.get(key)
        if not isinstance(entry, dict) or not is_text(entry.get("family")):
            continue
        item = find(catalog, entry["family"])
        if item is not None:
            members.append({"role": entry.get("set_role") or fallback,
                            "record": item})
    return members


def verify_pairing(font_families, catalog, errors):
    """Require the faces the system uses to work together as a set."""
    members = set_members(font_families, catalog)
    if len(members) < 1:
        return None
    verdict = font_pairing.check_set(members)
    for failure in verdict["failures"]:
        errors.append(f"typography.font_families pairing fails on "
                      f"{failure['dimension']}: {failure['reason']}")
    return verdict


def compare_live(path, entry, item, floor, errors):
    """Record drift between one entry and its live catalog record."""
    rarity = entry.get("rarity") if isinstance(entry.get("rarity"), dict) else {}
    if rarity.get("popularity_rank") != item["popularity_rank"]:
        errors.append(f"{path}.rarity.popularity_rank is stale; the live catalog "
                      f"reports {item['popularity_rank']}.")
    if item["rarity_percentile"] < floor and not has_common_exception(entry):
        errors.append(f"{path}.family {item['family']!r} now sits at percentile "
                      f"{item['rarity_percentile']}, below the {floor} floor.")
