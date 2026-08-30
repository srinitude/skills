# Review record

Owner and backlink: [`../SKILL.md`](../SKILL.md). This file owns the review record path, the required fields, the finding ID format, and the block and sign-off semantics. The parent owns runtime behavior.

## Record path

Write the record at `./review-log-<slug>.md` in the directory the author is working in. Derive the slug from the target name. Print the absolute path once when the record is created. If the working directory cannot hold files, keep the same visible record in the conversation and state that no file was written.

## Required fields

The record holds these fields, in order, after a one-line title:

- target: the path, commit, branch, or pull request identifier under review.
- contract: the acceptance contract the review checks against, named from the target, its tests, its task or issue, or a linked specification.
- verdict: `sign-off` or `block`, one active verdict only.
- findings: one entry per finding, in finding ID order.
- decisions: one entry per recorded decision, with the finding it resolves.
- next_check: the next step a resuming reviewer runs.
- status: `active`, `blocked`, or `finalized`.

## Finding entry

Each finding entry has:

- id: `F-001` upward, counted per record, never reused.
- severity: one of `blocker`, `major`, `minor`, `nit`.
- file and line: the exact location, or `unverified` when no location is confirmed.
- clause: the contract clause the finding violates, or `question` when none is confirmed.
- evidence: a direct quote of the line or command output that proves the finding.
- suggestion: one concrete fix, or the action that would verify an unverified finding.
- state: `open`, `resolved`, or `unverified`.

A finding with no contract clause and no evidence is a question, recorded with `clause: question` and `state: unverified`, never a blocker.

## Decision entry

Each decision entry has:

- id: `D-001` upward, counted per record, never reused.
- finding: the finding ID this decision resolves, or `none` for a scope decision.
- choice: the agreed resolution.
- reason: why the choice fits the contract.
- reversible: true or false.

## Block and sign-off

A `block` sets `status: blocked`, names the blocking finding, records its concrete fix, and stops further review. No sign-off may follow a block until the blocking finding is `resolved`.

A `sign-off` sets `verdict: sign-off`, requires zero open blocking findings, and records the merge decision. Open minor and nit findings may remain; the record reports both the verdict and the open count.

## Completion

The record is complete when `status` is `finalized` and the verdict, finding set, merge decision, and next action are all present. A blocked record is complete when it names the blocking finding and its concrete fix.
