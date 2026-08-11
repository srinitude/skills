# Preservation and acceptance contract

Parent owner and backlink: [`../SKILL.md`](../SKILL.md).

Load this file before the `CONTRACT` and `VERIFY` states. This file owns ledger fields, closed values, vetoes, deterministic data, acceptance thresholds, and report fields.

## Baseline packet

Freeze an ordered packet before mutation:

1. `SKILL.md`.
2. Every linked instruction, script, template, and asset needed by the cases.
3. Origin and registry records.
4. Current Hermes commit and relevant live-doc URLs.
5. Existing checks and their raw results.
6. Representative tasks and observed end states.

Record each relative path, byte count, and SHA-256. Hash ordered `relative-path`, null byte, and file-hash rows to form the packet hash. Use `ABSENT_BASELINE` only for a new skill.

## Closed values

Use only these values:

- Requirement strength: `must`, `must_not`, `should`, `may`, `prefer`.
- Ledger action: `keep`, `deduplicate`, `clarify`, `reorder`, `move`, `extract`, `approved_drop`.
- Mode: `deduplicate`, `clarify`, `reorder`, `progressive-disclosure`, `extract-child`, `simplify-code`, `approved-loss`.
- Decision: `ACCEPT`, `NO_CHANGE`, `NEEDS_APPROVAL`, `BLOCKED`.
- Check status: `PASS`, `FAIL`, `BLOCKED`, `NOT_APPLICABLE`, `PENDING`.
- Evidence type: `direct`, `inference`, `unverified`.

An unknown value is the literal string `unknown`. Do not add a synonym.

## Clause ledger

Split the baseline into atomic rules and observable behaviors. Assign stable IDs in source order as `S-001`, `S-002`, and so on.

Each row must contain:

- `source_id`, source path, and source span.
- Exact source text and normalized meaning.
- Authority, strength, conditions, and exceptions.
- Observable behavior or state transition.
- Exact-span flag and reason.
- Action and target path.
- Candidate span and replacement text.
- Baseline and candidate evidence IDs.
- Review status.

One target may serve several source IDs only when meaning, strength, conditions, authority, and exceptions are identical. Record all source IDs on that target.

Coverage is mapped source IDs divided by all source IDs. Coverage must equal `1.0`. `approved_drop` requires the approval record and exact loss bound.

## Protected spans

Mark a span exact when a byte change can alter authority, execution, compatibility, identity, or evidence. This includes commands, flags, paths, schemas, hashes, quotations, legal text, IDs, version ranges, permission rules, and numeric limits.

Every protected span must be byte-equal at its final destination or have an approved change record. Similar wording does not pass.

## Conflict handling

Apply authority order from the active profile and target workspace. If two same-authority rules conflict:

1. Record both IDs and the exact conflict.
2. Stop before rewrite.
3. Return `NEEDS_APPROVAL` when the user can choose.
4. Return `BLOCKED` when a higher authority or missing owner must resolve it.

Never merge a contradiction into vague prose.

## Vetoes

A candidate cannot be accepted when any item is true:

- Ledger coverage is below `1.0`.
- A rule, condition, exception, output, state, or verification path is absent.
- Requirement strength is weaker or scope changed without approval.
- A protected span changed without approval.
- Authority, safety, privacy, permission, rollback, or stop behavior regressed.
- A command, API, schema, import, path, or dependency was invented.
- The common task is worse on any user-declared hard measure.
- No declared cost decreased.
- A child duplicates an owner, lacks direct proof, or creates a load cycle.
- Package, active-load, or required regression checks fail.

A veto returns `NO_CHANGE`, `NEEDS_APPROVAL`, or `BLOCKED`. It never returns partial `ACCEPT`.

## Deterministic decision data

Store machine decisions as UTF-8 JSON. Use explicit keys, closed enum values, sorted object keys, and stable array order. Canonicalize before hashing. Reject duplicate keys, non-finite numbers, comments, and schema-unknown fields.

Required top-level keys are:

- `schema`, `target`, `baseline_packet_sha256`, `candidate_packet_sha256`.
- `state`, `decision`, `mode`, `actor`, `task`, `environment`.
- `invariants`, `measures`, `loss_budget`, `ledger_summary`.
- `human_verdict`, `agent_verdict`, `child_skills`, `checks`, `residuals`.

Do not let free prose select a branch. The enum field selects the branch. Prose may explain it.

## Child-skill record

For every proposed child, record:

- Name, trigger, standalone outcome, and canonical owner.
- Inputs, outputs, authority, failure states, and version boundary.
- Existing-owner search result and expected reuse.
- Direct cases, parent-route cases, and whole-package cases.
- Added discovery, loading, coordination, and maintenance cost.
- Parent and child dependencies as a directed graph.
- Gate result for each normal skill-creation rule.

Sort child names before hashing. Reject self-edges, parent-back-edges, cycles, duplicate owners, and children that exist only to meet a size limit.

## Acceptance thresholds

`ACCEPT` requires all of these:

1. Baseline and candidate packets parse and their hashes recompute.
2. Ledger coverage equals `1.0` and unauthorized drops equal `0`.
3. Every protected span passes or has exact approval.
4. Every invariant and veto check passes.
5. At least one declared cost is lower on the same actor, task, and environment.
6. Existing and new native checks pass.
7. Representative and fault tasks preserve or improve end-state results.
8. Active loading, links, metadata, and owner boundaries pass.
9. Child direct, routed, graph, and package checks pass when applicable.
10. Package verification passes and eval enrollment status is recorded separately.

A shorter candidate that fails any threshold is `NO_CHANGE` or a blocked status.

## Required pressure cases

Load `eval-cases.json` and run every case in its listed order. Do not add, remove, reorder, or relabel a case after packet freeze.

## Final report

Write one report with:

- Baseline and candidate packet identities, decision, mode, actor, task, environment, and loss budget.
- Invariant and ledger summaries.
- Per-measure baseline, candidate, delta, and method.
- Exact moved, rewritten, extracted, and approved-loss records.
- Human and agent verdicts with model or population scope.
- Native, task, graph, package, readback, and rollback checks.
- Eval job ID and packet hash, with enrollment separate from behavior result.
- Residual risks, unresolved conflicts, and required fresh-session checks.

Package PASS, queue PASS, behavior-eval PASS, and whole-skill PASS are different fields. Never derive one from another.
