---
name: {{NAME}}
description: "{{DESCRIPTION}}"
license: MIT
metadata:
  author: skill-factory
  version: "0.1.0"
---

# {{NAME}}

{{DESCRIPTION}}

SCAFFOLD-PLACEHOLDER: rewrite this whole line as two or three sentences naming the result this skill produces, then rerun `mise run lint-placeholders` until it prints 0 placeholders.

## Outcome

State the observable user result, its scope, its forbidden outcomes, and the evidence that permits completion. An artifact or passing task is evidence only for the behavior it checks.

## Motivation

Explain why every material constraint protects the outcome and what failure it prevents. This lets the executor adapt within the accepted boundary without treating one recipe as the goal.

## Simplicity and language

Use the smallest coherent structure that preserves every required rule and accepted behavior. Keep one canonical owner per rule, one stable term per concept, one default path per job, and one material decision per branch. Remove duplicate rules, decorative sections, needless indirection, and choices that do not change the result. Keep essential domain complexity visible.

Set a context budget for each {{NAME}} operation before loading support. Keep this always-loaded body as the smallest domain-complete decision path. At each branch, load only the canonical owner needed for the current decision, record or verify its content digest, reuse current verified receipts, and reread only after owner change or uncertainty. Token efficiency fails if it removes a {{NAME}} motive, constraint, interface, failure branch, proof duty, model-owned capability, or the context needed for intelligent and thoughtful adaptation.

Use plain and direct language. Load references/writing-rules.md through `mise run lint-writing`. Put the result first, use active verbs, keep one idea per sentence and one topic per paragraph, and place steps in execution order. Mechanical lint checks bounded text rules. Human review must confirm that the skill is easy to reason about and has not lost meaning.

## Evidence and references

Name live authoritative sources first, then local references, examples, and prior eval evidence. Separate facts, inferences, and unresolved claims. Read only the linked reference that the current decision needs.

## Use-case specificity

Read references/use-case-specificity.md before defining domain behavior. The aspect layer covers actors, objects, actions, states, invariants, variants, interfaces, authorities, failures, recoveries, evidence, time, resources, quality, terminology, and exclusions. The primitive layer covers every skill body, reference, asset, script, test, Mise task, example, eval, policy, schema, and record. Record each item's {{NAME}} role, protected outcome, concrete progress value, motivation, prevented failure, and proof in assets/use-case-contract.json. Run `mise run domain-research-policy` and `mise run use-case-policy`; a fresh scaffold must fail both until every seed is replaced with source-backed {{NAME}} content.

## Which commands does this skill accept?

Interpret the user's request as one of these commands.

| Command | What it does |
| --- | --- |
| help | Show this command table and the frontmatter description. |
| info | Run `mise run info` and report the JSON. |
| check | Run `mise run ci` and report each job with its exit code. |

Suppose the request matches none of these. Stop, say what is missing, and wait. Do not guess.

## Ordered workflow

1. **Frame the outcome and domain.** Model: freeze the observable {{NAME}} result, scope, authority, forbidden results, and accepted behavior. Branch: select the one {{NAME}} command that matches the request.
2. **Prove runner readiness.** Mise: run `mise run doctor`. Model: select the one {{NAME}} public operation that fits. If: readiness is false, stop the blocked work and report the exact failed prerequisite.
3. **Ground the use case.** Mise: run `mise run domain-research-policy` and `mise run use-case-policy`. Model: gather current sources, test counterevidence, and decide the {{NAME}} terms, roles, failures, evidence, and exclusions. For each: accept, reject, bound, or mark every required source and domain dimension inapplicable with a reason.
4. **Choose the smallest valid route.** Mise: run `mise run task-graph-policy` after declaring the operation and its dependencies. Model: locate the lowest {{NAME}} owner and keep unrelated behavior unchanged.
5. **Execute BOOTSTRAP, RED, GREEN, REFACTOR.** Mise: run `mise run task-graph-policy`, then `mise run test` to capture RED and again after each change. Model: perform the semantic, creative, perceptual, and exception work that {{NAME}} needs and code cannot decide. Repeat: observe one behavior contract fail in RED, run the smallest domain operation, rerun to GREEN, and refactor under the same checks until the required behavior passes or a real blocker stops the loop.
6. **Produce integrated proof.** Mise: run `mise run decision-policy`, `mise run ci`, and the applicable {{NAME}} eval task. Model: judge source-to-claim links, counterexamples, direct human-sense evidence when required, and whether the promised outcome is truly fulfilled. If: a check or judgment fails, return to the lowest owning step and invalidate its dependents.
7. **Account for the invocation.** Mise: run `mise run invocation-policy -- <receipt>`. Model: state every remaining limit. For each: record every task's run evidence or a {{NAME}}-specific inapplicability reason in the receipt.
8. **Keep or restore an improvement.** Mise: run `mise run improvement-policy` before an optional trial. Model: keep the candidate only when its named dimension improves and no protected dimension regresses; otherwise restore and verify the accepted digest.
9. **Finish maintenance last.** Mise: run `mise run mise-primitives-update` only after accepted {{NAME}} work concludes, then rerun `mise run ci`. Model: reconcile changed primitives and report any real blocker. Stop: end at the first fully accepted state; do not add unrelated work.

## Deterministic and model-owned boundary

Mise owns every deterministic command. Put schemas, parsing, validation, file generation, state transitions, task ordering, receipts, measurement, comparison, and reproducible rollback checks behind one owning Mise task. The model-owned boundary contains only work that needs semantic interpretation, domain judgment, creative generation, or direct human-sense review. A structural pass cannot prove meaning or quality.

Mise is an orchestration boundary, not a capability ceiling. Use every available, authorized capability needed for the {{NAME}} outcome, including direct vision, current web research, browser or computer interaction, tool calls, multimodal inspection, semantic reasoning, synthesis, creativity, and human-sense judgment. Mise may prepare inputs, route work, preserve evidence, and validate reproducible claims, but it must never replace direct judgment with a proxy. This skill fails if its task graph disables, imitates, or narrows a capability the outcome needs, even when every machine gate passes.

Run a long prompt, another skill, or another agentic primitive through `mise run agentic-request -- --request <file-or-dash> --runner <executable> --runner-args-json <array>`. Fill assets/agentic-request-template.json through `mise run agentic-request` and bind it to the completed {{NAME}} use-case contract, its digest, and exact promised outcome. The operation and prompt must use {{NAME}} domain terms. Give the prompt, every digest-bound SKILL.md dependency, and every open-ended primitive record a {{NAME}} role, outcome contribution, relevance reason, and expected proof. The invoking caller supplies runner authority outside the request, and the dispatcher never uses shell interpolation. Structure and term checks reject generic scaffolding; model or human judgment still decides whether each item is truly relevant, correctly used, and sufficient.

Assume an apparently nondeterministic job can be decomposed further. Move its stable inputs, queries, source receipts, schemas, coverage, dependency order, timestamps, digests, budgets, output envelopes, decision records, and rollback receipts into Mise. Repeat until only semantic interpretation, causal reasoning, creative work, direct perception, or human-sense judgment remains, then record why code cannot supply that capability.

Apply this rule to this skill itself. It has no exemption from the deterministic envelope, domain-specific primitive map, motivated decision record, tight dependency graph, proof, falsifier, failure branch, or rollback contract it applies to its work.

Every material decision states its outcome, motivation, why the path fits, owner, inputs, expected effect, proof, falsifier, and failure branch in assets/decision-records.json. Run `mise run decision-policy`; direct review still decides whether each reason is true.

Choose data structures, algorithms, file formats, batching, indexes, and cache keys from measured access patterns. Prefer single-pass reads, bounded memory, indexed lookup, append-only evidence, content-addressed invalidation, and atomic writes when they fit. Cache only deterministic work whose full inputs are declared. Never cache live judgment, mutable network state, randomness without a captured seed, or an external side effect.

## Mise task graph

Each deterministic job has one owning, {{NAME}}-specific Mise task whose outcome, motivation, concrete progress value, proof, and applicability are recorded in assets/use-case-contract.json through `mise run task-graph-policy`. Derive the job bound, cache keys, and batching from the {{NAME}} dependency and resource profile. Express prerequisite edges once, parallelize independent read-only work, serialize shared writers, and cache only tasks whose complete declared inputs and outputs determine the result. Keep live, mutating, network, model-owned, and human-judged work uncached. Measure cold and warm aggregate paths, and retain an optimization only when speed improves without a protected regression. Stop with `BLOCKED` if Mise is absent.

Every task declares its dependency list, including an empty list for a true root. Every task leads to CI, a public operation, or a required dependency. From a public operation, each dependency has one reachable path. Cycles, diamonds, disconnected tasks, unknown edges, redundant transitive edges, and nested Mise calls fail `mise run task-graph-policy`.

Map every aspect and primitive across discovery, research, experiment, decision, creation, inspection, update, validation, acceptance, restoration, deprecation, and retirement in assets/primitive-lifecycle.json through `mise run primitive-lifecycle-policy`. Every phase owner must be a real, {{NAME}}-specific task that traces to objective progress, motivation, proof, and a prevented failure.

Classify every official Mise config, task, task-config, and tool primitive in assets/mise-primitives.json through `mise run mise-primitives-policy`. Use every primitive that creates concrete {{NAME}} value, including useful creative compositions, and give each non-use a domain reason. Missing, stale, invented, or ceremonial dispositions fail.

Every Markdown reference to a package-owned file or directory must name its owning `mise run <task>` in the same prose line or fenced block. Apply this to references/, assets/, examples/, evals/, fixtures/, schemas/, templates/, data/, configuration, documentation, tests, workflows, prompts, policies, evidence, media, and every custom support root. Add each new root to `mise run lint-writing`. Direct implementation paths remain forbidden even when paired.

For every invocation, run the selected operation path and account for every remaining task as `inapplicable` only with a {{NAME}}-specific reason and proof. Fill an external receipt from assets/invocation-receipt-template.json and run `mise run invocation-policy -- <receipt>` last. The receipt proves accounting shape, not task execution; retain current command output separately and connect it to each `run` entry. The validator accounts for itself by executing; silent omission fails.

Keep the active Mise version fixed during meaningful {{NAME}} work. After the outcome and its acceptance tasks conclude, run `mise run mise-primitives-update` as the final maintenance chain. It self-updates Mise without plugins, refreshes the exact release schema catalog, and rejects unreconciled {{NAME}} dispositions. Then rerun `mise run ci` under the resulting binary and record its version and catalog digest. If package ownership or compatibility blocks it, report `BLOCKED` and never force replacement.

## Steps

1. Pick the command from the table that matches the request.
2. Before the first real task, look for a scoping skill named starting-point in the surrounding skills directory. If its SKILL.md is present, apply it first. If absent, continue without it.
3. Run the owning Mise task. Bundled scripts take flags or standard input, never prompts, and every script documents `--help`.
4. If Mise is absent, stop with `BLOCKED`. Do not bypass the task graph with a direct script command.
5. Run `mise run ci` from the skill root. Fix the first reported cause and rerun until the exit code is 0.
6. Run `mise run mise-primitives-policy` and `mise run primitive-lifecycle-policy`, then record every task as run or justified inapplicable and run `mise run invocation-policy -- <receipt>`.
7. After outcome work concludes, run `mise run mise-primitives-update`, then rerun `mise run ci` under the resulting binary. Stop with `BLOCKED` if package ownership, catalog reconciliation, or compatibility proof fails.
8. Report the result with fresh task, invocation, maintenance, and version output as evidence.

## Assets and references

- Load references/generation-contract.md through `mise run validate` before growing this skill or building another one. Every new file must meet that contract.
- Load references/resource-and-experiment-design.md through `mise run improvement-policy` before selecting a format, data structure, cache, resource measure, benchmark, or improvement trial.
- Load references/use-case-specificity.md through `mise run domain-research-policy` before defining or changing domain terms, roles, constraints, state, evidence, motivations, or primitive purposes.
- Load references/decisions.md through `mise run decision-policy` when you need the reason behind an earlier accepted change. Append one dated line per new decision.
- Load examples/example-first-run.md through `mise run validate` before the first run of this skill and whenever a reply needs the shape of a complete run. Add one example per command plus one for the likely failure.
- Load assets/eval-case-template.json through `mise run evals`, assets/use-case-contract.json through `mise run use-case-policy`, assets/mise-primitives.json through `mise run mise-primitives-policy`, assets/primitive-lifecycle.json through `mise run primitive-lifecycle-policy`, assets/decision-records.json through `mise run decision-policy`, and assets/improvement-contract.json through `mise run improvement-policy`.
- Run implementation behavior tests through `mise run test` after behavior changes. Invoke every implementation command only through its owning Mise task.

## Evals and passing evidence

Each check prints one summary line. Compare against these.

| Command | Passing last line |
| --- | --- |
| `mise run validate` | `PASS {{NAME}}: 0 problems` |
| `mise run lint-writing` | `checked files, 0 problems` |
| `mise run lint-code` | `checked files, 0 problems` |
| `mise run lint-placeholders` | `checked files, 0 placeholders` |
| `mise run evals` | `eval checks: 0 problems` |
| `mise run improvement-policy` | `improvement contract: 0 problems` |
| `mise run domain-research-policy` | `domain research: 0 problems` |
| `mise run use-case-policy` | `use-case contract: 0 problems` |
| `mise run mise-primitives-policy` | `Mise primitives: 0 problems` |
| `mise run primitive-lifecycle-policy` | `Primitive lifecycle: 0 problems` |
| `mise run task-graph-policy` | `task graph: 0 problems` |
| `mise run decision-policy` | `decision records: 0 problems` |
| `mise run invocation-policy -- <receipt>` | `invocation receipt: 0 problems` |

File counts grow with the skill. The trailing problem count must remain 0.

Update evals/evals.json through `mise run evals` whenever behavior changes, and replace every seed case before shipping. Run cases in fresh contexts, retain assertion evidence and timing, compare against the no-skill or prior-skill baseline when useful, and finish with domain or human review for meaning and quality.

## Gotchas

- The frontmatter description is the only trigger text. Keep it under 1024 characters and include the words "Use when".
- Keep every Markdown file at or below 200 lines. Route detail in references/ through `mise run validate`.
- Never name an agent product or a model in any file of this skill.
- The scaffold ships placeholder text on purpose. `mise run lint-placeholders` exits 1 until every placeholder is gone.
- JSON, YAML, TOML, a database, and a cache solve different jobs. Do not select a format before measuring ownership, mutation, query, interoperability, and human-editing needs.

## When is the work done?

Done needs fresh evidence from `mise run domain-research-policy`, `mise run use-case-policy`, `mise run mise-primitives-policy`, `mise run primitive-lifecycle-policy`, `mise run task-graph-policy`, `mise run decision-policy`, `mise run ci`, and `mise run invocation-policy -- <receipt>`: every job exits 0, validation prints PASS, writing and code checks report 0 problems, placeholder checks report 0 placeholders, evals hold at least four cases for the real job, and examples hold one complete run per command plus the likely failure. Semantic acceptance also needs source-to-claim review plus domain-swap and domain-term-removal attacks.

## Optional final improvement experiment

Run this step only after the required work is accepted. Freeze a fresh baseline, frozen evaluator, fixtures, environment, time budget, repetition count, and applicable resource measures. Change one named dimension at its smallest owning surface. Run `mise run improvement-policy`, then run the use-case experiment through its one owning Mise task. Record content digests, keep, discard, or crash status, results for every protected dimension, and reasons for each resource marked not applicable in an evidence ledger outside the editable surface. Keep the candidate only when the named dimension improves materially and no protected dimension regresses. On a worse, unknown, or invalid result, restore the last accepted version and verify its digest. Do not start an unbounded loop unless the user's terminal condition requires one.
