# Evaluation contract

Owner and backlink: [`../SKILL.md`](../SKILL.md) through `PD-101`.

Load this file and [`eval-cases.json`](eval-cases.json) before testing or changing the skill.

## Clock schema

A successful clock call returns one JSON object with these fields:

- `captured_at`: ISO 8601 local timestamp with UTC offset
- `date`: ISO local date
- `time`: local time to seconds
- `weekday`: English weekday name
- `timezone`: configured IANA name or `system-local`
- `zone_abbreviation`: active local abbreviation
- `utc_offset`: signed `HH:MM`
- `source`: `environment`, `hermes-config`, or `system-local`
- `yesterday`: ISO date
- `tomorrow`: ISO date

Unknown or invalid configured timezones fail with a nonzero exit and an error on standard error. An empty Hermes timezone setting uses system-local time.

## Native acceptance

Require all of these:

1. The script parses and stays within the code-shape limits.
2. A UTC run returns a valid internally consistent schema.
3. An invalid IANA timezone exits nonzero without a success object.
4. System-local fallback returns a valid offset and local date.
5. `SKILL.md` loads through `skill_view` with its linked files.
6. `/always-current-date` appears in the active slash-command map and loads the runtime contract.
7. The description is under 60 characters and the Markdown limits pass.
8. The stock Hermes prompt contains mandatory relevant-skill loading.
9. The raw clock command is relative to the supplied skill working directory and contains no unresolved skill-directory variable.

## Behavioral acceptance

Each case in `eval-cases.json` declares required and forbidden behavior. Every case must pass. One missed clock call, stale anchor, duplicate call, prompt rewrite, wrong absolute date, missing stored prefix, or fail-open fallback blocks behavioral parity.

Keep native, activation, behavior, enrollment, and whole-package statuses separate. A queued model evaluation is not a behavior PASS.

## Hook comparison

Compare the same cases against the prior hook contract. The skill may claim parity only when neither path misses a case. It may claim a benefit only for an observed axis such as persisted output, fail-closed clock errors, or starting-point binding.
