# Verdict protocol

Use this protocol after defining `[x]` and before issuing a substantive verdict.

## Source card

Complete one card for every source that changes the verdict:

```text
Claim used:
Citation, publisher, date, URL, and retrieval result:
Evidence type:
Direct or inference:
Population and setting:
Observed outcome and window:
Design, sample, comparator, attrition:
Estimate and uncertainty:
Fit to [x]: direct / close / distant / mechanism only
Bias and quality concerns:
Transport concerns:
Underlying study or dataset; independence and overlap:
Verdict impact: supports / opposes / narrows / no effect
```

A source cannot carry the verdict when its primary record, denominator, outcome, or relevant limitation cannot be checked.

## Evidence classes

1. **Observed target behavior:** the defined population performs `[x]` under the target setting and cost.
2. **Close-analog behavior:** a matched population or action differs on stated dimensions.
3. **Experimental behavior:** an intervention changes observed action under a declared design.
4. **Self-report:** a person reports past action or current state.
5. **Stated evidence:** intention, preference, approval, willingness, or forecast.
6. **Mechanism evidence:** evidence about a proposed causal path.
7. **Inference:** a reasoned bridge that was not directly observed.

Keep these classes separate. A later stage cannot be inferred from an earlier one.

## Quality and independence gate

Check selection, assignment, measurement, reporting, attrition, inconsistency, indirectness, imprecision, missing denominators, publication bias, time drift, cultural mismatch, channel mismatch, institutional mismatch, conflicts of interest, and transport. Every premise needed for verdict or confidence requires two independent author teams or datasets. Two summaries, papers, or posts using one study, dataset, or event count once.

## Verdicts

| Verdict                  | Use when                                                                                                                       |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `LIKELY`                 | The best direct or closely matched evidence supports `[x]`, opposing evidence is weaker, and transport is credible.            |
| `UNLIKELY`               | The best matched evidence shows low completion under comparable costs or a binding barrier without a supported countermeasure. |
| `UNCERTAIN`              | Credible evidence conflicts, differs by segment, or leaves the deciding mechanism unresolved.                                  |
| `INSUFFICIENT EVIDENCE`  | Live evidence exists, but directness, independence, denominator, measurement, or transport is too weak for a direction.        |
| `UNVALIDATED HYPOTHESIS` | Live research was unavailable or prohibited. The output contains assumptions and a test, not a validated verdict.              |

Split by segment when one label would hide a material difference.

## Confidence

| Confidence | Minimum basis                                                                                                                  |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------ |
| High       | Credible observed target behavior or repeated close field evidence, independent support, and little unresolved transport risk. |
| Medium     | Consistent close evidence and a defensible reference class with bounded indirectness.                                          |
| Low        | Self-report, distant analogs, mechanisms, conflict, or transport gaps dominate.                                                |
| None       | The verdict is `INSUFFICIENT EVIDENCE` or `UNVALIDATED HYPOTHESIS`.                                                            |

Confidence cannot exceed the weakest premise needed for the verdict. State why it is not one level higher.

## Probability guardrails

Give a probability only when the matched class has a clear denominator and outcome, target evidence supports an update, the window is fixed, selection and missingness are addressed, and uncertainty is shown. Never derive a conversion probability from a correlation, effect size, odds ratio, coefficient, or management rule.

## Ethical test specification

```text
Hypothesis:
Population and recruitment:
Behavior and real cost:
Denominator:
Baseline or comparator:
Observation window:
Success and failure thresholds; source and rationale:
Sample size; source and rationale:
Stop rule:
Consent and disclosure:
Privacy and retention:
Payment and refund controls:
Default and opt-out controls:
Rollback:
Decision changed by result:
```

Set thresholds and sample-size rationale before seeing results. Count every eligible participant, including dropouts. Do not recommend direct card storage, undisclosed charges, fake social proof, coercive defaults, or deception that leaves a participant misled.

## Final check

- The verdict category matches the evidence state.
- Confidence is capped by the weakest premise.
- Direct evidence and inference are separate.
- Every load-bearing premise passes the independence gate.
- The reference class and target differences are explicit.
- The next test has the controls required by its stakes.
- Every load-bearing source has a visible URL.
