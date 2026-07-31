# Logic audit check catalog

This reference supports `logic-audit`. Apply each class only after normalizing entities, terms, authority, scope, date, version, modality, quantifiers, and units.

## Consistency classes

| Class                  | Test                                                                                             | Typical repair                                              |
| ---------------------- | ------------------------------------------------------------------------------------------------ | ----------------------------------------------------------- |
| Direct negation        | Does the source assert both P and not-P under the same conditions?                               | Correct, qualify, or choose by authority.                   |
| Mutual exclusion       | Do two accepted states violate an exclusivity rule?                                              | Split conditions or remove one state.                       |
| Temporal               | Are statements true at different dates, phases, or versions?                                     | Add effective dates or a transition rule.                   |
| Identity and reference | Do names, pronouns, IDs, aliases, or versions point to different entities?                       | Bind each reference to one entity.                          |
| Definition             | Is one term used with incompatible meanings?                                                     | Define it once or label each sense.                         |
| Category               | Is a property or rule applied to the wrong kind of object?                                       | Correct the category or rule domain.                        |
| Scope                  | Does a local claim become global, or an exception become the rule?                               | Restore the bounded scope.                                  |
| Quantifier             | Does `some`, `most`, `all`, `none`, or `exactly one` change?                                     | Match the supported quantifier.                             |
| Modality               | Does `can`, `may`, `should`, or `must` change force?                                             | Restore the authorized modality.                            |
| Conditional            | Are necessary and sufficient conditions reversed, or is the consequent affirmed?                 | State the valid direction and missing premise.              |
| Units and dimensions   | Are values compared across incompatible units, bases, rates, currencies, or denominators?        | Convert and name the basis.                                 |
| Constraint feasibility | Can all accepted constraints hold together?                                                      | Relax only an approved constraint or declare infeasibility. |
| Authority              | Do instructions conflict across authority levels or owners?                                      | Apply precedence and surface the conflict.                  |
| Causal                 | Is correlation, sequence, or selection treated as causation?                                     | Limit the claim or add causal evidence.                     |
| Circular               | Does a conclusion directly or indirectly support its own premise?                                | Add independent support or remove the claim.                |
| Exhaustiveness         | Are listed alternatives claimed to be complete without excluding another case?                   | Add the missing case or weaken completeness.                |
| Aggregation            | Does a property move invalidly between a part, group, average, and individual?                   | State the valid level of analysis.                          |
| Probability            | Are base rates, conditional probabilities, or uncertainty combined incorrectly?                  | Recalculate with explicit events and priors.                |
| Epistemic              | Is unknown treated as false, absence of evidence as evidence of absence, or confidence as truth? | Restore the correct knowledge state.                        |
| Self-reference         | Does a rule invalidate or exempt itself without a defined meta-level?                            | Define the level or exception.                              |
| Source-version         | Are sources from incompatible schemas, editions, jurisdictions, or releases combined?            | Pin and reconcile versions.                                 |

## Gap classes

| Class                    | Missing object                                                                       | Deciding question                                 |
| ------------------------ | ------------------------------------------------------------------------------------ | ------------------------------------------------- |
| Premise                  | A conclusion lacks a required reason.                                                | What must be true for this inference to hold?     |
| Definition               | A material term has no bounded meaning.                                              | How can two readers classify the same case alike? |
| Evidence                 | A checkable claim lacks adequate source support.                                     | What observation would decide it?                 |
| Inference                | Evidence exists but does not entail the claim.                                       | Which rule connects evidence to conclusion?       |
| Case or branch           | An input, exception, alternative, or boundary case is unhandled.                     | What happens for every reachable class?           |
| State transition         | Initial, intermediate, failure, recovery, cancellation, or terminal state is absent. | Can each state enter and exit safely?             |
| Actor and authority      | No owner can decide or act.                                                          | Who is authorized and accountable?                |
| Dependency               | An upstream requirement, provider, interface, or order is unstated.                  | What must exist first?                            |
| Data                     | Required input, format, provenance, freshness, or quality is absent.                 | What data proves the step can run?                |
| Time                     | Deadline, validity window, sequence, or effective date is absent.                    | When does the rule apply?                         |
| Resource and feasibility | Cost, capacity, skill, permission, or runtime need is absent.                        | Can the plan execute within bounds?               |
| Safety and privacy       | Threat, consent, retention, exposure, or rollback control is absent.                 | What forbidden outcome remains possible?          |
| Acceptance               | No observable PASS or BLOCKED rule exists.                                           | What exact evidence decides completion?           |
| Coverage                 | Component evidence is presented as whole-outcome evidence.                           | Which parent outcome remains unproved?            |
| Implementation           | A requirement has no action, owner, or interface.                                    | How will it become real?                          |
| Verification             | An action has no exercised check or negative case.                                   | What real run can falsify success?                |
| Currentness              | A time-sensitive premise has no fresh source or date.                                | What is true as of the audit anchor?              |
| Rollout and recovery     | Migration, compatibility, rollback, or cleanup is absent.                            | How is partial failure contained?                 |

## Candidate adjudication

- `CONFIRMED`: The normalized source and evidence establish the issue.
- `PROBABLE`: The issue is more likely than not, but one material fact is missing.
- `POSSIBLE`: A coherent reading creates the issue, but another reading avoids it.
- `NOT_AN_ISSUE`: Normalization or evidence resolves the candidate.
- `BLOCKED`: Required source, authority, or deciding evidence is unavailable.

## Impact scale

- `critical`: Unsafe, unauthorized, irreversible, or invalidates the primary outcome.
- `high`: Blocks a required outcome or can produce a materially wrong decision.
- `medium`: Produces avoidable rework, ambiguity, or incomplete proof.
- `low`: Local clarity issue with no material effect on the accepted outcome.

## Counterexample prompts

- What smallest valid input breaks this claim?
- Which omitted date, version, actor, unit, or exception changes the result?
- Can all constraints hold at once?
- Does the evidence support the same quantifier and scope as the conclusion?
- Could the observed result arise if the claimed cause were absent?
- What whole-outcome claim is being inferred from a component check?
