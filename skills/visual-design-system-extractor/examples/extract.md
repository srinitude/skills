# Example: extract

Guess removed: that a document which validates against the schema is a finished extraction. It is not. The run below only reports success after the rendered page passes every visual criterion.

## The user says

> here is a poster crop, pull the design system out of it

## The reply

I read the crop, wrote the document in schema order, ranked fonts by fit before rarity, checked the set for pairing, then rendered the whole system to a page, screenshotted it, and judged the screenshot. The first render failed legibility and hierarchy, so I revised the type scale and rendered again. The second render passes all eight criteria, so the extraction is complete.

## Commands run

Fonts first, so the type section is not a guess.

```
$ python3 scripts/rare_google_fonts.py set --brief assets/font-brief.json --output examples/work/set.json
exit=0
```

With `--output` the command writes the record to the file and keeps stdout empty. The chosen set, the veto, and the pairing verdict from that file:

```
$ python3 -c "import json;d=json.load(open('examples/work/set.json'));print([c['family'] for c in d['chosen']]);print([(v['family'],v['failed_dimensions']) for v in d['vetoes']]);print(d['pairing']['passes'])"
['Ramsina', 'Epunda Slab']
[('Namdhinggo', ['role_distinction'])]
True
exit=0
```

Validate the document.

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

Render, screenshot, look. The full loop with both passes is in examples/viability-loop.md.

```
$ uv run --no-project --with 'PyYAML>=6,<7' python scripts/render_preview.py examples/extract-output.yaml --output examples/work/pass2.html
{
  "dark_mode": false,
  "output": "examples/work/pass2.html",
  "problems": [],
  "token_count": 15
}
exit=0
$ uv run --no-project --with playwright python scripts/screenshot_preview.py examples/work/pass2.html --output examples/work/pass2.png
wrote examples/work/pass2.png
exit=0
```

## Files created

| File                         | Contents                                                                                                                          |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| examples/extract-output.yaml | The complete document, 496 lines, byte identical to the validated file in this directory. Read it there rather than pasted twice. |
| examples/work/set.json       | The font decision record: chosen set, per role fit scores, vetoes, pairing dimensions, retrieved_at.                              |
| examples/work/pass2.html     | The standalone page that applies every token across the required components.                                                      |
| examples/work/pass2.png      | The full page screenshot that was judged.                                                                                         |

The verdicts recorded in meta.viability of examples/extract-output.yaml are the ones written after looking at examples/work/pass2.png, one line per criterion with the observed reason.
