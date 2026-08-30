# Behavior profile

Read this file before normalizing or reconciling user behavior. The source text remains authoritative and every normalized rule retains its original wording and locator.

## Required rule fields

Record timing or placement, trigger or predicate, actor, target, strength, input, transformation, action, output, state read or written, ordering, dependencies, precedence, repetition, concurrency, authorization, privacy, cost, reversibility, destination, success evidence, failure branch, fallback, stop condition, cleanup, and enforcement. Fields may carry `unspecified` only when the omission does not create an alternate operational reading; otherwise stop for one compact clarification.

Strength is `required`, `prohibited`, `permitted`, or `optional`. Enforcement is `instruction-only`, `host-assisted`, or `runtime-enforced`. A generated stable `B-` ID derives from source locator plus original wording, so reordering does not silently change a rule's identity when its locator is stable.

## Meaning preservation

Preserve context, content, intent, strength, order, exceptions, override points, and stop conditions. Do not replace exact input with a short summary, invent behavior from the tool contract, or turn a required rule into advice. When two user rules conflict and precedence does not resolve them, stop before generation.

## Rule-to-contract disposition

Each rule remains present and receives one disposition: `supported`, `supported with conditions`, `instruction-only`, `requires additional integration`, `conflicts with authority`, or `blocked by unknown`. A requested unavailable hook stays in the profile with `requires additional integration`; it is not weakened into instruction-only without user direction.

## Open-ended behavior

The profile accepts selection, substitution, argument or result transformation, batching, ordering, progress, cancellation, privacy, state, approval, retry, fallback, follow-up, cleanup, and conditional rules plus any other precisely stated instruction within current authority. The listed fields aid traceability and are not a closed behavior catalog.
