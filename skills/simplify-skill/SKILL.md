---
name: simplify-skill
description: 'Use when simplifying a skill without losing behavior.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
---

# Simplify a skill

## When to use

Use this skill when an existing skill is harder to understand, operate, verify, or maintain than its domain requires. Do not use it for an ordinary code-only cleanup.

## Outcome

Reduce at least one declared complexity cost for a named actor and task. Preserve purpose, authority, behavior, safety, dependencies, outputs, and proof unless the user approves an exact loss.

Never accept line count alone as evidence of simplification.

## Hard boundaries

- Treat the complete current package as the baseline source of truth.
- Preserve essential domain complexity. Remove accidental complexity first.
- Default to lossless change.
- Keep exact commands, paths, schemas, hashes, quotes, permission gates, numeric limits, and stop rules exact.
- Keep component status separate from whole-skill status.
- Do not claim identical prose from every model or provider.
- Define determinism as a closed decision contract plus machine-checked end state.

## Required composition

Resource gate: run `mise run validate` before using package files named here.

Read the [dependency reconciliation](references/dependency-reconciliation.md) before changing a package. Use the collection's starting-point, human-behavior, agent-behavior, and meaning-preservation owners when their triggers apply.

A native host-only load is evidence, not a portable dependency. Internalize its invariant or route to an installed public peer. If neither is possible, return `BLOCKED_DEPENDENCY`.

## Input contract

Record `target`, `actor`, `task`, `environment`, `scope`, `invariants`, `measure`, and `allowed_loss`. Use `unknown` for missing data. `allowed_loss` is `none` unless the user approves an exact bound.

## State machine

Use only this order:

`DISCOVER -> BASELINE -> CONTRACT -> SELECT -> REWRITE -> VERIFY -> ACCEPT`

A gate failure moves to `BLOCKED`. Unapproved loss moves to `NEEDS_APPROVAL`. No accepted cost reduction moves to `NO_CHANGE`.

Resolve ties by authority, safety and privacy, behavior preservation, the user's exact method, lower declared cost, then `NO_CHANGE`.

## Procedure

1. **Discover.** Read the live target, every linked file, nearby owners, origin record, checks, and governing source. Stop on unexplained drift.
2. **Freeze.** Back up and hash every file. Run existing checks and representative tasks.
3. **Contract.** Give each rule and observable behavior a stable ID. Record authority, strength, conditions, protected spans, target, and evidence. Coverage must equal `1.0`.
4. **Select.** Try `deduplicate`, `clarify`, `reorder`, `progressive-disclosure`, `extract-child`, `simplify-code`, then `approved-loss`. Use the first mode that lowers the declared cost without a veto.
5. **Check claims.** Define the human or agent population and target test before claiming behavior improved.
6. **Rewrite.** Change the smallest owner. Use plain language, one rule per sentence, named actors, closed status words, defaults, and exact stop conditions.
7. **Handle code.** Use tests first and keep code proof separate from instruction proof.
8. **Verify.** Recompute hashes, ledger coverage, protected spans, links, metadata, loading, tests, package state, and end-state readback. Compare baseline and candidate in the same environment.
9. **Accept or restore.** Accept only when a declared cost fell, every invariant passed, and no veto remains. Otherwise restore or return the exact blocked status.

## Child extraction

Create a child only when it has a distinct trigger, standalone outcome, explicit interface, canonical ownership, direct tests, parent-route tests, expected reuse above coordination cost, and an acyclic load graph. Never split only to reduce line count.

## Acceptance

`ACCEPT` requires:

- baseline and candidate packet hashes recompute;
- ledger coverage is `1.0` with no unauthorized loss;
- every protected span passes or has exact approval;
- at least one declared cost decreases in the same environment;
- native, task, package, link, and readback checks pass;
- all ten native pressure cases retain their required and forbidden behavior.

Package PASS, eval enrollment, behavior-eval PASS, component status, and whole-skill PASS are separate results.

## Resources

- [Simplification model](references/simplification-model.md)
- [Preservation contract](references/preservation-contract.md)
- [Dependency reconciliation](references/dependency-reconciliation.md)
- `assets/` for ledger templates
- `examples/` for accepted and blocked outcomes
- `evals/` for native-case lineage and portable tests
- `mise run test` for package checks

## Factory execution contract

The accepted outcome is: Reduce skill complexity while proving semantic parity and preserving every accepted behavior. Preserve current behavior-preserving simplification behavior while changing its smallest owner.

1. Freeze the current package with `mise run ci` and record its digest.
2. Run `mise run domain-research-policy`, then judge the current behavior-preserving simplification sources and counterevidence.
3. Run `mise run agentic-request` for the named behavior-preserving simplification operation. Keep semantic choices with the model.
4. Run `mise run decision-policy`, `mise run ci`, and the behavioral evals. Return to the lowest failed owner.
5. Run `mise run invocation-policy -- <receipt>` and account for every task or its domain-specific non-use.
6. Optionally run `mise run improvement-policy`. Keep one changed dimension only if no protected dimension regresses.

Load `assets/use-case-contract.json` through `mise run use-case-policy` and `evals/evals.json` through `mise run evals` only when their contracts are needed.

Mise owns repeatable mechanics, ordering, receipts, and checks. The model owns interpretation, causal judgment, creative work, and direct perception that code cannot supply. Stop on missing authority, stale evidence, or a failed gate.
