# Font sourcing rules

Owner and backlink: [`../SKILL.md`](../SKILL.md). Read this file before filling any field under `typography.font_families`. It defines where a typeface may come from, how rarity is measured, and what the document must record as proof.

The machine readable form of these rules lives under `font_rules` in [the schema contract](extraction-schema.yaml). Print it with `mise run schema-tools rules`. Change a rule there rather than in a script.

## The rule

Every family the extraction selects must satisfy both halves of one rule: it is published on Google Fonts, and the live catalog ranks it as rarely used at the moment of the run. Neither half may be asserted from memory. A stored font list goes stale, so the answer must come from the feed read during the run.

Rarity is the last question, not the first. A candidate has to fit the reference and stay readable before its rank matters, and rarity only orders candidates that already fit. A rare face that fails the role legibility floor is rejected, and no argument in prose overturns that.

Selection covers `typography.font_families.primary`, `typography.font_families.supporting`, and every entry in `typography.font_families.rare_unique_candidates`. Observation is different: `typography.font_families.observed_or_implied` records the faces visible in the reference, which may include licensed or custom type, and those entries carry no rarity requirement.

## Where the data comes from

The live feed is `https://fonts.google.com/metadata/fonts`. It returns one record per family with the fields this skill depends on: `family`, `category`, `popularity`, `trending`, `dateAdded`, `axes`, `subsets`, `designers`, and `isNoto`. Rank 1 is the most requested family, so a high rank number means low use.

Rarity percentile turns that rank into a stable number: `(popularity_rank - 1) / (rank_ceiling - 1) * 100`, rounded to one decimal. The rank ceiling is the highest rank the feed reports in the run, which is never below the family count, so the whole rare tail keeps distinct scores instead of piling up at 100.0. Only the single rarest rank reads 100.0, and the most requested family reads 0.0. Every rarity block records `rank_ceiling` beside `total_families` so the number can be recomputed later.

When two families still report the same percentile, the higher `popularity_rank` is the rarer one. `discover` sorts by percentile, then by rank descending, then by family name, so the first row is always the rarest match.

The default floor is 70.0, which keeps the least used third of the catalog. Raise it with `--min-rarity-percentile` when a brief asks for stronger distinction. Lower it only when the user states the tradeoff, and record the chosen floor in `meta.rarity_floor`. The recorded floor is binding: the validator reads it and raises its own floor to match, so anyone revalidating the document later gets the same gate. A recorded floor never lowers the contract floor of 70.0.

## How fit is scored

`mise run font-fit` scores each candidate against the brief on four parts: skeleton match at 0.45, width class at 0.15, weight coverage at 0.2, and reported style at 0.2, then multiplies by a script coverage gate. A score under 0.65 is rejected, and the reason names the part that failed.

Legibility is a separate score with its own floors: 0.7 for `text` and `mono`, 0.55 for `display` and `accent`, and a hard floor of 0.5 that nothing can pass. It drops for a display or handwriting face asked to hold text, for a family with no weight between 300 and 500, for a single weight family, for default leading outside 1.0 to 1.9, for a reported thickness at either extreme, and for a family whose primary script is not Latin.

Passing candidates are grouped into bands of 0.05. Rarity orders candidates inside a band and never across bands, so a rarer face never displaces a better fitting one.

Overexposed defaults are rejected by name. When the reference genuinely renders one, set `allow_common` with `common_reason` on the brief and record `common_face_reason` in the document, naming the visible evidence such as a live stylesheet that serves the family.

## How the set is checked

Fit and legibility judge one slot. Pairing judges the whole set, and it runs after the per slot bars across seven dimensions: `skeleton_relationship`, `vertical_proportion`, `stroke_modulation`, `width_compatibility`, `weight_capacity`, `optical_color`, and `role_distinction`.

Both directions fail. Two faces that clash break a metric dimension, and two faces too close to tell apart break `role_distinction`. Either way the failing dimension is named, the winning candidate is vetoed, and the next candidate takes the slot. `mise run font-set -- --brief <file>` fills every role this way and returns the chosen set, the vetoes, and the per dimension verdict. The validator runs the same check on a finished document.

## How to select a family

1. Read the catalog once per task: `mise run font-catalog -- --output /tmp/font-catalog.json`. Check: the file carries `total_families` above zero and a `retrieved_at` date equal to today.
2. Derive filters from the visual evidence rather than from taste. Serif proportions in the reference become `--category Serif`, a wide language range becomes `--subset latin-ext`, and a fluid weight range becomes `--variable-only`. Set `--subset` only when the reference itself shows extended Latin or non-Latin text, and set `--variable-only` only when the design needs axis interpolation at run time; a variable face in the reference does not require a variable replacement. Both filters shrink the rare tail sharply and can hide the rarest match, so name the filter you dropped when rarity matters more than the filter. Check: every filter traces back to something visible.
3. Rank the candidates by fit: `mise run font-discover -- --skeleton Serif --need-weight 400 --need-weight 700 --role text --show-rejected`. Check: the command exits 0, each result carries a `rarity` block and a `fit` block, and the rejected list explains what the bars dropped.
4. Fill every role at once: `mise run font-set -- --brief assets/font-brief.json`. Check: `unfilled` is empty and `pairing.passes` is true. A veto names its dimension, and the next candidate takes the slot.
5. Choose from the ranked list using the visual evidence, then record the exact `rarity` block and the `fit` block the command returned. Check: `popularity_rank`, `total_families`, `rank_ceiling`, `rarity_percentile`, `trending_rank`, `date_added`, `variable`, `source`, and `retrieved_at` are copied without edits.
6. Confirm the final set: `mise run font-verify -- --family "First" --family "Second"`. Exit 0 is required. On exit 1, read the `reason` field, replace the rejected family, and rerun.
7. Write `catalog_snapshot` under `typography.font_families` with the feed URL, the retrieval date, and the family count. Check: every rarity block in the document shares that same `retrieved_at`.

## What each entry records

A selected entry carries `family`, `google_fonts_family: true`, a complete `rarity` mapping, and a `fit` mapping with `fit_score`, `legibility_score`, and `evidence`, plus `classification`, `fallback_stack`, `visual_grounding`, `confidence`, and `inference_basis`. Add `set_role` when the family holds a role other than text, since the role sets the floor it must clear. A rare candidate adds `role`, `pairs_well_with`, `rarity_reason`, `pairing_logic`, and `use_constraints`.

`rarity_reason` explains the measured number in one sentence, such as which rank and date added put the family outside common use. It never substitutes for the number, and words like unusual or overlooked prove nothing on their own.

`fallback_stack` ends with a generic family so text still renders when the webfont fails. Name only families that exist; an invented fallback is a defect.

## When the feed cannot be read

Resource gate: run `mise run validate` before using package files named here.

Stop and report. Do not fill a rarity block from memory, do not copy an older snapshot, and do not present the extraction as verified. State that the live catalog was unreachable, return the rest of the document with `typography.font_families` marked using the standard not-applicable object, and name the exact command that failed. The user can then rerun once the network is available.

A worked brief, the command it produces, and a follow-up run that finds no usable family above a stricter floor are in [the examples](../examples/fonts-brief.md) and [the rarer run](../examples/make-it-rarer.md). The set-level veto path remains covered by the executable pairing tests because live candidate order can change.

## Rejected patterns

- A common interface default in a selected slot without a stated `common_face_reason`. The validator holds a list of these families and rejects them by name.
- A rarer candidate chosen over a better fitting one. Fit bands come first, and rarity only orders inside a band.
- A selected entry with no `fit` record, or a fit record whose scores were carried over from an earlier run.
- A font set that never ran the pairing check, or a veto reported without naming the failing dimension.
- A rarity block whose `source` is anything other than the live feed URL.
- A `popularity_rank` that disagrees with the live catalog. The default check compares them and fails on drift.
- A family that appears nowhere in the live catalog, including a self-hosted or licensed face placed in a selected slot.
- A `retrieved_at` date carried over from an earlier run.
