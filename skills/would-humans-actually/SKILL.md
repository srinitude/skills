---
name: would-humans-actually
description: 'Use when a claim depends on people taking a real action.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
---

# Would Humans Actually?

Produce an evidence-backed verdict about a defined action by a defined population in a defined setting and time window. Separate what people say from what they do. State uncertainty, scope limits, opposing evidence, and the next ethical test.

## Command grammar

- `/would-humans-actually help`: show the contract, verdict labels, and required inputs without researching.
- `/would-humans-actually verdict <behavior question>`: research the question, issue the supported verdict, and validate the completed artifact.

## Procedure

1. Define the target behavior as `[x]` before research. Name the actor, observable action, setting, trigger, timing, frequency, duration, money, effort, privacy, status, reversal cost, and current alternative. Ask one question only when an unknown changes the research path. Otherwise state the assumption.
2. Write support, contradiction, and insufficient-evidence conditions before searching. Prefer observed target behavior, direct field evidence, matched administrative records, experiments, systematic reviews, and close analogs. Use current primary sources. When recent discourse or change matters, load [recent-public-signal.md](references/recent-public-signal.md).
3. Verify every source at its primary record. Search results, summaries, engagement counts, and claims repeated by another article are discovery aids. Complete the source card in [verdict-protocol.md](references/verdict-protocol.md) for every claim that changes the verdict.
4. Require two independent author teams or datasets for every premise needed by the verdict or confidence. Shared datasets and restatements count once. If the independence gate fails, keep the source as directional context only.
5. Define the outside-view reference class before using its result. Match behavior, population, setting, costs, alternative, and observation window. Do not issue a numerical probability without a matched denominator and defensible uncertainty.
6. After evidence collection, load [frameworks.md](references/frameworks.md) to test motivation, capability, opportunity, prompts, norms, habit, friction, reward timing, identity, privacy, switching, and reversal mechanisms. Frameworks organize questions. They do not supply rates.
7. Choose `LIKELY`, `UNLIKELY`, `UNCERTAIN`, or `INSUFFICIENT EVIDENCE` under [verdict-protocol.md](references/verdict-protocol.md). If live research is unavailable or forbidden, use `UNVALIDATED HYPOTHESIS`. Never invent a study, sample, rate, base rate, quote, URL, or observed result.
8. Design the smallest ethical test that exposes the real cost. Prespecify the population, denominator, window, comparator, thresholds, sample-size rationale, stop rules, consent, disclosure, privacy, payment, legal review, rollback, opt-out, and decision changed. Use `user-specified; rationale not provided` when that is true.
9. Render the result with [output-template.md](references/output-template.md), save it outside the installed skill, then run `python3 scripts/validate_verdict.py --input <verdict.md>`. Exit 0 proves the artifact has the required shape. Exit 1 means the verdict is incomplete. Exit 2 means the command or input path is wrong.
10. Append the exact query, sources opened, exclusions, assumptions, and validation output to an external research log after each consequential step. Stop and report the missing item when a load-bearing source, denominator, permission, or safety control cannot be verified.

## Load conditions

- Load [evidence-base.md](references/evidence-base.md) when a source pattern or behavioral magnitude may inform the analysis, then recheck the primary source before use.
- Load [verdict-template.md](assets/verdict-template.md) when creating a verdict file. Copy it out of `assets/`; do not edit the installed template.
- Load [help.md](examples/help.md) for the help command, [verdict-insufficient-evidence.md](examples/verdict-insufficient-evidence.md) for a researched verdict, and [failure-unvalidated.md](examples/failure-unvalidated.md) when live research or a precise behavior is missing.
- Run [validate_verdict.py](scripts/validate_verdict.py) after writing the artifact. Read [test_validate_verdict.py](scripts/tests/test_validate_verdict.py) only when changing the validator contract.
- Read [contract.md](evals/contract.md) before changing behavior, trigger boundaries, or evaluation cases.
- Load [generation-contract.md](references/generation-contract.md) only when maintaining or repackaging this skill.

## Gotchas

- A click, waitlist signup, interview compliment, or stated intention is not a purchase, retained user, or completed action.
- Never apply a universal intent discount, willingness-to-pay divisor, loss multiplier, habit rate, or switching threshold.
- Do not count two papers using one dataset as independent evidence.
- Do not hide population, culture, channel, or time mismatch behind one global verdict.
- In health, finance, law, employment, housing, education, or another sensitive domain, assess behavioral plausibility only. Do not infer efficacy, safety, legality, entitlement, or compliance.

## Completion criteria

- `[x]` is observable and scoped to a population, setting, cost, and window.
- Every load-bearing premise has two independent sources and a complete ledger row.
- Direct evidence and inference are separate, and opposing evidence is visible.
- Confidence is capped by the weakest premise and transport bridge.
- The next test has a denominator, decision rule, and required participant protections.
- Every load-bearing source appears as a visible URL.
- The validator prints `"status": "PASS"` and exits 0.
