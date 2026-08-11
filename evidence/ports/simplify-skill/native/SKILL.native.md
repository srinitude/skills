---
name: simplify-skill
description: "Use when simplifying a complicated Hermes skill."
version: 1.0.1
author: Kiren Srinivasan
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, simplification, determinism, plain-language]
    related_skills: [starting-point, would-humans-actually, would-agents-actually, global-coding-policy, hermes-agent-skill-authoring, hermes-profile-remediation, hermes-skill-lifecycle, meaning-preserving-rewrite, deterministic-interview-workflows, simplify-code]
    created_by: agent
    created_with_hermes_commit: 46c7a4076fc543bdc98de12b81c2c85ef9c864b9
    compatibility_reviewed_with_hermes_commit: 33f8e96a72945afb29f3bc9ef9991940f0bedcf7
---

# Simplify a Hermes skill

## When to Use

Use this skill when an existing Hermes skill is harder to understand, operate, verify, or maintain than its domain requires. Do not use it for an ordinary code-only cleanup; route that work to the code simplification owner.

## Outcome

Make a skill easier for its named actor and task. Preserve its purpose, authority, behavior, safety, tool boundaries, dependencies, outputs, and proof unless the user approves an exact change.

A shorter skill is not automatically simpler. Accept a candidate only when a declared complexity cost falls and every preservation check passes.

## Hard boundaries

- Treat the current skill package as the baseline source of truth.
- Preserve essential domain complexity. Remove accidental complexity first.
- Default to lossless change. Do not approximate, weaken, omit, or broaden a rule without approval.
- Keep exact commands, paths, schemas, hashes, quotes, permission gates, and stop rules exact.
- Keep component status separate from whole-skill status.
- Do not claim identical output from every model. Models and providers can vary.
- Define determinism as an explicit decision contract plus machine-checked end state.

## Required loads

Before diagnosis, call `skill_view` for `starting-point`, `would-humans-actually`, `would-agents-actually`, `global-coding-policy`, `hermes-agent-skill-authoring`, `hermes-profile-remediation`, `hermes-skill-lifecycle`, `meaning-preserving-rewrite`, `deterministic-interview-workflows`, and `simplify-code`.

Then call `skills_list` and load every skill whose trigger governs the target domain, tool, code, test, evidence, package, or delivery path. Do not load unrelated skills. If a required skill is unavailable, stop before mutation and report the missing dependency.

Use `hermes-skill-lifecycle` for user-local mutation. Use `hermes-agent-skill-authoring` for repository-owned mutation. Their ownership rules override this skill's rewrite procedure.

## Input contract

Record these fields before editing:

- `target`: skill name, path, origin, owner, version, and complete linked-file set.
- `outcome`: actor, task, observable result, and current failure or cost.
- `scope`: read-only, propose, patch, edit, split, create-child, or package.
- `environment`: Hermes commit, profile, platform, tools, permissions, and live docs.
- `invariants`: required meanings, behaviors, states, exact spans, and proof.
- `measure`: one or more accepted costs to reduce.
- `allowed_loss`: `none` unless the user states an exact allowance.

Use `unknown` for a missing value. Never infer authority, permission, or allowed loss.

## Deterministic state machine

Use only these states in this order:

`DISCOVER -> BASELINE -> CONTRACT -> SELECT -> REWRITE -> VERIFY -> ACCEPT`

A gate failure moves to `BLOCKED`. A lossy change without approval moves to `NEEDS_APPROVAL`. No accepted cost reduction moves to `NO_CHANGE`. Never skip a state or rename a status.

Resolve ties in this order: higher authority, safety and privacy, behavior preservation, the user's exact method, lower declared cost, then `NO_CHANGE`.

## Procedure

1. **Discover.** Read the live target, every linked instruction file, its registry entry, nearby skills, origin records, current Hermes source, and live docs that govern it. Recheck compatibility for user-created skills. Stop on unexplained concurrent drift.
2. **Freeze the baseline.** Back up and hash every file in scope. Run existing checks and representative tasks. Record absent files as `ABSENT`, not as invented hashes.
3. **Build the contract.** Give each rule and observable behavior a stable ID. Record its source, authority, strength, conditions, exact spans, destination, and baseline evidence. Coverage must equal 100 percent before editing.
4. **Choose a mode.** Use only `deduplicate`, `clarify`, `reorder`, `progressive-disclosure`, `extract-child`, `simplify-code`, or `approved-loss`. Choose the first mode that reduces the declared cost without a veto.
5. **Check people and agents.** Define exact `[x]` and `[a]` when the result depends on human or agent behavior. Research live evidence, state the verdict limit, and prescribe a target test. Do not turn readability or prompt length into a behavior claim.
6. **Rewrite the smallest owner.** Use plain language, one rule per sentence, named actors, numbered ordered steps, closed status words, explicit defaults, and exact stop conditions. Keep always-needed rules in `SKILL.md`. Move only branch detail to a linked owner with a load trigger and backlink.
7. **Handle code.** Load the target language and test owners. Follow `simplify-code` and TDD. Keep code proof separate from instruction proof.
8. **Verify.** Recompute hashes, ledger coverage, clause strength, links, metadata, active loading, test results, and end-state readback. Compare baseline and candidate on the same tasks and environment.
9. **Accept or restore.** Accept only when at least one declared cost decreases, every invariant passes, and no veto remains. Otherwise restore the baseline or return the exact blocked status.

## Child-skill extraction

Extract functionality into a child skill only when all checks pass:

1. It has one distinct trigger and one standalone outcome.
2. It can be invoked and tested without the parent.
3. Its input, output, authority, failure, and version boundaries are explicit.
4. It owns a design decision or capability instead of one execution step.
5. No current skill is the rightful owner.
6. Expected reuse exceeds discovery, loading, coordination, and maintenance cost.
7. The parent becomes a thin router and the load graph stays acyclic.

If any check fails, keep the behavior in the parent or move branch detail to a reference. Never create a child to reduce line count alone. Each new child must pass the normal six skill-creation gates, direct-use tests, parent-route tests, and whole-package tests.

## Model-portable writing rules

Use `must`, `must not`, `should`, and `may` with one fixed meaning. Use closed enums for decisions. Name every input and output. State defaults, precedence, tie-breaks, unknown handling, retries, limits, and stop conditions. Use canonical sorted JSON for hashed machine data.

Plain language reduces interpretation differences. It cannot prove universal model behavior. Report model, provider, version, settings, runtime, and trial count for every behavior result.

## Progressive disclosure

`PD-001`: `references/simplification-model.md` owns context definitions, cost measures, modes, research findings, and decomposition rationale. Load it before selecting a mode or simplifying an unfamiliar domain.

`PD-002`: `references/preservation-contract.md` owns ledger fields, vetoes, deterministic schemas, acceptance thresholds, and report format. Load it before `CONTRACT` and `VERIFY`.

`PD-003`: `references/eval-cases.json` owns frozen pressure cases. Load it before testing or changing this skill.

## Verification checklist

- [ ] Required and triggered skills loaded
- [ ] Origin, owner, scope, environment, and compatibility verified
- [ ] Baseline packet, task results, and rollback proved
- [ ] Contract ledger covers every source rule and behavior
- [ ] At least one declared cost fell on a same-environment comparison
- [ ] No authority, behavior, safety, exact span, dependency, or proof was lost
- [ ] Any child passed creation, ownership, load-DAG, direct, routed, and package checks
- [ ] Human and agent claims have scoped verdicts and target tests
- [ ] Native checks, active loading, readback, and regression tasks passed
- [ ] Package verification, eval enrollment, behavior eval, and whole-skill status remain separate
