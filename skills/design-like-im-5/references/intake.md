# Intake

Load this file at the start of `create`, `review`, or `revise`.

## Goal

Freeze facts that guide the work. Do not fill a gap with a guess.

## Needed input

- `outcome`: What should change for the user?
- `audience`: Who needs that change?
- `platform`: Where will the product run?
- `primary_tasks`: Which tasks must work?
- `source_permissions`: Which sources may be read?
- `proof_threshold`: What fresh proof will show success?

Also record risk, access needs, locale, content range, input modes, skill, time, and setting when they matter.

## Stop rule

Ask one short question when a missing fact changes the result. Keep other safe work moving. Use `SOURCE_GAP` when a needed source has no access.

## Return

Write a JSON file that fits [assets/run-intake.schema.json](../assets/run-intake.schema.json). Pass it to `scripts/run_pipeline.py start`.

Go next to step 2 in `SKILL.md`.
