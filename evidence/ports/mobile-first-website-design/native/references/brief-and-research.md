# Brief and research

Backlink: [SKILL.md](../SKILL.md). Load at job start.

## Canonical brief

Create UTF-8 canonical JSON with sorted keys. Missing facts are `null` plus a blocker.

Required fields:

- `project_id`, `product`, `release_target`, `primary_conversion`
- `audience`, `visitor_state`, `problem`, `consequence`, `mechanism`
- `claims[]` with `claim_id`, evidence ID, truth status, and allowed wording
- `required_sections[]`, routes, assets, constraints, and brand inputs
- `breakpoints[]` with stable ID, positive integer width, and height
- `integrations[]` with availability, revision, and authorization state
- `image_jobs[]` and accessibility, performance, and privacy budgets

Reject unstated claims, duplicate IDs, unknown width order, and secret-bearing fields.

## Diagnosis

Classify the visitor once:

1. `problem-aware`: lead with cost and recognition, then mechanism.
2. `solution-aware`: lead with differentiator and proof.
3. `product-aware`: lead with specific value, objection handling, and action.

Record the classification evidence. A tie uses this order: product-aware, solution-aware, problem-aware.

## Section jobs

For each required section, define:

- one visitor question
- one required answer
- one proof obligation
- one primary or supporting action
- one image job or `none`
- one accessibility obligation

Do not choose style in this file.

## Research order

For each section, run available routes in this fixed order: Refero, Mobbin, Lazyweb, direct first-party web. Never stop after the first route. Keep mechanism notes, not copied appearance.

Normalize every result to:

```json
{"route":"mobbin","status":"PASS","query_id":"hero-value-proof","mechanism":"value statement plus product proof","relevance":4,"adaptation":"show the product outcome beside the primary action","source_id":"..."}
```

Use relevance integers `0..4`. Sort by relevance descending, then route order, then source ID byte order. Keep at most six results per route and section.

A section passes research when it has at least one current result, a mechanism, an adaptation, and a source ID. Otherwise return `BLOCKED_RESEARCH_FLOOR`.

## Conversion narrative

Write exactly five statements in order:

1. problem
2. consequence
3. mechanism
4. proof
5. action

Map each section to at least one statement. Freeze the narrative and section obligations before wireframing. Later styling may not change them without invalidating every downstream gate.
