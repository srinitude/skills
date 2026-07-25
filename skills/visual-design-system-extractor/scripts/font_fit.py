"""Fit and legibility scoring for one catalog record against one brief.

Fit comes first and rarity never buys a place. A record is scored on the
traits the live feed reports: skeleton, width class, available weights,
italic availability, and script subsets. Legibility is scored separately
and carries a hard floor no flag can lower, so a rare face that cannot be
read at text sizes is rejected instead of ranked. Traits the feed does not
report, such as terminals and x-height, are judged by eye and recorded in
the document as visual grounding; this module never guesses them.
"""
from __future__ import annotations

from extraction_schema import FONT_RULES

HARD_FLOOR = 0.5
ROLE_FLOORS = {"text": 0.7, "display": 0.55, "mono": 0.7, "accent": 0.55}
DEFAULT_MIN_FIT = 0.65
DISPLAY_CATEGORIES = {"display", "handwriting"}
TEXT_ROLES = ("text", "mono")
WEIGHT_STEP = 100
COMMON_FAMILIES = {name.casefold() for name in FONT_RULES["rejected_families"]}
TARGET_KEYS = ("skeleton", "width_class", "weights", "italic", "scripts",
               "role", "min_fit")


def target(**overrides):
    """Return one fit target: what the reference asks the typeface to be."""
    unknown = sorted(set(overrides) - set(TARGET_KEYS))
    if unknown:
        raise ValueError(f"unknown target keys: {', '.join(unknown)}")
    wanted = {"skeleton": None, "width_class": None, "weights": [],
              "italic": False, "scripts": ["latin"], "role": "text",
              "min_fit": DEFAULT_MIN_FIT}
    wanted.update({k: v for k, v in overrides.items() if v is not None})
    return wanted


def is_common(family):
    """Return True when the family is an overexposed interface default."""
    return str(family).strip().casefold() in COMMON_FAMILIES


def floor_for(role, requested=None):
    """Return the legibility floor for a role, never below the hard floor."""
    base = ROLE_FLOORS.get(role, ROLE_FLOORS["text"])
    if requested is None:
        return base
    return max(HARD_FLOOR, min(float(requested), 1.0), 0.0) if requested < base else base


def skeleton_score(item, wanted):
    """Return how closely the reported skeleton matches the wanted one."""
    if not wanted:
        return 1.0
    actual = (item.get("stroke") or item.get("category") or "").casefold()
    if actual == str(wanted).casefold():
        return 1.0
    if actual in DISPLAY_CATEGORIES:
        return 0.0
    return 0.15


def width_score(item, wanted):
    """Return closeness on the reported width class, 1 to 10."""
    if wanted is None:
        return 1.0
    actual = item.get("width_class")
    if actual is None:
        return 0.6
    return round(max(0.0, 1.0 - abs(float(actual) - float(wanted)) / 5.0), 3)


def covered_weights(item):
    """Return every weight the family can render, axis range included."""
    weights = set(item.get("weights") or [])
    span = item.get("weight_range") or []
    if len(span) == 2 and span[1] > span[0]:
        low, high = int(span[0]), int(span[1])
        weights.update(range(low - low % WEIGHT_STEP + WEIGHT_STEP, high + 1,
                             WEIGHT_STEP))
        weights.update({low, high})
    return weights


def weight_score(item, wanted):
    """Return the share of needed weights the family can render."""
    if not wanted:
        return 1.0
    have = covered_weights(item)
    hits = sum(1 for weight in wanted if weight in have)
    return round(hits / len(wanted), 3)


def script_score(item, wanted):
    """Return 1.0 only when every needed subset is present."""
    have = {name.casefold() for name in item.get("subsets") or []}
    return 1.0 if all(str(name).casefold() in have for name in wanted or []) else 0.0


def legibility_score(item, role):
    """Return legibility at the sizes the role uses, from feed traits only."""
    score = 1.0
    category = (item.get("category") or "").casefold()
    if category in DISPLAY_CATEGORIES and role in TEXT_ROLES:
        score -= 0.5
    weights = item.get("weights") or []
    if weights and not any(300 <= weight <= 500 for weight in weights):
        score -= 0.25
    if weights and len(weights) < 2 and not item.get("variable"):
        score -= 0.1
    height = item.get("line_height")
    if isinstance(height, (int, float)) and not 1.0 <= height <= 1.9:
        score -= 0.15
    thickness = item.get("thickness")
    if isinstance(thickness, (int, float)) and (thickness <= 2 or thickness >= 8):
        score -= 0.15
    script = item.get("primary_script") or ""
    if script and script != "Latn":
        score -= 0.2
    return round(max(0.0, min(1.0, score)), 3)


def fit_band(score):
    """Return the coarse band used before rarity breaks a tie."""
    return round(int(float(score) * 20) / 20, 2)


def weighted_fit(parts):
    """Return the weighted fit score from its named parts."""
    weights = {"skeleton_score": 0.45, "width_score": 0.15,
               "weight_score": 0.2, "style_score": 0.2}
    total = sum(parts[name] * weight for name, weight in weights.items())
    return round(total * parts["script_score"], 3)


def score(item, wanted, min_legibility=None):
    """Return the full fit verdict for one record against one target."""
    parts = {
        "skeleton_score": skeleton_score(item, wanted["skeleton"]),
        "width_score": width_score(item, wanted["width_class"]),
        "weight_score": weight_score(item, wanted["weights"]),
        "style_score": 1.0 if item.get("italic") or not wanted["italic"] else 0.0,
        "script_score": script_score(item, wanted["scripts"]),
    }
    fit = weighted_fit(parts)
    legible = legibility_score(item, wanted["role"])
    floor = floor_for(wanted["role"], min_legibility)
    verdict = dict(parts)
    verdict.update({"family": item.get("family", ""), "fit_score": fit,
                    "fit_band": fit_band(fit), "legibility_score": legible,
                    "legibility_floor": floor, "role": wanted["role"],
                    "common_default": is_common(item.get("family", "")),
                    "passes": fit >= wanted["min_fit"] and legible >= floor})
    verdict["reject_reason"] = reject_reason(verdict, wanted)
    return verdict


def reject_reason(verdict, wanted):
    """Return the named reason a record failed, or an empty string."""
    if verdict["script_score"] == 0.0:
        return "missing a required script subset"
    if verdict["legibility_score"] < verdict["legibility_floor"]:
        return (f"legibility {verdict['legibility_score']} is below the "
                f"{verdict['role']} floor {verdict['legibility_floor']}")
    if verdict["fit_score"] < wanted["min_fit"]:
        return (f"fit {verdict['fit_score']} is below the minimum "
                f"{wanted['min_fit']}")
    return ""
