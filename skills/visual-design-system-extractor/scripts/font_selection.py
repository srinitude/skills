"""Deterministic filters and ranking over a live font catalog snapshot.

Criteria map one to one onto fields present in the live feed, so the same
snapshot and the same criteria always return the same ordered list.

Ranking runs fit first. `select` applies the plain feed filters and orders
by rarity alone. `rank` scores every survivor for fit and legibility,
drops the ones that fail either bar, and orders by fit band first, so
rarity only breaks a tie between candidates that already fit. `choose_set`
then fills the roles of one design system in order and lets the set level
pairing check veto a winner, which forces the next candidate.
"""
from __future__ import annotations

import font_fit
import font_pairing

DEFAULT_MIN_PERCENTILE = 70.0
DEFAULT_LIMIT = 10

CRITERIA_KEYS = (
    "category",
    "skeleton",
    "width_class",
    "weights",
    "italic",
    "scripts",
    "role",
    "min_fit",
    "min_legibility",
    "allow_common",
    "common_reason",
    "subset",
    "search",
    "min_percentile",
    "variable_only",
    "added_after",
    "exclude_noto",
    "limit",
)


def default_criteria():
    """Return the criteria used when the caller sets nothing."""
    return {
        "category": None,
        "skeleton": None,
        "width_class": None,
        "weights": [],
        "italic": False,
        "scripts": ["latin"],
        "role": None,
        "min_fit": font_fit.DEFAULT_MIN_FIT,
        "min_legibility": None,
        "allow_common": False,
        "common_reason": None,
        "subset": None,
        "search": None,
        "min_percentile": DEFAULT_MIN_PERCENTILE,
        "variable_only": False,
        "added_after": None,
        "exclude_noto": True,
        "limit": DEFAULT_LIMIT,
    }


def build_criteria(**overrides):
    """Return default criteria updated with known overrides only."""
    unknown = sorted(set(overrides) - set(CRITERIA_KEYS))
    if unknown:
        raise ValueError(f"unknown criteria: {', '.join(unknown)}")
    criteria = default_criteria()
    criteria.update({key: value for key, value in overrides.items() if value is not None})
    if criteria["allow_common"] and not criteria["common_reason"]:
        raise ValueError("allow_common needs common_reason: name the visual "
                         "evidence that makes the common face the true fit")
    return criteria


def matches_text(item, criteria):
    """Return True when category, subset, and search terms all match."""
    category = criteria["category"]
    if category and item["category"].casefold() != category.casefold():
        return False
    subset = criteria["subset"]
    if subset and subset.casefold() not in [name.casefold() for name in item["subsets"]]:
        return False
    search = criteria["search"]
    return not search or search.casefold() in item["family"].casefold()


def matches_shape(item, criteria):
    """Return True when rarity, axes, date, and Noto rules all pass."""
    if item["rarity_percentile"] < criteria["min_percentile"]:
        return False
    if criteria["variable_only"] and not item["variable"]:
        return False
    if criteria["added_after"] and item["date_added"] <= criteria["added_after"]:
        return False
    return not (criteria["exclude_noto"] and item["is_noto"])


def matches(item, criteria):
    """Return True when a family record satisfies every criterion."""
    return matches_text(item, criteria) and matches_shape(item, criteria)


def rank_of(item):
    """Return the popularity rank as a sortable number."""
    rank = item.get("popularity_rank")
    return rank if isinstance(rank, int) else 0


def select(catalog, criteria):
    """Return the ranked family records that satisfy the criteria."""
    kept = [item for item in catalog["families"] if matches(item, criteria)]
    kept.sort(key=lambda item: (-item["rarity_percentile"], -rank_of(item),
                                item["family"]))
    limit = criteria["limit"]
    return kept[:limit] if isinstance(limit, int) and limit > 0 else kept


def resolve_role(criteria):
    """Return the role the candidate must play in the set."""
    if criteria.get("role"):
        return criteria["role"]
    category = (criteria.get("category") or "").casefold()
    return "display" if category in font_fit.DISPLAY_CATEGORIES else "text"


def fit_target(criteria):
    """Return the fit target built from the criteria."""
    return font_fit.target(
        skeleton=criteria.get("skeleton"),
        width_class=criteria.get("width_class"),
        weights=criteria.get("weights") or [],
        italic=criteria.get("italic") or False,
        scripts=criteria.get("scripts") or ["latin"],
        role=resolve_role(criteria),
        min_fit=criteria.get("min_fit"),
    )


def scored(catalog, criteria):
    """Return every family that clears the base filters, with its fit verdict."""
    wanted = fit_target(criteria)
    rows = []
    for item in select(catalog, dict(criteria, limit=None)):
        row = dict(item)
        row["fit"] = font_fit.score(item, wanted, criteria.get("min_legibility"))
        rows.append(row)
    return rows


def common_block(row, criteria):
    """Return the reason a common default is excluded, or an empty string."""
    if row["fit"]["common_default"] and not criteria.get("allow_common"):
        return ("an overexposed interface default; pass allow_common with a "
                "stated reason when it truly is the closest match")
    return ""


def sort_key(row):
    """Return the fit first, rarity second ordering key."""
    return (-row["fit"]["fit_band"], -row["rarity_percentile"], -rank_of(row),
            row["family"])


def rank(catalog, criteria):
    """Return candidates that clear fit and legibility, rarest tie broken first."""
    kept = [row for row in scored(catalog, criteria)
            if row["fit"]["passes"] and not common_block(row, criteria)]
    kept.sort(key=sort_key)
    limit = criteria.get("limit")
    return kept[:limit] if isinstance(limit, int) and limit > 0 else kept


def rejected(catalog, criteria):
    """Return the candidates dropped by the fit bars, each with its reason."""
    dropped = []
    for row in scored(catalog, criteria):
        reason = common_block(row, criteria) or row["fit"]["reject_reason"]
        if reason:
            dropped.append(dict(row, reject_reason=reason))
    dropped.sort(key=sort_key)
    return dropped


def try_role(catalog, brief, members, vetoes):
    """Return the first candidate for one role that pairs with the set."""
    taken = {member["record"]["family"] for member in members}
    for row in rank(catalog, brief["criteria"]):
        if row["family"] in taken:
            continue
        trial = members + [{"role": brief["role"], "record": row}]
        verdict = font_pairing.check_set(trial)
        if verdict["passes"]:
            return row
        vetoes.append({"role": brief["role"], "family": row["family"],
                       "fit_score": row["fit"]["fit_score"],
                       "failed_dimensions": verdict["failed_dimensions"],
                       "reasons": [item["reason"] for item in verdict["failures"]]})
    return None


def choose_set(catalog, briefs):
    """Return one complete font set where every face pairs with the others."""
    members, vetoes, unfilled = [], [], []
    for brief in briefs:
        row = try_role(catalog, brief, members, vetoes)
        if row is None:
            unfilled.append({"role": brief["role"],
                             "reason": "no candidate cleared fit, legibility, "
                                       "and pairing for this role"})
            continue
        members.append({"role": brief["role"], "record": row})
    chosen = [{"role": member["role"], "family": member["record"]["family"],
               "fit": member["record"]["fit"],
               "rarity_percentile": member["record"]["rarity_percentile"]}
              for member in members]
    return {"chosen": chosen, "vetoes": vetoes, "unfilled": unfilled,
            "pairing": font_pairing.check_set(members)}
