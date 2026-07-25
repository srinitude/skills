# Example: pairing veto

Guess removed: that a font set is the list of winners of separate per slot contests. Pairing is a constraint on the whole set, so the highest scoring individual candidate can still be wrong.

## The user says

> use the best fitting rare serifs for display and body

## The reply

Ramsina took display on fit and rarity. Namdhinggo then ranked first for the text slot, and the pairing check vetoed it on role_distinction: it shares Ramsina's skeleton and sits 0.048 away in default leading, so the two roles would read as one face. Epunda Slab, next in the ranking, differs in leading, 1.301 against 1.098, and carries seven weights, so it took the slot and the set passes.

## Commands run

```
$ python3 scripts/rare_google_fonts.py set --brief assets/font-brief.json --output examples/work/set.json
exit=0
```

The set command writes the record to the file and keeps stdout empty. Reading it back:

```
$ python3 -c "import json;d=json.load(open('examples/work/set.json'));print([c['family'] for c in d['chosen']]);print([(v['family'],v['failed_dimensions']) for v in d['vetoes']]);print(d['pairing']['passes'])"
['Ramsina', 'Epunda Slab']
[('Namdhinggo', ['role_distinction'])]
True
exit=0
```

The validator enforces the same rule on a finished document. This file swaps the text face back to the vetoed candidate:

```
$ uv run --no-project --with 'PyYAML>=6,<7' python scripts/validate_design_system_yaml.py examples/work/pairing-fail.yaml
{
  "confidence_markers": 62,
  "errors": [
    "typography.font_families pairing fails on role_distinction: Ramsina and Namdhinggo share a skeleton and match on width, vertical proportion, and stroke, so the display and text roles read as one face"
  ],
  "font_entries": 3,
  "live_fonts_checked": true,
  "rarity_floor": 70.0,
  "valid": false,
  "viability_recorded": true
}
exit=1
```

The fix is the next candidate, not a louder claim. Restoring Epunda Slab as typography.font_families.supporting clears it:

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

## The seven pairing dimensions

| Dimension             | Fails when                                                                |
| --------------------- | ------------------------------------------------------------------------- |
| skeleton_relationship | The set mixes skeletons that have no stated relationship.                 |
| vertical_proportion   | Default leading differs by more than 0.35 between roles.                  |
| stroke_modulation     | Reported thickness differs by more than 3 steps.                          |
| width_compatibility   | Reported width class differs by more than 2.5 steps.                      |
| weight_capacity       | The text face cannot span 300 weight units, so hierarchy has to be faked. |
| optical_color         | Two faces land at the same optical density and the page flattens.         |
| role_distinction      | Two faces are too close to tell apart in their separate roles.            |

Both directions are failures. Two faces that clash fail on the metric dimensions, two faces that cannot be told apart fail on role_distinction, and either way the reason is named in the report.

## Files created

| File                            | Contents                                                                                       |
| ------------------------------- | ---------------------------------------------------------------------------------------------- |
| examples/work/pairing-fail.yaml | The document with the vetoed text face restored, kept so the failing report can be reproduced. |
| examples/work/set.json          | The decision record: chosen set, vetoes with failed dimensions, per dimension pairing status.  |
