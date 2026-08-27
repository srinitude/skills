# Evaluation contract

Backlink: [SKILL.md](../SKILL.md). Load before testing or changing the public skill.

## Acceptance

Run each case twice with the skill and twice without it. The with-skill run must return the named deterministic release state, preserve the smallest-first breakpoint order, enforce every veto, and leave the native evidence packet unchanged. The without-skill condition must fail at least one required assertion for each behavior case.

## Trigger gate

All positive trigger cases must activate. Every hard negative and near neighbor must remain inactive. A false positive, missed positive, source hash mismatch, prompt-corpus mismatch, or wrong fixture state is `BLOCKED`.

## Evidence

Keep fixture output, command, exit code, source manifest digest, public prompt manifest digest, and replay hashes separate from any model-backed judgment. Component PASS does not prove repository CI.
