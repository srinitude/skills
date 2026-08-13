---
name: timebox
description: 'Use when work must finish within a stated time limit.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.1'
---

# Timebox

## Outcome

Complete the user's full requested work and its decisive validation within the stated limit. This is a hard acceptance constraint, not a request to make partial progress for a while. Only work that is complete, validated, and timestamped before the deadline may pass.

## When to use

Use when the user invokes `/timebox` with both a task and a duration or exact deadline, for example `/timebox 10 minutes fix and test the parser` or `/timebox by 16:00 EDT verify the release artifact`.

If the task or limit is missing, ask one concise question before starting. Resolve ambiguous dates or times through `always-current-datetime`. The limit must be positive and precise enough to compute one absolute deadline.

## Required composition

Before admitting the work:

1. Load `always-current-datetime` and acquire its fresh local clock anchor. Its `captured_at` value is the timebox start. Compute the absolute deadline from that anchor with a tool, not mental arithmetic.
2. Load `starting-point`. Define the complete outcome, decisive proof, scope, authority, unknowns, and forbidden outcomes.
3. Load `outcome-bounded-work`. Keep the full outcome and proof fixed while allowing a faster safe route.
4. Load `logic-audit`. Check for conflicting scope, an impossible deadline, missing proof, and dependencies that cannot fit.

Stop with `contract-unavailable: <skill-name>` if a required skill cannot load. Never replace its current instructions with remembered text.

## Admission gate

Admit the timebox only when all of these are true:

- The task, acceptance criteria, and deadline are unambiguous.
- Every required permission, input, credential, dependency, and human decision is already available or has a proven bound that fits.
- The chosen route preserves the full requested scope, safety rules, and decisive validation.
- Each tool call, command, retry, and external wait has an explicit maximum duration.
- A protected validation reserve covers the decisive checks, result inspection, and completion timestamp.
- The bounded execution plan plus the validation reserve fits before the deadline.

If any condition fails, do not begin. Return `TIMEBOX_NOT_STARTED`, name the failed admission condition, and request either a longer limit or an explicit scope change. Never promise guaranteed completion from an unbounded estimate.

## Execution contract

1. Record the start, absolute deadline, work cutoff, validation reserve, outcome, and proof before the first work action.
2. Work backward from the deadline. The work cutoff is the deadline minus the protected validation reserve.
3. Choose the fastest route that preserves every accepted requirement. Do not silently reduce scope, quality, safety, or proof.
4. Before each action, compare its maximum duration with the remaining work budget. Do not start an action that can cross the work cutoff.
5. Set command and tool timeouts no later than the applicable cutoff. Avoid open-ended retries, waits, polls, and background work.
6. Count subagents, queued jobs, approvals, restarts, and remote processing as incomplete until their final evidence is available inside the timebox.
7. If a required step no longer fits, use a faster route only when it preserves the full contract. Otherwise stop and report `TIMEBOX_FAILED` immediately.
8. Begin decisive validation at the work cutoff or earlier. No implementation work may consume the protected validation reserve.
9. Capture a completion timestamp after every decisive check passes. Do not reset or extend the deadline because of retries, clarification, tool latency, or failure.

## Completion decisions

Return `TIMEBOX_PASS` only when all of these are proved:

- The full accepted outcome is complete.
- Every decisive validation check passed.
- Final evidence was available before the absolute deadline.
- The completion timestamp is at or before the deadline.
- No required work remains queued, delegated, pending approval, or unverified.

Return `TIMEBOX_FAILED` when execution began but any condition is unproved by the deadline. State completed work, validation run, remaining work, side effects, and the exact time result without describing partial progress as completion.

Return `TIMEBOX_NOT_STARTED` when admission fails. This is the correct result when the requested guarantee cannot be supported within the limit.

## Failure and safety rules

- Never claim success because the main edit finished while tests or inspection remained.
- Never count queue submission, dispatch, a tool acknowledgment, or a background process as completed work.
- Never skip, weaken, or move validation beyond the deadline to manufacture a pass.
- Never conceal a deadline miss. Late success is still `TIMEBOX_FAILED` for that invocation.
- Preserve safe intermediate state and report it when stopping. Do not rush irreversible or sensitive actions to beat the clock.
- A new or changed task invalidates admission. Start a new timebox only from a fresh user-specified limit.

## Output

At admission, state the start, deadline, full outcome, decisive validation, and protected validation reserve. At closeout, lead with `TIMEBOX_PASS`, `TIMEBOX_FAILED`, or `TIMEBOX_NOT_STARTED`, then give the completion timestamp, deadline, evidence, and any remaining work.

## Progressive disclosure

`PD-101`: `evals/cases.json` owns objective pressure cases and acceptance. Load it before testing, reviewing, or changing this skill. This file owns runtime behavior and links to that evaluation owner.

## Verification

- The clock anchor came from the current `always-current-datetime` instructions.
- Admission covered the full task and validation, not implementation alone.
- The absolute deadline and validation reserve were computed before work.
- Every action was bounded to finish before its cutoff.
- PASS requires completion, decisive validation, and final evidence inside the limit.
- Partial, queued, late, or unvalidated work cannot pass.

## Resources

- Read [the timebox record](references/timebox-record.md) before recording admission or closeout fields.
- Use `assets/timebox-record.json` as the machine-readable field template.
- Use `examples/` for admitted, rejected, and passed response shapes.
- Run `mise run ci` from this skill directory to execute `scripts/` and `scripts/tests/` checks.
