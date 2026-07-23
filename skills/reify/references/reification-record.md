# Reification record

Load this reference when a reification spans turns, uses more than one source, or includes choices that may need to be reversed. The record keeps the user experience short while preserving enough state for another executor to resume.

## Required fields

- `signal`: the strongest useful phrase or need in the user's words.
- `outcome`: the one active concrete result.
- `done_means`: observable proof that the whole result is complete.
- `first_milestone`: the smallest useful result that tests the direction.
- `next_action`: the immediate safe action or named handoff owner.
- `sources_checked`: each source inspected and whether it was reachable.
- `constraints`: explicit limits, approvals, and safety boundaries.
- `open_questions`: only questions whose answers can change the outcome or next action.
- `status`: `active`, `finalized`, or `scrapped`.

## Decision entries

Give every accepted choice a stable ID such as `D-001`. Record the choice, the user's reason or observed signal, what depends on it, and whether it is reversible. A revert restores the state before that decision, marks later dependent choices for review, and leaves the old entry in the history.

## Progress entries

After each consequential step, append the object created, check performed, observed result, and next check. Do not claim a tool call, source read, write, message, publication, payment, deployment, or verification that did not occur.

## Resume check

Before continuing, confirm the record's active outcome still matches the user's latest instruction, each sensitive approval still covers the planned target and scope, and no unresolved question blocks the next safe action. If the latest instruction conflicts with the record, update the record and follow the latest instruction.
