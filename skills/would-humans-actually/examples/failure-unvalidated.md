# Example: fail closed without live research

## User says

```text
Do not browse. Say whether people will use my idea.
```

## Executor replies

```text
Verdict: UNVALIDATED HYPOTHESIS. The behavior is undefined and live research was prohibited. I recorded the missing inputs and a safe next test instead of presenting a validated direction.
```

## Commands run

```text
$ mise run validate-verdict --input ../../.artifacts/example-runs/human-unvalidated.md
{"errors": [], "input": "../../.artifacts/example-runs/human-unvalidated.md", "status": "PASS"}
exit 0
```

## Files created

Resource gate: run `mise run validate` before using package files named here.

`../../.artifacts/example-runs/human-unvalidated.md`

```markdown
# Human action verdict: unresolved idea use

## Exact behavior

The actor, observable action, setting, trigger, timing, frequency, duration, costs, and current alternative were not provided. The phrase "use my idea" is not an observable behavior specification.

## Verdict

**Verdict:** UNVALIDATED HYPOTHESIS
**Confidence:** None
**Why not higher:** Live research was prohibited and the behavior is undefined.

## Evidence ledger

No load-bearing evidence was collected because the user prohibited live research.

## Reference class and transport

No reference class can be selected until the population, action, setting, costs, alternative, and observation window are defined.

## Mechanisms

Potential motivation, capability, opportunity, cue, friction, privacy, habit, and switching mechanisms remain assumptions.

## Evidence and scope limits

This is not a validated behavior verdict. It establishes no prevalence, probability, demand, purchase, adoption, retention, safety, legality, or efficacy.

## What would change the verdict

A precise behavior definition and access to current primary sources would permit a real evidence check.

## Next ethical test

First define the population, observable action, setting, real cost, alternative, denominator, and window. Then prespecify a consented and reversible test with thresholds, stop rules, privacy controls, opt-out, and the decision changed.

## Sources

No live sources were inspected because the user prohibited research.

## Research log

Research status: NOT_RUN_PROHIBITED. Missing inputs: population, observable action, setting, costs, alternative, and window. Validator output is recorded in the example run.
```

## What the run proves

The completed artifact follows the public contract and the bundled validator exits 0 with `"status": "PASS"`.
