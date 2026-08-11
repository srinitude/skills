# Validation contract

Parent and backlink: [`../SKILL.md`](../SKILL.md), Procedure step 5.

## Required artifacts

A governed rewrite normally records a baseline, meaning ledger, voice scan, machine validation report, and human validation table. Add source inventory, context checks, or a review packet only when the claim requires them.

## Review packet

When a separate review is justified:

1. Freeze the exact live files, backups, ledger, scans, and current reports in scope.
2. Record packet and per-file hashes before dispatch.
3. Name every required check and in-scope path.
4. Give the reviewer read-only search and file access.
5. Require a disk recount of ledger IDs and test cases.
6. Save `PASS` or `BLOCKED`, the tool boundary, checks, failures, and required fixes.
7. After any fix, rebuild the packet and rerun review.

If the main-progress gate rejects waiting and no user, approval contract, or external standard requires separation, perform the same checks in the main worker. Label the review non-independent and keep that label in the final report.

## Closeout order

1. Complete the selected review path.
2. Update the machine report with separate component and whole-change results.
3. Update the human report to match the machine facts.
4. Run the final prose-only voice scan over governed files and report strings.
5. Cross-check report agreement, source hashes, ledger targets, packet integrity when used, secret safety, and temporary-file cleanup.
6. Rescan prose after any post-scan wording change.

## Honest labels

Focused JSON, hash, and prose checks are focused ad-hoc validation. A read-only separate review is independent. A main-worker review is non-independent. Neither is whole-suite CI. A component result cannot prove the full rewrite or deployed outcome.
