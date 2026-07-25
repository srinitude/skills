---
name: visual-design-system-extractor
description: 'Use when reference images, screenshots, moodboards, style frames, brand boards, cinematic stills, or product interface shots must become a production design system, design tokens, art direction, motion rules, or a YAML style specification. Covers reverse engineering visual references into a deterministic YAML contract with graded confidence, evidence boundaries, and typefaces drawn from the live Google Fonts catalog and ranked as rarely used. Not for generating images or for ordinary frontend work where no reference has to be decoded first.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
---

# Visual Design System Extractor

Turn visual references into one parser-valid YAML design system whose every claim traces back to something visible, and whose every selected typeface is a Google Fonts family the live catalog ranks as rarely used at the moment of the run.

The gates need a terminal, a YAML parser, and network access to the live font catalog. The commands below fetch the parser through `uv`; run `mise run ci` inside this directory to check the whole package.

## Which commands does this skill accept?

Interpret a plain request with an attached reference as `extract`.

| Command             | Result                                                                |
| ------------------- | --------------------------------------------------------------------- |
| `help`              | Show this table and the current schema version.                       |
| `extract <refs>`    | Produce the full YAML design system from the supplied references.     |
| `fonts <brief>`     | Return ranked rare Google Fonts candidates without a full extraction. |
| `validate <file>`   | Run the schema and font gates against an existing extraction.         |
| `maintain <change>` | Edit this package under the test-first rules below.                   |

If no reference is attached or reachable, stop and ask for the image, screenshot, moodboard, style frame, or URL. Do not invent a system from a description alone.

## What does the extraction return?

For `extract`, return parser-valid YAML and nothing else: no code fences, no prose before or after, no separate summary of the images, and no document that failed the gate. Determinism means the same evidence yields the same sections, key order, confidence labels, and not-applicable objects. Judgment lives inside field values only, and each value points back to visible evidence.

## How does an extraction run?

Use this full plan. After each step, run the stated check and fix a failure before moving on. Append one line per step to `extraction-log.md` in the working directory, or keep the same record in the reply when file writing is unavailable.

1. Confirm at least one reference is available and readable. Check: the reference is named in the log.
2. Load the skeleton: `uv run --no-project --with 'PyYAML>=6,<7' python scripts/schema_tools.py skeleton --output /tmp/extraction-skeleton.yaml`. When a field meaning is unclear, query [the schema contract](references/extraction-schema.yaml) with `uv run --no-project --with 'PyYAML>=6,<7' python scripts/schema_tools.py field <dotted.path>` or `uv run --no-project --with 'PyYAML>=6,<7' python scripts/schema_tools.py group <name>` instead of reading the whole file. Check: the skeleton file exists and opens with `meta:`.
3. Copy the skeleton key order exactly. Do not rename, reorder, or drop keys, and do not add a top-level section unless the user asked for a narrower artifact. Check: the section list matches the skeleton.
4. Fill `meta`, `source_analysis`, and `confidence_scores` first, keeping observed facts, inferred logic, and speculative extrapolation in separate buckets. Check: nothing speculative sits in the observed bucket.
5. Fill the visual foundations: color, spacing, layout, grid, sizing, borders, radii, shadows, gradients, materials, textures, and lighting. Check: every token carries `confidence` and `inference_basis`.
6. Read [the font sourcing rules](references/font-sourcing.md), then select every typeface through the live catalog before writing the typography section. Check: `python3 scripts/rare_google_fonts.py verify --family "<name>"` exits 0 for each selected family.
7. Fill `typography`, recording `catalog_snapshot` plus the exact `rarity` block the tool returned for each family. Check: every rarity block shares one `retrieved_at` date.
8. Fill the experiential layers: motion, animation, camera, composition, environment, setting, wardrobe, props, iconography, and the image and rendering styles. Check: unsupported layers use the not-applicable object rather than a guess.
9. Fill the product layers: accessibility, interaction, interface patterns, sound, narrative, worldbuilding, styling rules, token dependencies, responsive rules, state variants, platform adaptations, generation prompts, and implementation notes. Check: implementation-ready requests carry token dependencies and platform adaptations.
10. Run the gate: `uv run --no-project --with 'PyYAML>=6,<7' python scripts/validate_design_system_yaml.py /tmp/extraction.yaml`. Exit 0 is required. On exit 1, fix every listed problem and rerun. Check: the fresh run prints `"valid": true`.
11. Return the validated YAML only, without the validation report.

## What are the font rules?

One rule governs every typeface the system selects: it is published on Google Fonts, and the live catalog ranks it as rarely used right now. Both halves are measured during the run, never recalled. Rank and family count come from the live feed, and rarity percentile runs from 0.0 for the most requested family to 100.0 for the least. The floor is 70.0 unless the user sets another value.

`typography.font_families.primary`, `typography.font_families.supporting`, and every entry in `typography.font_families.rare_unique_candidates` carry `google_fonts_family: true` and a complete `rarity` record. `typography.font_families.observed_or_implied` is different: it records what the reference shows, so a licensed or custom face belongs there and needs no rarity record.

When the live feed cannot be read, stop and report. Name the failed command, mark `typography.font_families` with the not-applicable object, and do not present the result as verified. A rarity number recalled from memory or copied from an older snapshot is a defect, not a fallback.

## What loads when?

[The schema contract](references/extraction-schema.yaml) is machine readable YAML holding the section order, field rules, font rules, syntax rules, and self-check list. Query it through `scripts/schema_tools.py` rather than reading it whole. Load [the font sourcing rules](references/font-sourcing.md) before touching any font field. Load [the generation contract](references/generation-contract.md) only when editing this package.

Load `assets/schema-skeleton.yaml` through the skeleton command to start a document. Load `assets/font-brief.json` to map visible type evidence onto catalog filters before running discovery. Load `assets/minimal-extraction.yaml` to see the smallest document that clears every gate. Load `scripts/` for the executable gates, `scripts/tests/` only when changing script behavior, and `evals/` when measuring activation, behavior, failure handling, recovery, or timing.

## How is this package maintained?

For `maintain`, the YAML-only response contract does not apply. Establish the failing state first: a gate that rejects valid input, a missing behavior, or the exact gap the user named. Add the focused test, watch it fail, add the smallest change that passes it, then run `mise run ci` inside this directory. Exit 0 is required before reporting. Keep long detail in `references/`, executable checks in `scripts/`, and templates in `assets/`.

## Gotchas

- The live feed sometimes reports a popularity rank above the family count. The percentile clamps at 100.0; record the rank exactly as returned.
- A family that was rare last month may not be rare today. The default validation compares recorded ranks against the live catalog and fails on drift, which is the gate working.
- Common interface defaults are rejected by name even when the surrounding prose argues for them.
- Words such as unusual or overlooked prove nothing. `rarity_reason` explains the measured number; it never replaces it.
- A fallback stack must name families that exist and must end with a generic family.
- Do not run separate per-section validation passes. The bundled validator is the single mechanical gate.
- Do not read the schema contract end to end. Query one field or one group at a time.
- The section order, the confidence labels, and the font floor all come from the schema contract. Change the rule there and every gate follows; hardcoding a value in a script breaks that link.

## When is an extraction complete?

An extraction is complete only when the validator exits 0 on a fresh run, the live font comparison passed or its failure was reported in plain words, every selected family carries a rarity record at or above the floor, every unsupported layer uses the not-applicable object, and the reply contains the validated YAML alone.
