"""Document-level rules for extraction YAML.

Every rule here works on already-parsed data, so the same checks run
whether the document arrived from a file, from standard input, or from a
test fixture.
"""
from __future__ import annotations

from extraction_schema import (
    CONFIDENCE_VALUES,
    EVIDENCE_BOUNDARY_KEYS,
    REQUIRED_TOP_LEVEL,
    SOURCE_BUCKETS,
    SOURCE_INVENTORY_KEYS,
    is_text,
    path_join,
)
from font_rules import DEFAULT_MIN_PERCENTILE, check_font_families


def check_text_form(text, errors):
    """Reject fenced or tab indented output before parsing matters."""
    if "```" in text:
        errors.append("Output contains markdown code fences; return raw YAML only.")
    if "\t" in text:
        errors.append("Output contains tab characters; use spaces for indentation.")


def resolve_floor(data, floor, errors):
    """Return the floor to enforce, raised by meta.rarity_floor when recorded."""
    meta = data.get("meta")
    recorded = meta.get("rarity_floor") if isinstance(meta, dict) else None
    if recorded is None:
        return floor
    usable = isinstance(recorded, (int, float)) and not isinstance(recorded, bool)
    if not usable or not 0.0 <= float(recorded) <= 100.0:
        errors.append("meta.rarity_floor must be a number from 0.0 to 100.0.")
        return floor
    return max(floor, float(recorded))


def order_message(present, expected):
    """Return an order problem that names the first key out of place."""
    head = "Top-level section order must match the schema order exactly"
    for index, (found, wanted) in enumerate(zip(present, expected), start=1):
        if found != wanted:
            return (f"{head}; position {index} holds {found!r} where "
                    f"{wanted!r} belongs.")
    return head + "."


def check_sections(data, errors):
    """Require the canonical sections, in order, with no bare placeholders."""
    missing = [key for key in REQUIRED_TOP_LEVEL if key not in data]
    if missing:
        errors.append("Missing required top-level sections: " + ", ".join(missing))
    extras = [str(key) for key in data if key not in REQUIRED_TOP_LEVEL]
    if extras:
        errors.append("Unexpected top-level sections: " + ", ".join(extras))
    present = [key for key in data if key in REQUIRED_TOP_LEVEL]
    expected = [key for key in REQUIRED_TOP_LEVEL if key in data]
    if present != expected:
        errors.append(order_message(present, expected))
    empty = [key for key in REQUIRED_TOP_LEVEL if key in data and data[key] is None]
    if empty:
        errors.append("Top-level sections must not be bare null placeholders: "
                      + ", ".join(empty))


def check_mapping_lists(mapping, prefix, keys, errors):
    """Require every named key under a mapping to hold a list."""
    if not isinstance(mapping, dict):
        errors.append(f"{prefix} must be a mapping.")
        return
    for key in keys:
        if not isinstance(mapping.get(key), list):
            errors.append(f"{prefix}.{key} must be a list.")


def check_source_analysis(data, errors):
    """Keep observed, inferred, and speculative evidence separated."""
    source_analysis = data.get("source_analysis")
    if not isinstance(source_analysis, dict):
        errors.append("source_analysis must be a mapping.")
        return
    check_mapping_lists(source_analysis, "source_analysis", SOURCE_BUCKETS, errors)
    check_mapping_lists(source_analysis.get("source_inventory"),
                        "source_analysis.source_inventory",
                        SOURCE_INVENTORY_KEYS, errors)
    check_mapping_lists(source_analysis.get("evidence_boundaries"),
                        "source_analysis.evidence_boundaries",
                        EVIDENCE_BOUNDARY_KEYS, errors)


def check_confidence_scores(data, errors):
    """Require a populated confidence_scores section."""
    scores = data.get("confidence_scores")
    if not isinstance(scores, dict) or not scores:
        errors.append("confidence_scores must be a non-empty mapping.")


def check_typography(data, floor, errors):
    """Run the font rules and return the entries found."""
    typography = data.get("typography")
    if not isinstance(typography, dict):
        errors.append("typography must be a mapping.")
        return []
    return check_font_families(typography, floor, errors)


def check_not_applicable(node, path, errors):
    """Require the standard shape wherever a field is marked unusable."""
    if node.get("applicability") != "not_applicable":
        return
    if node.get("confidence") not in CONFIDENCE_VALUES:
        errors.append(f"{path or 'root'} not-applicable object needs a confidence "
                      "of low, medium, or high.")
    if not is_text(node.get("inference_basis")):
        errors.append(f"{path or 'root'} not-applicable object needs a non-empty "
                      "inference_basis.")


def check_shapes(node, path, errors):
    """Walk the document and check confidence and not-applicable shapes."""
    if isinstance(node, dict):
        if "confidence" in node and node["confidence"] not in CONFIDENCE_VALUES:
            errors.append(f"{path_join(path, 'confidence')} must be low, medium, "
                          "or high.")
        check_not_applicable(node, path, errors)
        for key, value in node.items():
            check_shapes(value, path_join(path, str(key)), errors)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            check_shapes(item, f"{path}[{index}]", errors)


def check_root(data, errors):
    """Return True when the parsed document can carry further checks."""
    if data is None:
        errors.append("YAML document is empty.")
        return False
    if not isinstance(data, dict):
        errors.append("YAML root must be a mapping.")
        return False
    return True


def validate(data, text, floor=DEFAULT_MIN_PERCENTILE):
    """Return every static problem plus the font entries found."""
    errors = []
    check_text_form(text, errors)
    if not check_root(data, errors):
        return errors, []
    check_sections(data, errors)
    check_source_analysis(data, errors)
    check_confidence_scores(data, errors)
    entries = check_typography(data, floor, errors)
    check_shapes(data, "", errors)
    return errors, entries
