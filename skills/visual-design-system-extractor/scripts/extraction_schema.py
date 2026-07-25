"""Load the canonical schema contract and expose shared helpers.

The contract lives in references/extraction-schema.yaml. Section order,
confidence labels, evidence buckets, and the font rules all come from that
one file, so a rule changes in one place and every check follows.
"""
from __future__ import annotations

from pathlib import Path

import yaml

SCHEMA_FILE = Path(__file__).resolve().parents[1] / "references" / "extraction-schema.yaml"


def load_schema(path=SCHEMA_FILE):
    """Return the parsed schema contract."""
    return yaml.safe_load(path.read_text(encoding="utf-8"))


SCHEMA = load_schema()

REQUIRED_TOP_LEVEL = list(SCHEMA["top_level_sections"])
CONFIDENCE_VALUES = set(SCHEMA["confidence_values"])
SOURCE_BUCKETS = tuple(SCHEMA["source_analysis"]["buckets"])
SOURCE_INVENTORY_KEYS = tuple(SCHEMA["source_analysis"]["source_inventory_keys"])
EVIDENCE_BOUNDARY_KEYS = tuple(SCHEMA["source_analysis"]["evidence_boundary_keys"])
FONT_RULES = SCHEMA["font_rules"]


def path_join(parent, key):
    """Return a dotted path for an error message."""
    return f"{parent}.{key}" if parent else key


def is_text(value):
    """Return True for a non-empty string."""
    return isinstance(value, str) and bool(value.strip())


def is_string_list(value):
    """Return True for a non-empty list of non-empty strings."""
    return isinstance(value, list) and bool(value) and all(is_text(item) for item in value)


def count_key(node, target):
    """Return how many times a key appears anywhere in the document."""
    if isinstance(node, dict):
        own = sum(1 for key in node if key == target)
        return own + sum(count_key(value, target) for value in node.values())
    if isinstance(node, list):
        return sum(count_key(item, target) for item in node)
    return 0
