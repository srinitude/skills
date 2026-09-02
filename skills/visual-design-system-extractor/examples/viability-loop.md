# Example: the viability gate

Guess removed: that a validating document is a working design system. This run renders the system, captures the full page, and judges the pixels before reporting success.

## The user says

> prove the extracted system actually works before you tell me it is done

## The reply

Resource gate: run `mise run validate` before using package files named here.

I generated a standalone page from the validated design-system file, captured the full page, and sent the current pixels to the `computer-user` visual owner. The image passed all eight criteria on the first verified render. The observed reasons are recorded in `meta.viability` of `examples/extract-output.yaml`.

## Render and capture

```text
$ uv run --no-project --with 'PyYAML>=6,<7' python \
    `mise run render-preview` examples/extract-output.yaml \
    --output examples/work/pass2.html
{
  "dark_mode": false,
  "output": "examples/work/pass2.html",
  "problems": [],
  "token_count": 15
}
exit=0
$ uv run --no-project --with playwright python \
    `mise run screenshot-preview` examples/work/pass2.html \
    --output examples/work/pass2.png
wrote examples/work/pass2.png
exit=0
```

## Visual verdict

The reviewed PNG has SHA-256 `908631a82e345d2e6d5e5b5a20c0627c6b152a122d1d737c294debb5034eac64`.

| Criterion          | Verdict | Observed                                                                                                                                       |
| ------------------ | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| legibility         | pass    | Wittgenstein remains readable from the 64px hero through card titles, and Parastoo stays readable in body, labels, tables, and footer.         |
| contrast           | pass    | Near-black type and controls remain clear on warm cream, with outlined and disabled states visibly separate.                                   |
| hierarchy          | pass    | The 64, 40, 28, 22, 17, and 16px levels create an unambiguous order.                                                                           |
| font_pairing       | pass    | Wittgenstein supplies expressive display forms while Parastoo supplies calmer reading text; their roles stay distinct and consistent.          |
| spacing_rhythm     | pass    | Stable margins, shared left edges, even component padding, and larger section breaks avoid crowding and broken alignment.                      |
| color_harmony      | pass    | Warm cream, near-black, pale cool-gray rules, and neutral disabled gray form one restrained palette.                                           |
| state_distinction  | pass    | Filled primary, outlined secondary, and gray disabled controls are distinct. Hover and focus are not visible and are not inferred.             |
| reference_fidelity | pass    | The display face reads as a clean high-contrast editorial serif; the prior charted, jagged treatment is absent from every displayed component. |

Verdict: pass at iteration 1 of a cap of 3.

```text
$ uv run --no-project --with 'PyYAML>=6,<7' python \
    `mise run validate-design-system-yaml` examples/extract-output.yaml
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

Resource gate: run `mise run validate` before using package files named here.

| File                         | Contents                                                             |
| ---------------------------- | -------------------------------------------------------------------- |
| examples/work/pass2.html     | The standalone page generated from the validated document.           |
| examples/work/pass2.png      | The current full-page screenshot that passed all eight criteria.     |
| examples/extract-output.yaml | The validated document with the exact rendered and screenshot paths. |

## If a render fails

Change the tokens that caused the observed failure, rerender, recapture, and judge again. Three iterations is the limit. On a third failure, report the failing criteria and do not claim completion.
