# Example: extract

Guess removed: that a document which validates against the schema is a finished extraction. It is not. The run below only reports success after the rendered page passes every visual criterion.

## The user says

> here is a poster crop, pull the design system out of it

## The reply

I read the crop, wrote the document in schema order, ranked fonts by fit before rarity, checked the set for pairing, rendered the whole system, captured the full page, and sent the current pixels to the visual owner. The verified render passes all eight criteria, so the extraction is complete.

## Commands run

Fonts first, so the type section is not a guess.

```
$ mise run font-set -- --brief assets/font-brief.json --output examples/work/set.json
exit=0
```

With `--output` the command writes the record to the file and keeps stdout empty. The chosen set, the veto, and the pairing verdict from that file:

```
$ mise run font-record -- examples/work/set.json
['Wittgenstein', 'Parastoo']
[]
True
exit=0
```

Validate the document.

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

Render, capture, and judge the pixels. The full gate is in examples/viability-loop.md.

```
$ mise run render-preview examples/extract-output.yaml --output examples/work/pass2.html
{
  "dark_mode": false,
  "output": "examples/work/pass2.html",
  "problems": [],
  "token_count": 15
}
exit=0
$ mise run screenshot-preview examples/work/pass2.html --output examples/work/pass2.png
wrote examples/work/pass2.png
exit=0
```

## Files created

Resource gate: run `mise run validate` before using package files named here.

| File                         | Contents                                                                                                                          |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| examples/extract-output.yaml | The complete document, 496 lines, byte identical to the validated file in this directory. Read it there rather than pasted twice. |
| examples/work/set.json       | The font decision record: chosen set, per role fit scores, vetoes, pairing dimensions, retrieved_at.                              |
| examples/work/pass2.html     | The standalone page that applies every token across the required components.                                                      |
| examples/work/pass2.png      | The full page screenshot that was judged.                                                                                         |

The verdicts recorded in meta.viability of examples/extract-output.yaml are the ones written after looking at examples/work/pass2.png, one line per criterion with the observed reason.
