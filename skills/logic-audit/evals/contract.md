# Evaluation contract

## Scope

Evaluate activation, rejection, normalization, contradiction and gap classification, repair, failure handling, recovery, and speed under both `with_skill` and `without_skill` conditions. Run each case twice. Keep activation, behavior, source preservation, and whole-package results separate.

## Activation

Activate when the user asks to find, explain, reconcile, or repair contradictions, ambiguities, unsupported inferences, missing cases, incomplete proof chains, authority conflicts, or reasoning gaps across a bounded source set. Reject routine fact lookup, exact copying, ordinary summarization, and code debugging that has no logical-contract question.

## Behavior

A passing response acquires the current date, maps the desired outcome, separates fixed requirements from candidate routes, names the bounded source set and authority order, normalizes entity, time, scope, meaning, modality, and quantifiers before classification, traces each conclusion to premises and evidence, tests a counterexample, and records one finding per independent issue.

The response distinguishes contradiction, ambiguity, unsupported inference, missing case, proof gap, and authority conflict. It preserves exact methods and stronger authority, does not invent missing premises, and limits completion claims to accessible sources.

## Failure and recovery

When required source text or authority is unavailable, return `BLOCKED` for the affected decision and name the deciding evidence. When a web capability fails, record it as `UNAVAILABLE`, use an authorized capability-neutral fallback when possible, and keep current facts unresolved without inspected evidence. Recovery restores omitted premises or source clauses, applies the smallest coherent repair, rebuilds the dependency map, and reruns the original check plus a negative case.

## Model disclosure

A judge may assess only the supplied prompt, response, trace, source requirements, and vetoes. It must not infer hidden source reads, approvals, external checks, mutations, or actions. Missing direct evidence remains unproven.

## Decision rule

Every native expectation must pass and every native prohibition must remain absent. Calling ambiguity a contradiction, changing requirement strength, hiding an authority conflict, inventing evidence, omitting a required source, or claiming complete proof from a component check makes the case `BLOCKED`.
