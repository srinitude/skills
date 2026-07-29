# Verdict protocol

Use this protocol before issuing a substantive agent-action verdict.

## Source card

Complete one card for every source that changes the verdict:

```text
Claim used:
Source type and primary-record status:
Authors, task set, and dataset:
System, prompts, runtime, tools, permissions, state, and versions:
Tasks, environment, horizon, dependencies, and threat conditions:
Eligible tasks, attempts, trials, exclusions, and dropped runs:
Metric definition, including k for pass@k or pass^k:
Outcome, trace, constraint, and infrastructure graders:
Result and uncertainty:
Failure handling:
Leakage and overlap:
Independence from other sources:
Transport match and differences from [a]:
Limit:
Visible URL and access date:
```

A summary, comparison, announcement, or paper that restates another run set is not an independent source.

## Target trace card

Record the system version, opportunity rule, eligible denominator, task selection, requested action, tool payload, response, final state, independent readback and timestamp, permission and approval status, retries, fallbacks, checkpoints, handoffs, token and time budgets, cost and latency, dependency failures, missing traces, and interventions during the window.

Target traces are strongest only after this audit. Operational reliability retains infrastructure failures, even when a model-only diagnostic reports them separately.

## Evidence classes

1. **Target outcomes:** the pinned system on target tasks with independent state readback.
2. **Target traces:** process, tool, policy, cost, and failure evidence from those outcomes.
3. **Matched end-to-end analogs:** a different system or environment with an explicit transport argument.
4. **Component evidence:** one model, tool, grader, retrieval, or constraint check.
5. **Mechanism evidence:** evidence for a proposed success or failure path.
6. **Inference:** a reasoned bridge that was not directly observed.

A component check cannot prove the full action. A target trace can mislead when its denominator, grader, or retention is biased.

## Independence and transport gates

Every premise needed by the verdict or confidence requires two independent teams, task sets, or datasets. Independence fails when sources share runs, tasks, simulators, production windows, leaked answers, unvalidated judges, or one analysis pipeline. Match the reference class on action, tasks, horizon, tools, permissions, state, runtime, model version, environment, graders, budgets, failures, threat conditions, and time.

## Trial rules

Prespecify unique tasks, independent trials, reset procedure, sampling settings, retries, best-of selection, fallbacks, eligible denominator, failure treatment, metric definitions, uncertainty method, success and invalid-run rules, subgroup comparisons, holdout, and contamination controls. Keep model-caused and infrastructure-caused views separate while retaining both in the operational result.

## Grader stack

- **Outcome grader:** independent environment state or deterministic artifact check.
- **Trace grader:** tool choice, arguments, ordering, recovery, handoff, verification, and stopping.
- **Constraint grader:** policy, permission, privacy, side effects, and approval rules.
- **Security grader:** the defined unsafe action under a stated threat model.
- **Efficiency grader:** cost, tokens, latency, calls, retries, and resources.
- **Infrastructure grader:** transport, dependency, credential, rate-limit, and runtime health.

Validate judgment-based graders against a blinded human or deterministic gold sample. Record disagreement and adjudication. A good trace cannot replace a failed outcome, and nominal utility cannot erase a constraint failure.

## Verdicts

| Verdict                  | Use when                                                                                                                                                                   |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `LIKELY`                 | Repeated direct or closely matched evidence supports `[a]`, load-bearing premises pass independence, graders fit the decision, and no unresolved contradiction changes it. |
| `UNLIKELY`               | Repeated matched evidence shows non-action or failure under comparable opportunity and cost, with the same independence and grader requirements.                           |
| `UNCERTAIN`              | Credible evidence conflicts, uncertainty crosses the decision threshold, or material system or task strata differ.                                                         |
| `INSUFFICIENT EVIDENCE`  | Live sources exist, but directness, independence, denominator, grader validity, trials, or transport is too weak for a direction.                                          |
| `UNVALIDATED HYPOTHESIS` | Live research was unavailable or prohibited. The output contains assumptions and a test, not a validated verdict.                                                          |

## Confidence

High confidence needs repeated target outcomes, independent readback, fit graders, visible failures, corroboration, and close deployment match. Medium confidence allows repeated matched analogs and bounded transport gaps. Low confidence applies when component checks, demos, claims, sparse trials, weak graders, or large transport gaps dominate. `INSUFFICIENT EVIDENCE` and `UNVALIDATED HYPOTHESIS` have no confidence.

Confidence cannot exceed the weakest premise, outcome grader, independence check, or transport bridge.

## Next safe test

Use representative frozen tasks and a disjoint holdout, the target tool and verification friction, least-privileged test credentials, approved or synthetic data, reversible or fake side effects, fit graders, prespecified trials and thresholds, adversarial and dependency-failure cases where relevant, idempotency, budgets, timeouts, a kill switch, readback, rollback, cleanup, and human approval where the real action requires it.

Never add authority merely to make an evaluation realistic.

## Final check

- The verdict matches the evidence state.
- System and task strata with different outcomes are separate.
- Every load-bearing premise passes independence.
- Outcome, trace, constraints, infrastructure, and efficiency remain separate.
- Trial and denominator rules were set before results.
- The next test uses the least authority needed.
- Every load-bearing source has a visible URL.
