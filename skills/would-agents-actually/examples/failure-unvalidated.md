# Example: fail closed without a system pin or live evidence

## User says

```text
Do not inspect sources or run trials. Tell me whether this agent will delete the right records.
```

## Executor replies

```text
Verdict: UNVALIDATED HYPOTHESIS. The system and action are unpinned, and source inspection and trials were prohibited. I recorded a least-privileged sandbox test instead of a validated direction.
```

## Commands run

```text
$ mise run validate-verdict --input ../../.artifacts/example-runs/agent-unvalidated.md
{"errors": [], "input": "../../.artifacts/example-runs/agent-unvalidated.md", "status": "PASS"}
exit 0
```

## Files created

Resource gate: run `mise run validate` before using package files named here.

`../../.artifacts/example-runs/agent-unvalidated.md`

```markdown
# Agent action verdict: unresolved destructive action

## Exact action

The system, trigger, observable action, tasks, environment, permissions, window, budgets, comparator, and independent readback were not supplied. The user prohibited source inspection and trials.

## Verdict

**Verdict:** UNVALIDATED HYPOTHESIS
**Confidence:** None
**Scope:** An unpinned system and undefined destructive action with no live evidence.

## Pinned system card

No versioned system card is available. Model identifier, provider route, prompts, runtime, tools, permissions, memory, environment, retries, fallbacks, tasks, and budgets remain unknown.

## Evidence ledger

No load-bearing source or target trace was collected because research and trials were prohibited.

## Trial metrics

No eligible tasks, attempts, trials, resets, failures, costs, or latency were observed.

## Outcome, trace, and constraints

No environment state, tool trace, permission check, grader result, or infrastructure record exists.

## Outside view and transport

No matched reference class can be selected without a pinned action, system, task distribution, environment, and grader.

## Mechanisms

Potential grounding, planning, tool, permission, recovery, verification, stopping, and transport mechanisms remain assumptions.

## Limits and safety boundary

This is not a validated agent-action verdict. It establishes no capability, propensity, reliability, compliance, safety, authorization, or permission to act.

## What would change the verdict

A precise system pin, current primary-source access, and a least-privileged sandbox trial could create assessable evidence.

## Next safe test

Use synthetic records in an isolated sandbox with least-privileged credentials, no production access, representative frozen tasks, prespecified trials and denominator, deterministic state and permission graders, budgets, timeouts, a kill switch, idempotency, readback, rollback, and cleanup.

## Sources

No live sources were inspected because the user prohibited research.

## Research log

Research status: NOT_RUN_PROHIBITED. Missing inputs: system pin, action, tasks, environment, permissions, window, budgets, comparator, and readback. Validator output is recorded in the example run.
```

## What the run proves

The completed artifact follows the public contract and the bundled validator exits 0 with `"status": "PASS"`.
