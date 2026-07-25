"""Set level pairing checks for the typefaces of one design system.

Pairing is a property of the whole set, so this module scores the display,
text, mono, and accent faces together. Two faces fail for opposite
reasons: they clash, or they sit so close that no reader can tell the
roles apart. Both verdicts name the dimension that failed. The live feed
reports skeleton, line height, width class, stroke thickness, and the
available weights, so those stand in for the proportions a designer reads
by eye; a dimension the feed cannot report is left to the visual check
rather than guessed here.
"""
from __future__ import annotations

from itertools import combinations

DIMENSIONS = ("skeleton_relationship", "vertical_proportion", "stroke_modulation",
              "width_compatibility", "weight_capacity", "optical_color",
              "role_distinction")
LOUD_CATEGORIES = {"display", "handwriting"}
TEXT_ROLES = {"text", "mono"}
LIMITS = {"line_height": 0.35, "thickness": 3.0, "width_class": 2.5}
NEAR_LIMITS = {"line_height": 0.05, "thickness": 1.0, "width_class": 0.5}
TEXT_WEIGHT_SPAN = 300


def name_of(member):
    """Return the family name of one set member."""
    return member["record"].get("family", "")


def skeleton_of(member):
    """Return the reported skeleton, lowercased."""
    record = member["record"]
    return (record.get("stroke") or record.get("category") or "").casefold()


def is_loud(member):
    """Return True when the face is a display or handwriting face."""
    return (member["record"].get("category") or "").casefold() in LOUD_CATEGORIES


def gap_of(one, two, key):
    """Return the absolute distance on one metric, or None when unknown."""
    left, right = one["record"].get(key), two["record"].get(key)
    if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
        return None
    return round(abs(float(left) - float(right)), 3)


def metric_gaps(members, key):
    """Return every known pairwise gap on one metric."""
    found = []
    for one, two in combinations(members, 2):
        gap = gap_of(one, two, key)
        if gap is not None:
            found.append((one, two, gap))
    return found


def check_metric(members, key, label):
    """Return one reason per pair that exceeds the metric limit."""
    limit = LIMITS[key]
    return [f"{name_of(one)} and {name_of(two)} differ by {gap} on {label}, "
            f"past the {limit} limit"
            for one, two, gap in metric_gaps(members, key) if gap > limit]


def check_skeleton_relationship(members):
    """Reject two attention faces competing inside one set."""
    loud = [name_of(member) for member in members if is_loud(member)]
    if len(loud) > 1:
        return [f"{' and '.join(loud)} are both attention faces, so neither "
                "can carry a supporting role"]
    return []


def check_vertical_proportion(members):
    """Reject mismatched vertical proportions."""
    return check_metric(members, "line_height", "vertical proportion")


def check_stroke_modulation(members):
    """Reject mismatched contrast and stroke weight."""
    return check_metric(members, "thickness", "stroke modulation")


def check_width_compatibility(members):
    """Reject mismatched widths."""
    return check_metric(members, "width_class", "width class")


def span_of(member):
    """Return the weight span the family can render."""
    found = member["record"].get("weight_range") or []
    return int(found[1] - found[0]) if len(found) == 2 else 0


def check_weight_capacity(members):
    """Require every text face to carry the hierarchy on its own weights."""
    reasons = []
    for member in members:
        weights = member["record"].get("weights") or []
        enough = span_of(member) >= TEXT_WEIGHT_SPAN or len(weights) >= 3
        if member["role"] in TEXT_ROLES and not enough:
            reasons.append(f"{name_of(member)} carries {len(weights)} weights "
                           f"spanning {span_of(member)}, too few for hierarchy")
    return reasons


def check_optical_color(members):
    """Require a text weight in every face so page color can be matched."""
    return [f"{name_of(member)} ships no weight between 300 and 500, so its "
            "optical color cannot match the rest of the set"
            for member in members
            if (member["record"].get("weights") or [])
            and not any(300 <= weight <= 500
                        for weight in member["record"]["weights"])]


def near_duplicate(one, two):
    """Return True when two faces are too close to read as separate roles."""
    if skeleton_of(one) != skeleton_of(two):
        return False
    gaps = [(key, gap_of(one, two, key)) for key in NEAR_LIMITS]
    known = [(key, gap) for key, gap in gaps if gap is not None]
    return bool(known) and all(gap <= NEAR_LIMITS[key] for key, gap in known)


def check_role_distinction(members):
    """Reject two faces in different roles that read as the same face."""
    return [f"{name_of(one)} and {name_of(two)} share a skeleton and match on "
            "width, vertical proportion, and stroke, so the "
            f"{one['role']} and {two['role']} roles read as one face"
            for one, two in combinations(members, 2)
            if one["role"] != two["role"] and near_duplicate(one, two)]


CHECKS = {name: globals()[f"check_{name}"] for name in DIMENSIONS}


def check_set(members):
    """Return the set level pairing verdict, one entry per dimension."""
    dimensions = []
    for name in DIMENSIONS:
        reasons = CHECKS[name](members)
        dimensions.append({"dimension": name,
                           "status": "fail" if reasons else "pass",
                           "reason": "; ".join(reasons)})
    failures = [item for item in dimensions if item["status"] == "fail"]
    return {"passes": not failures, "dimensions": dimensions,
            "failures": failures,
            "failed_dimensions": [item["dimension"] for item in failures],
            "members": [{"role": member["role"], "family": name_of(member)}
                        for member in members]}
