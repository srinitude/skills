# Blocked source drift

## Request

Apply an approved wording map to a policy file.

## Finding

The live source hash differs from the recorded baseline, and the change is not explained by the task packet.

## Result

Return `BLOCKED`. Do not reconstruct the old source, apply stale targets, or claim partial rewrite success. Rebuild the baseline and ledger from the current authorized source before editing.
