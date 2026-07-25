# Example: the failure this skill causes most

Guess removed: that the prose order of the extraction plan is the order the document has to ship in. It is not. The plan works in the order a reader can see things, the file ships in schema order, and step 9 of the plan exists to reorder the sections before validation.

## The user says

> why does my file fail when every section is there

## The reply

Because top level order is part of the schema. The validator names the position and the two keys, so the fix is a move, not a rewrite. Write in whatever order the reference reveals itself, then reorder to references/extraction-schema.yaml order as the last step before validating.

## Command run

```
$ uv run --no-project --with 'PyYAML>=6,<7' python scripts/validate_design_system_yaml.py examples/work/order-fail.yaml
{
  "confidence_markers": 62,
  "errors": [
    "Top-level section order must match the schema order exactly; position 10 holds 'spacing' where 'typography' belongs."
  ],
  "font_entries": 3,
  "live_fonts_checked": true,
  "rarity_floor": 70.0,
  "valid": false,
  "viability_recorded": true
}
exit=1
```

Moving the typography block back above spacing clears it:

```
$ uv run --no-project --with 'PyYAML>=6,<7' python scripts/validate_design_system_yaml.py examples/extract-output.yaml
{
  "confidence_markers": 62,
  "errors": [],
  "font_entries": 3,
  "live_fonts_checked": true,
  "rarity_floor": 70.0,
  "valid": true,
  "viability_recorded": true
}
exit=0
```

## The canonical order

```
$ uv run --no-project --with 'PyYAML>=6,<7' python scripts/schema_tools.py sections
```

Run it and copy the order from the output rather than from memory. The list changes when the schema changes, and the error message always names the position that is wrong.

## Files created

| File                          | Contents                                                                                               |
| ----------------------------- | ------------------------------------------------------------------------------------------------------ |
| examples/work/order-fail.yaml | The valid document with the spacing block moved above typography, kept so the error can be reproduced. |
