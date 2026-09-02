# Baseline and ledger contract

Resource gate: run `mise run validate` before using package files named here.

Parent and backlink: [`../SKILL.md`](../SKILL.md), Procedure steps 1 and 2.

## Baseline

For every governed source and future target, record an absolute path and `present` or `absent` status. For a present file, record SHA-256, bytes, lines, physical ATX headings, and mode. Record expected source hashes when a task pins them and stop on drift.

A backup record names its owner-only backup, post-copy hash, and mode. Do not store credential-bearing remote URLs. Record remote names only.

Do not create rewrites, durable notes, commits, or configuration changes during baseline capture.

## Ledger wrapper

Record:

- `task`
- `source_files`
- optional `future_files`
- `coverage_required`, normally `1.0`
- `coverage_method`
- `entries`

## Ledger entry

Each entry records:

- stable `id`
- `source_file` and exact `original`
- `meaning` and `strength`
- target file, section, and text
- one or more target records after a split
- `action`: `keep`, `split`, `move`, or `clarify`
- `review`: same meaning or failed
- routing reason when ownership moves

Never use `drop`. Use `mixed` strength only when sibling targets retain different source strengths.

## Focused acceptance

1. Parse every JSON artifact.
2. Require unique IDs and complete required fields.
3. Require allowed strengths, actions, and reviews.
4. Recount source clauses and compare them with ledger coverage.
5. Rehash live sources and compare them with the baseline.
6. Prove backup byte identity and required mode.
7. Recount physical headings in source order.
8. Confirm planned future paths remain recorded as absent until created.
9. Confirm no temporary builder remains.

Call these checks focused ad-hoc validation unless a complete suite ran.
