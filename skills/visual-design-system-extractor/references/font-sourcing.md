# Font sourcing rules

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this file before filling any field under `typography.font_families`. It defines where a typeface may come from, how rarity is measured, and what the document must record as proof.

The machine readable form of these rules lives under `font_rules` in [the schema contract](extraction-schema.yaml). Print it with `uv run --no-project --with 'PyYAML>=6,<7' python scripts/schema_tools.py rules`. Change a rule there rather than in a script.

## The rule

Every family the extraction selects must satisfy both halves of one rule: it is published on Google Fonts, and the live catalog ranks it as rarely used at the moment of the run. Neither half may be asserted from memory. A stored font list goes stale, so the answer must come from the feed read during the run.

Selection covers `typography.font_families.primary`, `typography.font_families.supporting`, and every entry in `typography.font_families.rare_unique_candidates`. Observation is different: `typography.font_families.observed_or_implied` records the faces visible in the reference, which may include licensed or custom type, and those entries carry no rarity requirement.

## Where the data comes from

The live feed is `https://fonts.google.com/metadata/fonts`. It returns one record per family with the fields this skill depends on: `family`, `category`, `popularity`, `trending`, `dateAdded`, `axes`, `subsets`, `designers`, and `isNoto`. Rank 1 is the most requested family, so a high rank number means low use.

Rarity percentile turns that rank into a stable number: `(popularity_rank - 1) / (total_families - 1) * 100`, rounded to one decimal. It reads 0.0 for the single most popular family and 100.0 for the least popular one. Because the feed sometimes carries a rank above the family count, the percentile clamps at 100.0.

The default floor is 70.0, which keeps the least used third of the catalog. Raise it with `--min-rarity-percentile` when a brief asks for stronger distinction. Lower it only when the user states the tradeoff, and record the chosen floor in `meta`.

## How to select a family

1. Read the catalog once per task: `python3 scripts/rare_google_fonts.py catalog --output /tmp/font-catalog.json`. Check: the file carries `total_families` above zero and a `retrieved_at` date equal to today.
2. Derive filters from the visual evidence rather than from taste. Serif proportions in the reference become `--category Serif`, a wide language range becomes `--subset latin-ext`, and a fluid weight range becomes `--variable-only`. Check: every filter traces back to something visible.
3. Rank the candidates: `python3 scripts/rare_google_fonts.py discover --category Serif --limit 10`. Check: the command exits 0 and each result carries a `rarity` block.
4. Choose from the ranked list using the visual evidence, then record the exact `rarity` block the command returned. Check: `popularity_rank`, `total_families`, `rarity_percentile`, `trending_rank`, `date_added`, `variable`, `source`, and `retrieved_at` are copied without edits.
5. Confirm the final set: `python3 scripts/rare_google_fonts.py verify --family "First" --family "Second"`. Exit 0 is required. On exit 1, read the `reason` field, replace the rejected family, and rerun.
6. Write `catalog_snapshot` under `typography.font_families` with the feed URL, the retrieval date, and the family count. Check: every rarity block in the document shares that same `retrieved_at`.

## What each entry records

A selected entry carries `family`, `google_fonts_family: true`, and a complete `rarity` mapping, plus `classification`, `fallback_stack`, `visual_grounding`, `confidence`, and `inference_basis`. A rare candidate adds `role`, `pairs_well_with`, `rarity_reason`, `pairing_logic`, and `use_constraints`.

`rarity_reason` explains the measured number in one sentence, such as which rank and date added put the family outside common use. It never substitutes for the number, and words like unusual or overlooked prove nothing on their own.

`fallback_stack` ends with a generic family so text still renders when the webfont fails. Name only families that exist; an invented fallback is a defect.

## When the feed cannot be read

Stop and report. Do not fill a rarity block from memory, do not copy an older snapshot, and do not present the extraction as verified. State that the live catalog was unreachable, return the rest of the document with `typography.font_families` marked using the standard not-applicable object, and name the exact command that failed. The user can then rerun once the network is available.

## Rejected patterns

- A common interface default in a selected slot. The validator holds a list of these families and rejects them outright.
- A rarity block whose `source` is anything other than the live feed URL.
- A `popularity_rank` that disagrees with the live catalog. The default check compares them and fails on drift.
- A family that appears nowhere in the live catalog, including a self-hosted or licensed face placed in a selected slot.
- A `retrieved_at` date carried over from an earlier run.
