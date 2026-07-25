# Example: the viability gate

Guess removed: that a validating document is a working design system. This run renders the system, screenshots it, looks at the screenshot, and fails it. Then it fixes the tokens and passes.

## The user says

> prove the extracted system actually works before you tell me it is done

## The reply

I generated a standalone page from the design system file, screenshotted it, and judged eight criteria by looking at the image. Pass one failed legibility and hierarchy for reasons visible in the picture. I revised the type scale, regenerated, screenshotted again, and pass two clears all eight. The verdicts are recorded in meta.viability of examples/extract-output.yaml with the observed reason on each line.

## Pass one

```
$ uv run --no-project --with 'PyYAML>=6,<7' python scripts/render_preview.py examples/work/pass1-input.yaml --output examples/work/pass1.html
{
  "dark_mode": false,
  "output": "examples/work/pass1.html",
  "problems": [],
  "token_count": 9
}
exit=0
$ uv run --no-project --with playwright python scripts/screenshot_preview.py examples/work/pass1.html --output examples/work/pass1.png
wrote examples/work/pass1.png
exit=0
```

Looking at examples/work/pass1.png:

| Criterion          | Verdict | Observed                                                                                                                                                                                                                                             |
| ------------------ | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| legibility         | fail    | The document defines no body or caption step, so the page falls back to 1rem for body copy and 0.85rem for nav, table headers, form labels, and footer. Those fall to about 13px, below the 16px floor the document's own accessibility note states. |
| contrast           | pass    | Ink 141210 on paper f6f2ea, about 15.6 to 1, and the filled button inverts the same pair.                                                                                                                                                            |
| hierarchy          | fail    | Heading level four renders smaller than the body paragraph next to it, so a heading reads as fine print. Every step below the 64px display size was derived by calculation instead of declared.                                                      |
| font_pairing       | pass    | The Ramsina headline and the Epunda Slab body copy stay apart in leading and stroke weight.                                                                                                                                                          |
| spacing_rhythm     | pass    | The 16px base drives even gaps between header, hero, sections, and footer.                                                                                                                                                                           |
| color_harmony      | pass    | Two warm values only, one for surface and one for text and rules.                                                                                                                                                                                    |
| state_distinction  | pass    | Filled, outlined, and disabled buttons are distinct in the capture.                                                                                                                                                                                  |
| reference_fidelity | pass    | The headline keeps the wedge terminals and the thick to thin transition of the crop.                                                                                                                                                                 |

## The token revision

Two failures, one cause: the type scale shipped a single step. I added five declared steps and the emphasis weight the text face actually ships.

```
    heading_2:
      value: '40px'
    heading_3:
      value: '28px'
    heading_4:
      value: '22px'
    body_1:
      value: '17px'
    caption:
      value: '16px'
```

Each new step carries its own family, line_height, weight, visual_grounding, confidence, and inference_basis, as the schema requires. heading_4 sits at 22px specifically so a heading can never render below body copy again, and caption holds at 16px rather than dropping under the stated floor. The renderer now reads the four largest declared steps as the heading roles instead of deriving them from the display size.

## Pass two

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

Looking at examples/work/pass2.png:

| Criterion          | Verdict | Observed                                                                                                                                                           |
| ------------------ | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| legibility         | pass    | Body copy sets at 17px in Epunda Slab with open counters and no fallback face, and the smallest text on the page holds at 16px.                                    |
| contrast           | pass    | Unchanged from pass one, about 15.6 to 1 for body copy.                                                                                                            |
| hierarchy          | pass    | The steps 64, 40, 28, 22, 17, and 16 are each visibly apart, and heading level four now sits above body copy.                                                      |
| font_pairing       | pass    | Leading 1.05 against 1.55 and a clear weight difference keep display and text from reading as one face.                                                            |
| spacing_rhythm     | pass    | The 16, 32, 64, and 96 steps carry the page down evenly.                                                                                                           |
| color_harmony      | pass    | Paper for surface, ink for text, rules, and the filled button, with no third hue needed.                                                                           |
| state_distinction  | pass    | Filled, outlined, and disabled are distinct, and the focus ring is a 3px offset outline. Hover cannot appear in a still capture, so it was read in the stylesheet. |
| reference_fidelity | pass    | The 64px headline reads as the same editorial voice as the crop.                                                                                                   |

Verdict: pass, at iteration 2 of a cap of 3. Recorded in meta.viability with rendered_file, screenshot_file, iterations, verdict, and the eight criteria lines.

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

## Files created

| File                           | Contents                                                                                |
| ------------------------------ | --------------------------------------------------------------------------------------- |
| examples/work/pass1-input.yaml | The pre revision document, one type step and one weight, kept so pass one can be rerun. |
| examples/work/pass1.html       | The page generated from the pre revision document, 9 tokens.                            |
| examples/work/pass1.png        | The full page screenshot that failed legibility and hierarchy.                          |
| examples/work/pass2.html       | The page generated after the type scale revision, 15 tokens.                            |
| examples/work/pass2.png        | The full page screenshot that passed all eight criteria.                                |
| examples/extract-output.yaml   | The finished document, including the meta.viability record above.                       |

## If the cap runs out

Three iterations is the limit. On a third failing judgment, stop, report the failing criteria with the observed reason, and do not claim the extraction is complete. A reported failure is a result. A silent pass is not.
