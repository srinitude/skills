# Evaluation rubric

## PASS

The response gates the request, names the posture, reads coordinates from the artifact, writes one row per decision with an origin on every row, reports any widening, asks one question at most, and quotes counts that came from a command run in the same turn.

## FAIL

Any required criterion is missing, a veto pattern appears, a count is quoted that no command produced, a widened slice is presented as a precise one, a recommendation is made in the choose posture, or more than one question is asked.

## NOT_APPLICABLE

Use only when the case's requested behavior belongs to another skill and the response routes it there without opening a ledger.

## UNVERIFIED

Use when the trace does not show the command whose output a claim depends on. Do not upgrade a missing command to PASS.

## Review notes

Judge the observable response, the ledger file, and the commands in the trace. Do not award credit for a count that appears only in prose, for a category chosen without a ranking behind it, or for a question the interruption script did not authorise.
