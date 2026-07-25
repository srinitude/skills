"""Style metrics read from one live feed entry.

The feed carries a `fonts` mapping keyed by weight, where a key ending in
`i` is an italic cut, plus optional variable `axes`. Each cut may report
`width`, `thickness`, and `lineHeight` on a small integer or ratio scale.
These helpers turn that into the numbers fit and pairing checks need, so
no other module parses feed shapes.
"""
from __future__ import annotations


def cuts(entry):
    """Return the weight keyed cut mapping, or an empty mapping."""
    found = entry.get("fonts")
    return found if isinstance(found, dict) else {}


def weights_of(entry):
    """Return the upright weights the family ships, sorted."""
    found = set()
    for key in cuts(entry):
        digits = str(key).rstrip("i")
        if digits.isdigit():
            found.add(int(digits))
    return sorted(found)


def italic_of(entry):
    """Return True when the family ships an italic or oblique cut."""
    return any(str(key).endswith("i") for key in cuts(entry))


def weight_axis(entry):
    """Return the variable weight axis range, or None."""
    for axis in entry.get("axes") or []:
        if isinstance(axis, dict) and axis.get("tag") == "wght":
            return [int(axis.get("min", 0)), int(axis.get("max", 0))]
    return None


def weight_range(entry):
    """Return the widest weight span the family can render."""
    axis = weight_axis(entry)
    if axis:
        return axis
    weights = weights_of(entry)
    return [weights[0], weights[-1]] if weights else []


def metric(entry, name):
    """Return the mean of one reported cut metric, or None."""
    values = [cut.get(name) for cut in cuts(entry).values()
              if isinstance(cut, dict) and isinstance(cut.get(name), (int, float))]
    return round(sum(values) / len(values), 3) if values else None


def style_record(entry):
    """Return every style metric this skill reads from one feed entry."""
    return {
        "stroke": entry.get("stroke") or "",
        "primary_script": entry.get("primaryScript") or "",
        "weights": weights_of(entry),
        "weight_range": weight_range(entry),
        "italic": italic_of(entry),
        "line_height": metric(entry, "lineHeight"),
        "width_class": metric(entry, "width"),
        "thickness": metric(entry, "thickness"),
    }
