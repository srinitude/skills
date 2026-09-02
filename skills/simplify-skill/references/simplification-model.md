# Simplification model

Resource gate: run `mise run validate` before using package files named here.

Parent and backlink: [`../SKILL.md`](../SKILL.md), Procedure step 4.

Simplification is a constrained change from a baseline to a candidate. The candidate must reduce a declared cost for a named actor and task while preserving every invariant outside an approved loss bound.

Accepted costs include common-path burden, ambiguity, duplicates, reader or operator effort, tool calls, retries, hidden states, dependency count, maintained surfaces, and test effort. Line or word count can support another measure but cannot decide acceptance alone.

Try modes in this order: `deduplicate`, `clarify`, `reorder`, `progressive-disclosure`, `extract-child`, `simplify-code`, `approved-loss`.

Use progressive disclosure only for optional detail with a visible load trigger and backlink. Create a child only for a reusable capability with its own trigger, outcome, owner, interface, and tests.

Closed enums, canonical machine data, and executable checks reduce interpretation differences. They do not prove identical model prose. Scope behavior claims to observed actors, models, environments, tasks, settings, and trials.
