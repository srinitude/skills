---
name: skill-factory
description: "Use when a workflow or capability must become a new agent skill, when an existing skill must be updated or standardized without losing its purpose, or when a skill needs validation, evaluation, scaffolding, scripts, tests, or a Mise task graph."
license: MIT
metadata:
  author: Kiren Srinivasan
  version: "0.4.5"
---

# skill-factory

skill-factory creates, updates, and standardizes working agent skills. It preserves the requested purpose while producing a portable directory whose instructions, references, assets, scripts, tests, Mise graph, CI, examples, and evals pass fresh checks.

## Outcome and motivation

The outcome is a skill that produces the intended user-visible result and can prove it. Package shape is necessary evidence, never the result by itself. State the reason behind every material constraint so the executor can adapt inside the allowed boundary without defeating the outcome. Keep deterministic mechanics out of prose so model attention stays on semantics, judgment, creative work, and exceptions.

## Simplicity and language

Keep this factory and every output as the smallest coherent structure that preserves the outcome, proof, boundaries, forbidden outcomes, and mandatory methods, plus accepted behavior. Simple means easy to reason about: one canonical owner per rule, one stable term per concept, one default path per job, and one explicit failure branch for each material unknown. Remove duplicate rules, decorative structure, needless indirection, and choices that do not change behavior. Never hide essential domain complexity or weaken a rule to reduce lines.

Set a context budget for each operation before loading support. Keep the always-loaded body as the smallest domain-complete decision path. At each branch, load only the canonical owner needed for the current decision, record or verify its content digest, reuse current verified receipts, and reread only after owner change or uncertainty. Token efficiency fails if it removes a domain motive, constraint, interface, failure branch, proof duty, model-owned capability, or the context needed for intelligent and thoughtful adaptation.

Use plain and direct language. Load [the writing rules](references/writing-rules.md) through `mise run lint-writing` for this factory and every skill it creates, updates, standardizes, or imports. Put the result first, use active verbs, keep one idea per sentence and one topic per paragraph, and place instructions in execution order. Mechanical lint finds bounded text faults. A same-meaning human review decides whether the package is simpler and still complete.

## Evidence and source order

Use the user's request and live owning sources first. Then use the current target skill, [the generation contract](references/generation-contract.md) through `mise run validate`, task-specific references, worked examples, and eval evidence. Load [use-case specificity](references/use-case-specificity.md) through `mise run domain-research-policy` before defining domain behavior, terms, roles, constraints, or proof. Every aspect and primitive must state its domain role, protected outcome, concrete progress value, motivation, prevented failure, and proof. Load [resource and experiment design](references/resource-and-experiment-design.md) through `mise run improvement-policy` before choosing a data structure, format, cache, benchmark, or improvement trial. The required generated-skill order is Outcome, Motivation, Evidence, Mise task graph, Steps, Assets, then Evals. This order links intent to action and action to proof.

## Which commands does this skill accept?

Interpret the user's request as one of these commands.

| Command | What it does |
| --- | --- |
| help | Show this table and a one line summary per command. |
| new <prompt> | Build a skill that fulfills the prompt. Main path below. |
| update <path> <prompt> | Change an existing skill and preserve its domain purpose and accepted behavior. |
| standardize <path> | Transform an existing skill into this factory's standard format without replacing its domain purpose. |
| standardize-target <path> <profile> | Plan or apply a profile-bound in-place registry standardization after the baseline is frozen. |
| refresh-registry-lineage <skill...> | Refresh source lineage after accepted registry skill changes. |
| import <source> <destination> | Convert a host-specific source into a separate portable skill and repository-guidance package. |
| validate <path> | Run the structure, writing, code, and placeholder checks on a skill. |
| eval <path> | Check a skill's eval files, then run its cases. |
| doctor | Run `mise run doctor` and report readiness. |

Suppose the request matches no command, or a required fact cannot be retrieved. Stop, report what is missing, and wait. Do not guess.

## Ordered workflow

1. **Frame the outcome and domain.** Model: classify the command, freeze the user-visible result, boundaries, forbidden results, and accepted behavior without inventing a fact. Branch: choose new, update, standardize, import, validate, eval, doctor, or help from the request.
2. **Prove runner readiness.** Mise: run `mise run doctor`. Model: choose the matching public operation. If: readiness is false, stop the blocked work and report the exact failed prerequisite.
3. **Ground the use case.** Mise: run `mise run domain-research-policy` and `mise run use-case-policy`. Model: gather current sources, test counterevidence, and decide the target skill's terms, roles, failures, evidence, and exclusions. For each: accept, reject, bound, or mark every required source and domain dimension inapplicable with a reason.
4. **Freeze and route the change.** Mise: run `mise run plan-standardize -- <source>` and `mise run audit-source-corpus -- <source>` when the operation has a source. For an in-place registry update, run `mise run standardize-target -- <source> --profile <profile>` without `--apply`, review the profile and change set, then rerun with `--apply`. Model: preserve the baseline, locate the smallest owner, and reject collisions, unknown ownership, or host-only assumptions.
5. **Build under BOOTSTRAP, RED, GREEN, REFACTOR.** Mise: run `mise run task-graph-policy`, then `mise run test` to capture RED and again after each change. Model: write the domain reasoning, creative behavior, and exception handling that deterministic code cannot decide. Repeat: observe one behavior contract fail in RED, implement the smallest change, rerun to GREEN, and refactor under the same contract until the required behavior passes or a real blocker stops the loop.
6. **Produce integrated proof.** Mise: run `mise run decision-policy`, the target skill's `mise run ci`, then `mise run refresh-registry-lineage -- <skill>`, `mise run validate-target -- <path>`, and `mise run eval-target -- <path>`. Model: review semantics, source-to-claim links, direct perception when required, counterexamples, and whether the result actually fulfills the frozen outcome. If: a check or judgment fails, return to the lowest owning step and invalidate its dependents.
7. **Account for the invocation.** Mise: run `mise run invocation-policy -- <receipt>`. Model: state every remaining limit. For each: record every task's run evidence or a domain-specific inapplicability reason in the receipt.
8. **Keep or restore an improvement.** Mise: run `mise run improvement-policy` before an optional trial. Model: retain a candidate only when its named dimension improves and no protected dimension regresses; otherwise restore the accepted digest and verify it.
9. **Finish maintenance last.** Mise: run `mise run mise-primitives-update` only after accepted outcome work concludes, then rerun `mise run ci`. Model: reconcile any changed primitive and report a package-manager blocker without force. Stop: end at the first fully accepted state; do not add unrelated work.

## Deterministic and model-owned boundary

Mise owns every deterministic command. Put schemas, parsing, validation, file generation, state transitions, task ordering, receipts, measurement, comparison, and reproducible rollback checks in tested scripts behind one owning Mise task. The model-owned boundary holds only semantic interpretation, domain judgment, creative generation, causal explanation, and direct human-sense review. A schema pass cannot prove meaning or quality.

Mise is an orchestration boundary, not a capability ceiling. Use every available, authorized capability needed for the outcome, including direct vision, current web research, browser or computer interaction, tool calls, multimodal inspection, semantic reasoning, synthesis, creativity, and human-sense judgment. Let Mise prepare inputs, schedule dependencies, preserve receipts, and test reproducible claims, but never replace direct judgment with a proxy. If the task needs a capability that code cannot supply, disabling or imitating that capability is failure, even when every deterministic gate passes. Mise exists to remove mechanical delay and expose reproducible faults so model-owned attention stays on meaning, perception, creativity, and exceptions.

Run long prompts, skills, and agentic primitives through `mise run agentic-request -- --request <file-or-dash> --runner <executable> --runner-args-json <array>`. Bind the request to its use-case contract, outcome, domain terms, and digests. Each prompt, SKILL.md dependency, and primitive states its domain role, contribution, relevance, and proof. The caller supplies runner authority. The dispatcher uses one JSON envelope over standard input without shell interpolation. It proves structure, not relevance or result quality.

Decompose apparently nondeterministic work. Route stable manifests, receipts, schemas, coverage, order, digests, budgets, output envelopes, decisions, and rollback through one Mise task. Stop only at semantic interpretation, causal reasoning, creativity, direct perception, or human-sense judgment, then record why code cannot own it.

Apply the same envelope, primitive map, motivated decisions, graph, proof, falsifier, failure branch, and rollback to skill-factory itself.

Record each material decision's outcome, motivation, selected-path reason, owner, inputs, effect, proof, falsifier, and failure branch in assets/decision-records.json through `mise run decision-policy`. Semantic review decides whether the record is true.

Choose data structures, algorithms, formats, cache keys, batching, and concurrency from measured access patterns. Measure cold and warm paths plus applicable time, CPU, memory, storage, network, cache, context, process, concurrency, accelerator, cost, and human attention. Record non-use. Cache only deterministic tasks with complete inputs, versions, environment, and outputs. Never cache live judgment, mutable remote state, uncaptured randomness, or side effects.

## Mise task graph

The public surface is `mise run doctor`, `mise run new`, `mise run plan-standardize`, `mise run standardize-target`, `mise run refresh-registry-lineage`, `mise run audit-source-corpus`, `mise run domain-research-policy`, `mise run use-case-policy`, `mise run mise-primitives-policy`, `mise run primitive-lifecycle-policy`, `mise run task-graph-policy`, `mise run decision-policy`, `mise run validate-target`, `mise run eval-target`, `mise run agentic-request`, `mise run invocation-policy`, `mise run mise-primitives-update`, and `mise run ci`. Never bypass it. Missing Mise is `BLOCKED`. Declare every dependency and one path from each operation. Cycles, diamonds, unknown or disconnected edges, redundant edges, and nested Mise calls fail. Record each task's outcome, motivation, progress, proof, and applicability in assets/use-case-contract.json.

Map actors, objects, actions, states, invariants, variants, interfaces, authorities, failures, recoveries, evidence, time, resources, quality, terms, and exclusions. Map every skill body, reference, asset, script, test, Mise task, example, eval, policy, schema, and record. Cover discovery through retirement in assets/primitive-lifecycle.json through `mise run primitive-lifecycle-policy`; every phase needs a real domain task, progress, motivation, proof, and prevented failure.

Classify every official Mise primitive in assets/mise-primitives.json through `mise run mise-primitives-policy`. Use only outcome-serving primitives; give each non-use a domain reason. Missing, stale, invented, or nominal use fails.

Account for every invocation task. Run the chosen path and give each other task request-specific `inapplicable` proof. Validate the receipt with `mise run invocation-policy -- <receipt>`. Keep command output for every run claim; silence fails.

Keep the Mise version fixed during outcome work. Run `mise run mise-primitives-update` only after acceptance, reconcile its catalog, then rerun `mise run ci` and record version and digest. A package-manager or update failure is `BLOCKED`; never force replacement.

## Operation branches

- **New:** Run `mise run doctor`, reuse an owner through `mise run source-corpus`, then `mise run new -- --name <name> --description "<description>" --dest <destination>`. Author tasks, graph tests, behavior tests, scripts, SKILL.md, references, assets, examples, and evals in RED, GREEN, REFACTOR order. A fresh scaffold stays blocked until all placeholder seeds are replaced.
- **Update or standardize:** Run `mise run plan-standardize -- <source>` and save its `baseline_digest`. For registry-wide policy adoption, run `mise run standardize-target -- <source> --profile <profile>` first as a no-write plan, then add `--apply` only after the domain profile and baseline are accepted. These operations preserve domain purpose, triggers, accepted behavior, evidence, outcome, proof, boundaries, forbidden outcomes, and mandatory methods. Change the smallest owner, then compare against the baseline.
- **Import:** Also run `mise run audit-source-corpus -- <source>`. Keep coding-agent clients distinct from package formats. Reject collisions, symlinks, unknown owners, and platform-specific assumptions. Translate capability instructions to SKILL.md, repository rules to AGENTS.md, and host ownership to `.agents/`. The source stays unchanged unless the user requests in-place migration.
- **Validate or eval:** Run `mise run validate-target -- <path>` or `mise run eval-target -- <path>`. Report every failure and grade behavioral cases against fresh saved evidence.

## Progressive disclosure

Use `mise run validate` for references/generation-contract.md and examples/example-help.md; `mise run improvement-policy` for references/resource-and-experiment-design.md; `mise run domain-research-policy` for references/use-case-specificity.md; `mise run lint-writing` for references/writing-rules.md; `mise run lint-code` for references/code-rules.md; `mise run evals` for references/eval-authoring.md and evals/; `mise run source-corpus` for references/registry.md and assets/source-shape-corpus.json; and `mise run new` for assets/skill-template.md and examples/example-new-skill.md. Load examples/example-doctor.md after doctor failure, placeholder evidence through `mise run lint-placeholders`, and validation examples through their matching target task. Implementation stays private behind Mise.

## Proof output

A passing command exits 0. `mise run validate`, `mise run lint-writing`, `mise run lint-code`, `mise run lint-placeholders`, `mise run evals`, and `mise run improvement-policy` report zero problems. `mise run doctor` reports `"ready": true` and `"mode": "mise"`. A structural pass proves only its contract; behavioral evals and domain review remain required.

## When is the work done?

Done means fresh `mise run domain-research-policy`, `mise run use-case-policy`, `mise run mise-primitives-policy`, `mise run primitive-lifecycle-policy`, `mise run task-graph-policy`, `mise run decision-policy`, `mise run ci`, `mise run validate-target`, `mise run eval-target`, and `mise run invocation-policy -- <receipt>` evidence passes; task-specific behavior, source-to-claim review, domain-swap attack, and domain-term-removal attack pass; the log traces outcome through motivation, evidence, tasks, steps, assets, and evals; no generic aspect, primitive, lifecycle phase, Mise disposition, task, placeholder, source collision, host-only assumption, skipped applicable task, or unproved completion claim remains.

## Optional final improvement experiment

Run this only after required work is accepted. Freeze a fresh baseline, frozen evaluator, fixtures, environment, time budget, repetitions, and applicable resource measures. Change one named dimension at its smallest owner. Run `mise run improvement-policy`, then the use-case experiment through its owning Mise task. Keep an external keep, discard, or crash ledger with content digests and protected-dimension results. Retain the candidate only when the named dimension improves materially and no protected dimension regresses. Otherwise restore the last accepted version and verify its digest. Do not start an open-ended loop unless the user's completion condition requires one.
