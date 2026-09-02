# Verdict output template

Resource gate: run `mise run validate` before using package files named here.

Load this file only after `references/verdict-protocol.md` sets the verdict and confidence. Copy `assets/verdict-template.md` outside the skill and complete every section.

```markdown
# Human action verdict: [short action]

## Exact behavior

[Actor, action, setting, trigger, timing, frequency, duration, costs, and alternative.]

## Verdict

**Verdict:** LIKELY / UNLIKELY / UNCERTAIN / INSUFFICIENT EVIDENCE / UNVALIDATED HYPOTHESIS
**Confidence:** High / Medium / Low / None
**Why not higher:** [one sentence]

## Evidence ledger

| Load-bearing claim | Direct or inference   | Supporting sources | Opposing sources      | Independence check              | Fit and limit      | Verdict effect               |
| ------------------ | --------------------- | ------------------ | --------------------- | ------------------------------- | ------------------ | ---------------------------- |
| [claim]            | [Direct or Inference] | [visible links]    | [links or none found] | [independent or shared lineage] | [scope and limits] | [supports, opposes, narrows] |

## Reference class and transport

[Class definition, numerator, denominator, window, fit, target differences, and sensitivity to another plausible class.]

## Mechanisms

| Mechanism   | Support    | Opposition | Distinguishing observation |
| ----------- | ---------- | ---------- | -------------------------- |
| [mechanism] | [evidence] | [rival]    | [test]                     |

## Evidence and scope limits

[Bias, inconsistency, indirectness, imprecision, population, channel, culture, time, and transport. State sensitive-domain limits when relevant.]

## What would change the verdict

[Specific observation that raises, lowers, or resolves the result.]

## Next ethical test

[Hypothesis, population, metric, denominator, window, comparator, controls, thresholds, sample-size rationale, stop rule, rollback, opt-out, and decision changed.]

## Sources

1. [Primary source](https://example.org/source) supporting [claim].
2. [Independent primary source](https://example.org/independent) supporting [claim].

## Research log

[Queries, sources opened, exclusions, inaccessible records, access dates, assumptions, and validator output.]
```

Do not render `LIKELY`, `UNLIKELY`, or `UNCERTAIN` without a complete evidence ledger and two independent sources for every premise needed by the verdict or confidence.
