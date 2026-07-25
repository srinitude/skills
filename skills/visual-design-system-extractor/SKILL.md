---
name: visual-design-system-extractor
description: 'Use when reference images, screenshots, moodboards, style frames, brand boards, cinematic stills, product interface shots, or a live site URL must become a production design system, design tokens, art direction, motion rules, or a YAML style specification. Covers reverse engineering visual references into a deterministic YAML contract with graded confidence, evidence boundaries, and typefaces drawn from the live Google Fonts catalog and ranked as rarely used. Not for generating images or for ordinary frontend work where no reference has to be decoded first.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.2.0'
---

# Visual Design System Extractor

Turn visual references into one parser-valid YAML design system whose every claim traces back to something visible, and whose every selected typeface is a Google Fonts family the live catalog ranks as rarely used at the moment of the run.

The gates need a terminal, a YAML parser, and network access to the live font catalog. Run every command from this skill directory, since all paths are relative to it. Commands that parse YAML fetch the parser through `uv`; the font commands need no third-party package, so they run under plain `python3`. The rendering gate needs a browser, which `uv run --no-project --with playwright` supplies. Check the whole package with these five, each of which must exit 0: `python3 -m unittest discover -s scripts/tests -p 'test_*.py'`, `python3 scripts/validate_skill.py .`, `python3 scripts/lint_writing.py .`, `python3 scripts/check_code_rules.py .`, `python3 scripts/check_evals.py .`.

## Which commands does this skill accept?

Interpret a plain request with an attached reference or a URL as `extract`.

| Command             | Result                                                                |
| ------------------- | --------------------------------------------------------------------- |
| `help`              | Show this table and the current schema version.                       |
| `extract <refs>`    | Produce the full YAML design system from the supplied references.     |
| `fonts <brief>`     | Return ranked rare Google Fonts candidates without a full extraction. |
| `preview <file>`    | Render, screenshot, and judge a document without extracting again.    |
| `validate <file>`   | Run the schema and font gates against an existing extraction.         |
| `maintain <change>` | Edit this package under the test-first rules below.                   |

If no reference is attached or reachable, stop and ask for the image, screenshot, moodboard, style frame, or URL. Do not invent a system from a description alone.

## What does each command return?

- `help`: The command table and the schema version, as prose.
- `extract`: The validated YAML document alone: no code fences, no prose before or after, no summary of the references, and no document that failed either gate. The document carries the `meta.viability` record, so the visual verdict travels with it.
- `extract` that cannot pass the viability gate in three iterations: Prose naming each failing criterion with the observed visual reason, the paths of the last render and screenshot, then the document marked `meta.viability.verdict: fail`. Never a success claim.
- `preview`: The render and screenshot output with their exit codes, then one table row per criterion with the verdict and the observed reason.
- `extract` narrowed to named sections: The requested sections only, still YAML alone. A casual phrase such as give me the tokens is not a narrowing; narrow only when the user names sections or says only.
- `fonts`: The discovery or set JSON plus one short paragraph naming the fit scores, the rarity tiebreak, why the winner beat the runner up, and any pairing veto by dimension.
- `validate`: The validator JSON plus a plain-language verdict naming the exit code and each failing path.
- A follow-up edit to a document already returned: A short prose summary of what changed and what it cost, then the revalidated YAML.
- `maintain`: Free prose.

Determinism means the same evidence yields the same sections, key order, confidence labels, and not-applicable objects. Judgment lives inside field values only, and each value points back to visible evidence.

## How does an extraction run?

Use this full plan. Work in one directory of your choosing and keep every file there: `extraction.yaml` for the document, `extraction-log.md` for the log, one line per step. Keep the same record in the reply when file writing is unavailable. After each step, run the stated check and fix a failure before moving on.

1. Confirm at least one reference is available and readable. Check: the reference is named in the log.
2. Load the skeleton: `uv run --no-project --with 'PyYAML>=6,<7' python scripts/schema_tools.py skeleton --output extraction.yaml`. When a field meaning is unclear, query [the schema contract](references/extraction-schema.yaml) with `uv run --no-project --with 'PyYAML>=6,<7' python scripts/schema_tools.py field <dotted.path>` or `uv run --no-project --with 'PyYAML>=6,<7' python scripts/schema_tools.py group <name>` instead of reading the whole file. Check: the file exists and opens with `meta:`.
3. Copy the skeleton key order exactly. Do not rename, reorder, or drop top-level sections, and do not add one unless the user asked for a narrower artifact. Inside a section you may collapse an unsupported layer to the not-applicable object or keep its keys beside the applicability keys; both forms pass. Check: the section list matches the skeleton.
4. Fill `meta`, `source_analysis`, and `confidence_scores` first, keeping observed facts, inferred logic, and speculative extrapolation in separate buckets. Record the floor you enforced in `meta.rarity_floor`, the run date in `meta.extracted_at`, and one `source_types` entry per reference. Check: nothing speculative sits in the observed bucket.
5. Fill the visual foundations: color, spacing, layout, grid, sizing, borders, radii, shadows, gradients, materials, textures, and lighting. Every token carries `value`, `usage`, `visual_grounding`, `confidence`, and `inference_basis`, plus `hex`, `rgb`, and `hsl` for colours and `duration`, `easing`, and `trigger` for motion. Check: `assets/minimal-extraction.yaml` shows one filled token of each kind, and yours match those shapes.
6. Read [the font sourcing rules](references/font-sourcing.md), fill `assets/font-brief.json` from the visible type evidence, then fill every role as one set: `python3 scripts/rare_google_fonts.py set --brief <brief.json>`. Fit and legibility decide, rarity breaks the tie, and the pairing check can veto a winner. Check: the command exits 0, `unfilled` is empty, and `pairing.passes` is true.
7. Fill `typography`, recording `catalog_snapshot`, the exact `rarity` block, and the `fit` block with `fit_score`, `legibility_score`, and `evidence` for every selected family. Check: every rarity block shares one `retrieved_at` date, and `python3 scripts/rare_google_fonts.py verify --family "<name>"` exits 0 for each family.
8. Fill the experiential layers: motion, animation, camera, composition, environment, setting, wardrobe, props, iconography, and the image and rendering styles. Check: unsupported layers use the not-applicable object rather than a guess.
9. Fill the product layers in schema order: `accessibility`, `interaction_design`, `ui_patterns`, `sound_design`, `narrative_tone`, `emotional_palette`, `worldbuilding`, `styling_rules`, `dos_and_donts`, `token_dependencies`, `dynamic_tokens`, `responsive_rules`, `state_variants`, `platform_adaptations`, `ai_generation_prompts`, and `implementation_notes`. Check: `uv run --no-project --with 'PyYAML>=6,<7' python scripts/schema_tools.py sections` lists your keys in the same order.
10. Render the whole system to a page: `uv run --no-project --with 'PyYAML>=6,<7' python scripts/render_preview.py extraction.yaml --output preview.html`. Check: exit 0 and `problems` empty, which means every required token group reached the page.
11. Screenshot it: `uv run --no-project --with playwright python scripts/screenshot_preview.py preview.html --output preview.png`. Check: the PNG exists.
12. Look at the PNG and judge the eight criteria below, one verdict and one observed reason each. Check: no verdict repeats a token value instead of describing what the image shows.
13. On any failing criterion, revise the offending tokens, then repeat steps 10 through 12. Check: at most three iterations. On a third failure, stop and report the failing criteria instead of claiming success.
14. Record the passing judgment in `meta.viability`: `rendered_file`, `screenshot_file`, `iterations`, `verdict`, and the `criteria` list. Check: every criterion name from the list below appears once.
15. Run the gate: `uv run --no-project --with 'PyYAML>=6,<7' python scripts/validate_design_system_yaml.py extraction.yaml`. Exit 0 is required. On exit 1, fix every listed problem and rerun. Check: the fresh run prints `"valid": true`.
16. Return the validated YAML only, without the validation report.

## What does the validator report?

The report is one JSON object on stdout. A document passes only when exit is 0 and every field below reads correctly.

- `valid`: true only when `errors` is empty.
- `errors`: one sentence per problem. An order problem names the position and the key that sits in it.
- `rarity_floor`: the floor enforced in this run. It starts at 70.0, rises to `meta.rarity_floor` when the document records a higher one, and rises to `--min-rarity-percentile` when the flag sets a higher one.
- `live_fonts_checked`: true when the recorded ranks were compared against the live catalog. False means the comparison was skipped, so the result is unverified and the reply must say so.
- `confidence_markers`: how many `confidence` keys the document carries. It must reach `--min-confidence-markers`, which defaults to 5.
- `font_entries`: how many selected families were checked, counting primary, supporting, and every rare candidate.
- `viability_recorded`: true only when `meta.viability` holds a rendered file, a screenshot file, an iteration count, and one verdict per criterion. False means the system was never looked at, so the run is unfinished.

## What are the font rules?

One rule governs every typeface the system selects: it is published on Google Fonts, and the live catalog ranks it as rarely used right now. Both halves are measured during the run, never recalled. Rank and rank ceiling come from the live feed, and rarity percentile runs from 0.0 for the most requested family to 100.0 for the rarest rank in the feed. The floor is 70.0 unless the document or the flag sets a higher one.

`typography.font_families.primary`, `typography.font_families.supporting`, and every entry in `typography.font_families.rare_unique_candidates` carry `google_fonts_family: true` and a complete `rarity` record. `typography.font_families.observed_or_implied` is different: it records what the reference shows, so a licensed or custom face belongs there and needs no rarity record.

Rarity is a tiebreaker, never the reason for a choice. Ranking runs fit first: the candidate must match the skeleton, width, weight range, italic need, and script coverage the reference shows, scoring at least 0.65, and it must clear the legibility floor for its role, 0.7 for text and mono, 0.55 for display and accent, with 0.5 as a hard floor no rarity number can buy past. Candidates are then banded in steps of 0.05, and rarity only orders candidates inside the same band. Record the numbers in `fit`, since a rejected rarer candidate is part of the answer.

Overexposed defaults lose by default. When a common face genuinely is the true fit, name the visible evidence in `common_face_reason` and the checker accepts it; without that reason the family is rejected by name.

Pairing is a constraint on the whole set, checked after the per slot bars across seven dimensions: `skeleton_relationship`, `vertical_proportion`, `stroke_modulation`, `width_compatibility`, `weight_capacity`, `optical_color`, and `role_distinction`. Two faces that clash fail, and so do two faces too close to tell apart. A veto forces the next candidate into the slot, and the validator fails a finished document whose set does not pass, naming the failing dimension.

When the live feed cannot be read, stop and report. Name the failed command, mark `typography.font_families` with the not-applicable object, and do not present the result as verified. A rarity number recalled from memory or copied from an older snapshot is a defect, not a fallback.

## How is the system proved to work?

Schema validation proves shape, not that the system works. The rendering gate proves the rest. `scripts/render_preview.py` writes a standalone page from the document itself, so it is reproducible rather than hand written, and applies every token across a header, nav, hero, body copy at reading length, every heading level, buttons in each state, form fields, a table, a card grid, a code block, a footer, and a token inventory, in both light and dark when the document declares both. `scripts/screenshot_preview.py` captures the full page.

Judge eight criteria by looking at the screenshot, and write what the image shows rather than a number with no source: `legibility`, `contrast`, `hierarchy`, `font_pairing`, `spacing_rhythm`, `color_harmony`, `state_distinction`, and `reference_fidelity`. Any failure sends you back to the tokens, not to the wording of the verdict. The loop is capped at three iterations, and a run that still fails reports the failing criteria rather than shipping.

## What loads when?

[The schema contract](references/extraction-schema.yaml) is machine readable YAML holding the section order, field rules, font rules, syntax rules, and self-check list. Query it through `scripts/schema_tools.py` rather than reading it whole. Load [the font sourcing rules](references/font-sourcing.md) before touching any font field. Load [the generation contract](references/generation-contract.md) only when editing this package.

Load `assets/schema-skeleton.yaml` through the skeleton command to start a document. Load `assets/font-brief.json` to map visible type evidence onto catalog filters before running discovery. Load `assets/minimal-extraction.yaml` to see the smallest document that clears every gate and one filled token of each kind. Load `scripts/` for the executable gates, `scripts/tests/` only when changing script behavior, and `evals/` when measuring activation, behavior, failure handling, recovery, or timing.

Load one file from `examples/` when you are about to run the matching command, since each one is a real transcript with real exit codes.

- [examples/help.md](examples/help.md) before answering `help`.
- [examples/extract.md](examples/extract.md) before a first extraction, and for the complete validating document in [examples/extract-output.yaml](examples/extract-output.yaml).
- [examples/fonts-brief.md](examples/fonts-brief.md) before running discovery, to turn a filled brief into a command line.
- [examples/validate.md](examples/validate.md) before validating a file someone else wrote.
- [examples/maintain.md](examples/maintain.md) before editing this package.
- [examples/make-it-rarer.md](examples/make-it-rarer.md) when a user asks for rarer typefaces after a document already exists.
- [examples/viability-loop.md](examples/viability-loop.md) before the first render, for a real failing pass, the token revision, and the passing second pass.
- [examples/pairing-veto.md](examples/pairing-veto.md) when a set level veto blocks the highest scoring candidate.
- [examples/failure-section-order.md](examples/failure-section-order.md) when the validator reports a section order problem, which is the failure this skill causes most often.

## How is this package maintained?

For `maintain`, the YAML-only response contract does not apply. Establish the failing state first: a gate that rejects valid input, a missing behavior, or the exact gap the user named. Add the focused test, watch it fail, add the smallest change that passes it, then run the five checks listed at the top of this file. Exit 0 on each is required before reporting. Keep long detail in `references/`, executable checks in `scripts/`, templates in `assets/`, and worked runs in `examples/`. A rule change that outdates an example updates that example in the same edit.

## Gotchas

- The feed reports ranks above the family count. The denominator is the rank ceiling, the highest rank in the run, so the rare tail stays ordered. Record the rank and the ceiling exactly as returned.
- When two families report the same percentile, the higher `popularity_rank` is the rarer one. Discovery already sorts that way, so the first row is the rarest match.
- `--subset` and `--variable-only` shrink the rare tail sharply and can hide the rarest family. Apply them only when the reference demands them, and name the tradeoff when you relax one.
- `meta.rarity_floor` is binding. The validator reads it and raises its own floor to match, so recording 90.0 makes every later revalidation enforce 90.0.
- A family that was rare last month may not be rare today. The default validation compares recorded ranks against the live catalog and fails on drift, which is the gate working.
- Common interface defaults are rejected by name even when the surrounding prose argues for them, unless `common_face_reason` names the visible evidence.
- Percentiles stay under 100.0 because the denominator is the rank ceiling plus one, so the rarest family no longer saturates and ties no longer hide behind a shared 100.0.
- A rarer face that fails the legibility floor is a rejection, not a tradeoff to argue about. Report it as rejected and name the floor.
- Inline links take the accent role in every mode, so a dark canvas system fixes a failed `contrast` verdict by changing the accent token. A link left at the browser default is a harness bug, not a token decision.
- When a criterion cannot be fixed by any token value, say so and name the harness limit. Editing the page to hide the problem is not a pass.
- Words such as unusual or overlooked prove nothing. `rarity_reason` explains the measured number; it never replaces it.
- A fallback stack must name families that exist and must end with a generic family.
- Do not run separate per-section validation passes. The bundled validator is the single mechanical gate.
- Do not read the schema contract end to end. Query one field or one group at a time.
- The section order, the confidence labels, and the font floor all come from the schema contract. Change the rule there and every gate follows; hardcoding a value in a script breaks that link.

## When is an extraction complete?

An extraction is complete only when the validator exits 0 on a fresh run with `live_fonts_checked` true or its failure reported in plain words, every selected family carries a rarity record at or above the enforced floor and a `fit` block that clears its role floor, the font set passes the pairing check, every unsupported layer uses the not-applicable object, the rendered page has been screenshotted and passed all eight criteria with `meta.viability.verdict: pass`, and the reply contains the validated YAML alone. Until the picture passes, the run is not done and must not be reported as done.
