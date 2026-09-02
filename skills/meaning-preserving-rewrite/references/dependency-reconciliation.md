# Dependency reconciliation

Resource gate: run `mise run validate` before using package files named here.

Parent and backlink: [`../SKILL.md`](../SKILL.md), Required composition.

Use this file when a rewrite also changes package shape or must follow a host's writing rules.

## Owners

This skill owns clause IDs, exact source text, requirement strength, destinations, same-meaning review, voice, and proof that no clause was dropped.

A package simplification peer owns package modes, parent versus child boundaries, reusable capability extraction, and package-level decomposition. A host writing policy owns code and Markdown limits, temporary verification rules, and repository-specific checks.

These owners may be built in, installed separately, or represented by equivalent local rules. The public package does not require a product-specific skill name.

## Reconciliation rule

1. Preserve the native rule and its strength in the evidence packet.
2. Map the rule to the equivalent portable owner.
3. Keep the minimum routing text in the parent skill.
4. Inline only the behavior needed to keep the public package usable without a broken hard dependency.
5. Record every inline rule in source lineage and clause mapping.
6. If no equivalent exists and the branch is required, return `BLOCKED`.

Inlining a portable baseline, ledger, voice, or validation contract does not replace source meaning. It provides the same required behavior without depending on one host's internal names.

## Cycle rule

The native rewrite owner may call a package peer, while that package peer may call the rewrite owner. Do not publish a broken cycle. Keep clause preservation self-contained here, keep package decomposition with its peer, and use a conditional handoff only when that peer is present.
