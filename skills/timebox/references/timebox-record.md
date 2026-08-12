# Timebox record

This reference owns the record fields used at admission and closeout. The main skill owns admission, execution, and decision rules and links here.

## Admission fields

- `start`: The fresh `captured_at` anchor.
- `deadline`: The calculated absolute deadline with timezone.
- `work_cutoff`: The latest time implementation may continue.
- `validation_reserve_seconds`: Time protected for decisive validation, inspection, and the completion timestamp.
- `outcome`: The complete accepted result.
- `proof`: The decisive validation evidence.
- `action_bounds`: Maximum duration for each action, retry, or wait.

## Closeout fields

- `decision`: `TIMEBOX_PASS`, `TIMEBOX_FAILED`, or `TIMEBOX_NOT_STARTED`.
- `completion_timestamp`: A fresh timestamp captured after decisive validation, or `null` when completion was not proved.
- `evidence`: The validation commands, outputs, inspected results, and artifact identities that decide completion.
- `remaining_work`: Work still incomplete, queued, delegated, pending approval, or unverified.
- `side_effects`: State changed before closeout.

## Validation

Reject a record with a missing start, deadline, work cutoff, validation reserve, outcome, proof, or decision. A pass also requires nonempty evidence, no remaining work, and a completion timestamp at or before the deadline.
