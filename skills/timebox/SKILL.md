---
name: timebox
description: 'Use when work must finish within a stated time limit.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
---

# Timebox

## When to use

Use this skill when the user gives both a complete task and a duration or exact deadline and requires the work plus decisive validation to finish inside that limit. An invocation may look like `/timebox 10 minutes fix and test the parser` or `/timebox by 16:00 EDT verify the release artifact`.

If the task or limit is missing, ask one concise question before starting. Resolve an ambiguous date, time, or zone before admission. Require a positive limit that yields one absolute deadline.

## Required composition

Before admission:

1. Load `always-current-datetime` and acquire a fresh clock anchor. Use its `captured_at` value as the start and calculate the absolute deadline with a tool.
2. Load `starting-point` and define the complete outcome, decisive proof, scope, authority, unknowns, and forbidden outcomes.
3. Load `outcome-bounded-work` and keep the full outcome and proof fixed while allowing a faster safe route.
4. Load `logic-audit` and check for conflicting scope, an impossible deadline, missing proof, or dependencies that cannot fit.

Stop with `contract-unavailable: <skill-name>` when a required skill cannot load. Do not replace current instructions with remembered text.

## Admission gate

Start only when the task, acceptance criteria, and deadline are unambiguous; every required input, permission, dependency, credential, and human decision is available or predictably bounded; each action and retry has a maximum duration; and the complete execution plan plus a protected validation reserve fits before the deadline.

If admission fails, return `TIMEBOX_NOT_STARTED`, name the failed condition, and request a longer limit or an explicit scope change. Do not begin work or promise completion from an unbounded estimate.

## Execution contract

1. Record the start, deadline, work cutoff, validation reserve, outcome, and decisive proof before the first work action. Use [`assets/timebox-record.json`](assets/timebox-record.json) as the field template and read [the timebox record](references/timebox-record.md) before creating the record.
2. Set the work cutoff to the deadline minus the protected validation reserve.
3. Choose the fastest route that preserves scope, quality, safety, and proof.
4. Before each action, compare its maximum duration with the remaining work budget. Do not start an action that can cross the work cutoff.
5. Set command and tool timeouts no later than the applicable cutoff. Avoid open-ended retries, waits, polls, and background work.
6. Count work as incomplete while it remains queued, delegated, pending approval, or unverified.
7. If a required step no longer fits, use a faster route only when it preserves the complete contract. Otherwise return `TIMEBOX_FAILED` immediately.
8. Begin decisive validation at the work cutoff or earlier. Implementation work may not consume the validation reserve.
9. Capture a completion timestamp after every decisive check passes. Never reset or extend the deadline because of latency, retry, clarification, or failure.

## Completion decisions

Return `TIMEBOX_PASS` only when the full accepted outcome is complete, every decisive validation check passed, final evidence was available before the absolute deadline, the completion timestamp is at or before the deadline, and no required work remains queued, delegated, pending approval, or unverified.

Return `TIMEBOX_FAILED` when execution began but any pass condition is unproved by the deadline. State completed work, validation run, remaining work, side effects, completion timestamp, and deadline. Late success remains a failure for that invocation.

Return `TIMEBOX_NOT_STARTED` when admission fails. This is the correct result when the requested guarantee cannot be supported inside the limit.

## Safety rules

- Never report implementation-only or partial progress as completion.
- Never count queue submission, dispatch, acknowledgment, or a background process as completed work.
- Never weaken, skip, or move validation after the deadline to manufacture a pass.
- Never conceal a deadline miss or rush an irreversible or sensitive action.
- Preserve safe intermediate state and report it when stopping.
- Treat a new or changed task as a new timebox requiring a fresh user-stated limit.

## Output

At admission, state the start, deadline, complete outcome, decisive validation, and protected validation reserve. At closeout, lead with `TIMEBOX_PASS`, `TIMEBOX_FAILED`, or `TIMEBOX_NOT_STARTED`, then provide the completion timestamp, deadline, evidence, and remaining work.

## Resources

- Read [the timebox record](references/timebox-record.md) before recording admission or closeout fields.
- Use `assets/timebox-record.json` as the machine-readable field template.
- Use `examples/` for admitted, rejected, and passed response shapes.
- Use `evals/` for trigger, rejection, behavior, failure, recovery, and speed cases.
- Run `mise run ci` from this skill directory to execute `scripts/` and `scripts/tests/` checks.
