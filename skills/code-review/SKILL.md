---
name: code-review
description: 'Use when code is complete and needs a structured review for defects, contract gaps, and merge readiness before it is committed, pushed, or merged.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
---

# Code review

Review completed code against its contract before it merges. Produce one review record that separates verified findings from guesses, blocks merge on real defects, and leaves the next reviewer a resume point. Keep the exchange with the author short; move evidence into the record and the files.

## Which commands does this skill accept?

Interpret a plain request as `review` unless a prior review record clearly applies.

| Command             | Result                                                                         |
| ------------------- | ------------------------------------------------------------------------------ |
| `help`              | Show these commands and the current record state.                              |
| `review <target>`   | Review a target path, commit, or pull request against its acceptance contract. |
| `continue <record>` | Resume a saved review without repeating settled findings.                      |
| `block <reason>`    | Record a blocking defect, mark the record blocked, and stop.                   |
| `sign-off`          | Record that no open blocking defects remain and the target is merge ready.     |

A finding ID matches `^F-[0-9]{3}$`, counts up per record from `F-001`, and is never reused. A record path looks like `review-log-parser-refactor.md`.

If the request matches no command and intent cannot be inferred from context, ask one short question and stop. Do not guess at a merge decision, a deploy target, or a recipient the contract does not name.

## How does a review work?

Use this full plan. After each consequential step, run the stated check and fix a failed check before moving on. Keep every author-facing reply at or below 350 words; move detail into the record and the files instead of the reply.

1. Resolve the target. Accept a path, a commit, a branch, or a pull request identifier. Read the acceptance contract from the target itself: its tests, its task or issue description, and any linked specification. If no contract is named and none can be inferred from tests, ask for the one acceptance criterion that decides merge and stop. Check: one named target and one named acceptance contract are explicit.
2. Check for an active record. Inspect reachable conversation, files, notes, and task systems before asking the author to repeat findings. If one missing fact would change the verdict, ask for only that fact and stop. Check: the current target and contract boundary are explicit.
3. Create or resume the record at `./review-log-<slug>.md` in the directory the author is working in, as [the review record](references/review-record.md) defines, and print its absolute path once. Append the target, contract, findings, decisions, and next check after each remaining step. Check: another reviewer could resume without asking settled questions again.
4. Run the target's own checks first. Execute its test suite, linters, type checks, and build with the exact command the contract names, and capture real command output with exit codes. Never report a check result from memory. If a check command is unknown, ask for it and stop. Check: every claimed pass is backed by fresh output in the record.
5. Map findings to severity. For each defect, assign one of `blocker`, `major`, `minor`, or `nit`, state the file and line, the contract clause it violates, and the evidence. A finding with no contract clause and no evidence is a question, not a finding. Check: every finding names a contract clause and evidence.
6. Separate verified findings from guesses. Quote the line or output that proves a finding. Mark any claim you did not directly observe as `unverified` and state what would verify it. Never present a plausible inference as a confirmed defect. Check: no finding asserts a defect without direct evidence.
7. Redteam the diff. Read the change as an adversary: look for the case the tests do not cover, the input that breaks an assumption, the side effect the contract forbids, and the revert path a broken change needs. Record each as a finding only when it violates a contract clause. Check: at least one adversarial read is recorded.
8. Record each finding with a finding ID, severity, file, line, contract clause, evidence, and a concrete suggested fix. For `block`, set `status: blocked` on the record, name the blocking finding, and stop. For `sign-off`, confirm zero open blocking findings and record the verdict. Check: the record explains the current state without hidden findings.
9. Converge after one to three exchanges unless the author asks to keep investigating. State the verdict, the count of findings by severity, the merge decision, and the next action. Check: only one verdict is active.
10. When the review must pass to another reviewer, copy the template out of the skill and validate the copy. Never edit files inside the installed skill. Set `SKILL_DIR` to the absolute path of this skill directory, then run `cp "$SKILL_DIR/assets/review-checklist.json" ./CHECKLIST.json`, fill `./CHECKLIST.json` with the review record fields, and run `python3 "$SKILL_DIR/scripts/validate_checklist.py" ./CHECKLIST.json`. Exit 0 is required. On exit 1 the checklist is wrong: fix every reported field and rerun. On exit 2 the command is wrong, not the checklist: recheck `SKILL_DIR`, use the absolute script path, and rerun. Check: target, contract, verdict, findings, and status are present and the report reads `"status": "PASS"`.
11. Finalize with either a signed-off review or a blocked record with the exact unblocking fix. Report `status: finalized` and the open finding count as two separate sentences when findings remain open. Check: the result names what was verified, what blocks merge, and what remains.

## What goes in the record?

Read [the review record](references/review-record.md) when work spans turns, uses multiple sources, or contains findings that may be disputed. It owns the record path, the required fields, the finding ID format, and block and sign-off semantics. Read [the generation contract](references/generation-contract.md) before changing this skill's structure or support files.

Load `assets/review-checklist.json` only when a structured handoff is needed, and copy it out before filling it. Load `scripts/validate_checklist.py` to check that handoff. Load `scripts/tests/` only when changing script behavior, and run the tests before implementation changes. Load `evals/` when measuring activation, behavior, failure handling, recovery, or timing.

## Which worked example should you read?

Each file in `examples/` is one complete run with real command output. Read the one that matches the move you are about to make.

- `examples/help-command.md` when the user types `help` or asks what this skill can do.
- `examples/clean-sign-off.md` when a change passes every check and you need the sign-off record and the validated checklist.
- `examples/block-on-defect.md` when a real defect blocks merge and the record must stop at `block`.
- `examples/unverified-guess.md` before recording a finding you did not directly observe. This is the failure this skill causes most often.
- `examples/continue-review.md` when resuming a saved review, including the case where the directory holds more than one.

## Gotchas

- Do not report a passing test suite as merge ready when the contract names a check the suite does not cover.
- Do not turn an unverified suspicion into a blocker. Mark it `unverified` and state what would confirm it.
- Do not invent a contract clause to justify a stylistic preference. A nit is a nit; it does not block.
- Do not skip the adversarial read when the tests pass. Passing tests are the moment to look for the case they miss.
- Do not hide a broken change behind a sign-off. Record the defect, set `blocked`, and name the unblocking fix.
- Do not claim a check ran when only its command was typed. Capture real output and exit codes in the record.

## Limitations

Code review cannot prove the absence of all defects, authorize a merge the contract forbids, or supply an acceptance criterion the target never named. It can still preserve the contract gap, keep findings reversible, and produce a handoff with the exact missing input.

## When is a review complete?

A review is complete only when one named target has an agreed verdict, a finding set by severity, a merge decision, and either a signed-off record or a blocked record with the exact unblocking fix. A signed-off review may still carry open minor or nit findings; report both the verdict and the open count. A blocked review is complete when the record reads `status: blocked` and the blocking finding names a concrete fix.
