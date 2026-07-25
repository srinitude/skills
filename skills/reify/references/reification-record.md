# Reification record

Load this reference when a reification spans turns, uses more than one source, or includes choices that may need to be reversed. The record keeps the user experience short while preserving enough state for another executor to resume.

## Where the record lives

Write the record to `./reify-log-<slug>.md` in the directory the user is working in, where `<slug>` is two or three lowercase words from the signal joined by hyphens, for example `./reify-log-lighthouse-summers.md`. Print the absolute path once when the file is created so the user can find it later. One record holds one active reification. When the directory already holds a record for a different signal, create a second file with its own slug instead of appending to the first. `continue <record>` takes that exact relative path as its argument, for example `continue reify-log-lighthouse-summers.md`. When no path is given and exactly one record file exists in the directory, resume that one. When several exist, list them and ask which one, then stop.

## Required fields

The record header and the JSON brief carry the same ten fields, so a record converts to a brief without invention.

- `signal`: the strongest useful phrase or need in the user's words.
- `outcome`: the one active concrete result.
- `done_means`: observable proof that the whole result is complete.
- `first_milestone`: the smallest useful result that tests the direction.
- `next_action`: the immediate safe action or named handoff owner.
- `sources_checked`: each source inspected and whether it was reachable.
- `constraints`: explicit limits, approvals, and safety boundaries.
- `decisions`: every accepted choice, as entries in the shape below.
- `open_questions`: only questions whose answers can change the outcome or next action.
- `status`: `active`, `finalized`, or `scrapped`.

## Decision entries

Every accepted choice gets an ID matching `^D-[0-9]{3}$`. IDs are per record, start at `D-001`, increase by one, and are never reused, not even after a revert. Record the choice, the user's reason or observed signal, the IDs that depend on it, whether it is reversible, and a state of `accepted`, `superseded`, or `reverted`. A superseded choice keeps its ID and gains a `superseded by D-0NN` line; it is never deleted or renumbered. In the JSON brief the same entry is an object: `{"id": "D-001", "choice": "...", "reason": "...", "dependents": ["D-003"], "reversible": true}`.

## Revert semantics

`revert D-0NN` performs these five moves in order, then reports them.

1. Set that entry's state to `reverted` and leave the entry in place with its original text.
2. Set every entry listing it in `dependents` to `needs-review` and name them in the reply.
3. Reopen the record fields that the reverted choice set, which usually means `outcome`, `done_means`, `first_milestone`, or `next_action`, and mark each reopened field `undecided`.
4. Move every file created under that choice into `./superseded/` beside the record, keeping the file name, and log the old and new paths. Never delete a file during a revert.
5. Append a progress entry naming the reverted ID, the reviewed dependents, the moved files, and the next check.

The next new choice takes the next unused number, so a revert of `D-002` when `D-003` exists means the next entry is `D-004`.

## Probe lifecycle

A probe object is a small file written to test a direction. When a later object absorbs or replaces it, move the probe into `./superseded/` in the same turn, name the replacement in the log, and never leave two live files that open with the same text.

## Progress entries

After each consequential step, append the object created, check performed, observed result, and next check. Do not claim a tool call, source read, write, message, publication, payment, deployment, or verification that did not occur.

## Finalized against milestone met

These are two separate states and the record shows both. `status: finalized` means one outcome is named, the completion proof is stated, and either a verified artifact exists or a brief passes the validator. The first milestone is met only when its own observable proof happened. When the milestone depends on another person, write `status: finalized` plus a `milestone: open, closes when <person> <does the thing>` line, and say both parts in the reply.

## Resume check

Before continuing, confirm the record's active outcome still matches the user's latest instruction, each sensitive approval still covers the planned target and scope, and no unresolved question blocks the next safe action. If the latest instruction conflicts with the record, update the record and follow the latest instruction.
