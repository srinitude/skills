# Example: validate

Guess removed: that the validator reports only true or false. It returns seven keys, and each one is a claim the run has to earn.

## The user says

> validate this extraction

## The reply

Seven keys come back. valid is the gate, errors names every problem with the path that owns it, rarity_floor echoes the binding floor from meta.rarity_floor, live_fonts_checked says whether the catalog was reachable, confidence_markers counts the confidence and inference_basis pairs, font_entries counts the checked font records, and viability_recorded says whether the rendered page was judged.

## Command run

```
$ mise run validate-design-system-yaml examples/extract-output.yaml
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

## The failure that catches most runs

A document that validates on shape and has never been rendered:

```
$ mise run validate-design-system-yaml examples/work/no-viability.yaml
{
  "confidence_markers": 62,
  "errors": [
    "meta.viability must record the judgment of the rendered preview: render, screenshot, look, then record a verdict per criterion. Schema validation alone does not prove the system works."
  ],
  "font_entries": 3,
  "live_fonts_checked": true,
  "rarity_floor": 70.0,
  "valid": false,
  "viability_recorded": false
}
exit=1
```

examples/work/no-viability.yaml is the finished document with the meta.viability block removed, kept so this report stays reproducible. The fix is to render, screenshot, look, and record, not to add the key with a guessed verdict.

## Exit codes

| Code | Meaning                                                     |
| ---- | ----------------------------------------------------------- |
| 0    | valid is true and errors is empty.                          |
| 1    | At least one error. Read errors, fix the named path, rerun. |
| 2    | Bad usage or an unreadable file.                            |

## Files created

Resource gate: run `mise run validate` before using package files named here.

| File                            | Contents                                                                                       |
| ------------------------------- | ---------------------------------------------------------------------------------------------- |
| examples/work/no-viability.yaml | The valid document with meta.viability removed, kept so the failing report above can be rerun. |
