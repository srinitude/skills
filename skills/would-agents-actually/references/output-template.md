# Verdict output template

Load this file only after `references/verdict-protocol.md` sets the verdict and confidence. Copy `assets/verdict-template.md` outside the skill and complete every section.

```markdown
# Agent action verdict: [short action]

## Exact action

[Opportunity, pinned system, observable action or abstention, tasks, environment, window, budgets, friction, comparator, and readback.]

## Verdict

**Verdict:** LIKELY / UNLIKELY / UNCERTAIN / INSUFFICIENT EVIDENCE / UNVALIDATED HYPOTHESIS
**Confidence:** High / Medium / Low / None
**Scope:** [system, tasks, environment, and window]

## Pinned system card

- Model identifier and version:
- Provider route and sampling:
- Prompt and runtime versions:
- Planner, router, verifier, retries, and fallbacks:
- Tools, schemas, permissions, and approvals:
- Memory, retrieval, context, and checkpoints:
- Environment, dependencies, and task sampling:
- Budgets, concurrency, horizon, and stop rules:
- Comparator and success readback:

## Evidence ledger

| Conclusion | Direct or inference   | Evidence class                                        | System and tasks | Metric and denominator | Independent support | Bias and transport limits | Verdict effect         |
| ---------- | --------------------- | ----------------------------------------------------- | ---------------- | ---------------------- | ------------------- | ------------------------- | ---------------------- |
| [claim]    | [Direct or Inference] | [target outcome, trace, analog, component, mechanism] | [match]          | [definition]           | [teams or datasets] | [limits]                  | [raises, lowers, none] |

## Trial metrics

| Metric             | Definition                        | Tasks | Trials | Result and uncertainty | Failure treatment |
| ------------------ | --------------------------------- | ----: | -----: | ---------------------- | ----------------- |
| Single-run outcome | [full outcome plus constraints]   |   [n] |    [n] | [result]               | [rule]            |
| Propensity         | [action per eligible opportunity] |   [n] |    [n] | [result]               | [rule]            |
| pass@k or pass^k   | [exact k and reset]               |   [n] |    [n] | [result]               | [rule]            |
| Cost and latency   | [scope]                           |   [n] |    [n] | [result]               | [rule]            |

## Outcome, trace, and constraints

- Environment outcome and readback:
- Trace, recovery, handoff, verification, and stop behavior:
- Constraint and safety checks:
- Grader validation and disagreements:
- Infrastructure status:

## Outside view and transport

[Reference class, closest evidence, nearest excluded evidence, task and system gaps, leakage, overlap, and expected transport error.]

## Mechanisms

| Mechanism   | Direction          | Evidence  | Competing explanation | Separating observation |
| ----------- | ------------------ | --------- | --------------------- | ---------------------- |
| [mechanism] | [raises or lowers] | [support] | [rival]               | [test]                 |

## Limits and safety boundary

[What the verdict does not establish. In a sensitive domain, state that this is an action verdict only and does not establish safety, efficacy, legality, entitlement, authorization, compliance, or permission to act.]

## What would change the verdict

[Evidence that raises, lowers, or resolves it.]

## Next safe test

[System, tasks, holdout, trials, denominator, reset, graders, budgets, permissions, approvals, faults, stop rules, readback, rollback, cleanup, thresholds, and decision changed.]

## Sources

1. [Primary source](https://example.org/source) supporting [claim].
2. [Independent primary source](https://example.org/independent) supporting [claim].

## Research log

[Queries, sources opened, exclusions, system pins, run identity, failures, access dates, assumptions, and validator output.]
```
