"""Validate the closed JSON Schema vocabulary used by variant review records."""
import json
import re
from pathlib import Path

SCHEMA = Path(__file__).resolve().parents[1] / "assets/variant-review.schema.json"
TYPES = {"object": dict, "array": list, "string": str, "integer": int}


def validate(value, schema, path="review"):
    kind = schema.get("type")
    if kind and (not isinstance(value, TYPES[kind]) or kind == "integer" and isinstance(value, bool)):
        raise ValueError(f"{path} must be {kind}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{path} has an invalid value")
    if "minLength" in schema and len(value) < schema["minLength"]:
        raise ValueError(f"{path} must not be empty")
    if "pattern" in schema and not re.fullmatch(schema["pattern"], value):
        raise ValueError(f"{path} has an invalid digest")
    if kind == "object":
        object_fields(value, schema, path)
    if kind == "array":
        if len(value) < schema.get("minItems", 0):
            raise ValueError(f"{path} needs more entries")
        for index, item in enumerate(value):
            validate(item, schema["items"], f"{path}[{index}]")


def object_fields(value, schema, path):
    missing = set(schema.get("required", [])) - set(value)
    if missing:
        raise ValueError(f"{path} is missing {', '.join(sorted(missing))}")
    properties = schema.get("properties", {})
    for key, item in value.items():
        rule = properties.get(key, schema.get("additionalProperties", True))
        if rule is False:
            raise ValueError(f"{path} has unknown field {key}")
        if isinstance(rule, dict):
            validate(item, rule, f"{path}.{key}")


def validate_review(value):
    validate(value, json.loads(SCHEMA.read_text(encoding="utf-8")))
