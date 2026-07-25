"""Deterministic filters and ranking over a live font catalog snapshot.

Criteria map one to one onto fields present in the live feed, so the same
snapshot and the same criteria always return the same ordered list. Results
sort by rarity percentile descending, then by family name, so ties never
depend on feed order.
"""
from __future__ import annotations

DEFAULT_MIN_PERCENTILE = 70.0
DEFAULT_LIMIT = 10

CRITERIA_KEYS = (
    "category",
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


def select(catalog, criteria):
    """Return the ranked family records that satisfy the criteria."""
    kept = [item for item in catalog["families"] if matches(item, criteria)]
    kept.sort(key=lambda item: (-item["rarity_percentile"], item["family"]))
    limit = criteria["limit"]
    return kept[:limit] if isinstance(limit, int) and limit > 0 else kept
