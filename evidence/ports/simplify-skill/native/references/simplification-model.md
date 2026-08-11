# Simplification model

Parent owner and backlink: [`../SKILL.md`](../SKILL.md).

Load this file before selecting a simplification mode or working in an unfamiliar domain. This file owns the meaning of simplicity, accepted cost measures, context rules, research findings, and child-skill rationale.

## Definition

Simplification is a constrained change from a baseline to a candidate.

The candidate must reduce at least one declared cost for a named actor and task. It must also preserve every invariant unless the user approves an exact loss.

There is no context-free simplicity score. The shortest artifact can be harder to understand, execute, verify, change, or use safely.

## Name the target

Record:

- Actor: person, agent, maintainer, reviewer, or system.
- Task: what the actor must complete.
- Environment: model, runtime, tools, platform, permissions, and version.
- Baseline: current package and observed task results.
- Invariants: meanings, behavior, authority, safety, outputs, and proof.
- Cost: the exact burden to reduce.
- Loss budget: `none` or an approved bound.

If the actor, task, invariant, or cost is `unknown`, do not select a mode.

## Accepted cost measures

Choose one or more before rewriting:

- Common-path rules, steps, or linked files.
- Ambiguous branches or unresolved terms.
- Duplicate clauses or duplicate owners.
- Human retrieval, reading, memory, or decision burden.
- Agent tool calls, tokens, retries, latency, or spend.
- Hidden states, unhandled errors, or invalid transitions.
- Dependency count or change blast radius.
- Number of independently maintained surfaces.
- Test setup, execution, or diagnosis effort.

Line count and word count may support another measure. They cannot be the only accepted cost.

## Mode order

Try modes in this order. Stop at the first mode that produces an accepted candidate.

| Order | Mode | Use when | Veto |
|---|---|---|---|
| 1 | `deduplicate` | Two clauses have the same owner, meaning, strength, and conditions | Any narrow exception differs |
| 2 | `clarify` | A rule is vague, indirect, or uses an undefined term | New wording broadens or narrows behavior |
| 3 | `reorder` | Common actions are buried or dependencies appear late | Authority or required order changes |
| 4 | `progressive-disclosure` | Rare branch detail interrupts the common path | Detail is always needed or loses its load trigger |
| 5 | `extract-child` | A capability has a standalone trigger, outcome, owner, and tests | Shared invariant, atomicity, cycle, or extra coordination dominates |
| 6 | `simplify-code` | Scripts or code contain accidental structure | Behavior proof or TDD is unavailable |
| 7 | `approved-loss` | The user accepts a named approximation or removed capability | Loss is vague, unbounded, unsafe, or unapproved |

If all modes have a veto, return `NO_CHANGE`.

## Context rules

### Human communication

Use audience-first order, familiar words, direct verbs, visible conditions, and short logical units. Keep technical terms when they carry needed meaning. Test finding, understanding, execution, and verification. Readability scores are proxies, not behavior proof.

### Accessibility and information structure

Keep the common path visible. Chunk related rules and provide headings that name the action. Use progressive disclosure for optional detail, but keep a visible route to it. Do not hide safety, consent, error, or frequently used material.

### Policy and safety

Preserve authority, scope, strength, exceptions, prohibitions, approvals, and enforcement. A clearer sentence that weakens a rule is not equivalent. Keep exact legal or policy text when wording itself has authority.

### Code and refactoring

Change internal structure only with observable behavior held constant. Use tests, public interfaces, state readback, and same-environment comparisons. Removing code is useful only when the accepted behavior remains.

### Mathematics and symbolic expressions

Name the intended use. The shortest expression may be worse for evaluation, proof, factoring, numerical stability, or domain assumptions. Check equivalence under the same domain and assumptions. Prefer targeted transformations over a generic simplifier when the target form is known.

### Agents

Reduce hidden state, ambiguous choices, open-ended output, unnecessary calls, and unverified completion. Keep tool schemas, permissions, budgets, retries, stop rules, state transitions, and independent readback exact. Measure end-state success, reliability across trials, latency, and cost.

### Skills

Keep always-needed behavior in `SKILL.md`. Use a reference for branch detail that has no standalone outcome. Use a child skill only for a reusable capability with a distinct trigger and independent proof.

## Determinism and model portability

Plain language and ordered steps reduce interpretation differences. Closed enums, schemas, canonical data, and executable checks reduce them further.

They do not force every model or provider to emit identical prose. OpenAI describes seeded reproduction as best effort. Google states that schema-valid output can still contain semantically wrong values. Agent evaluations also show model, scaffold, environment, and trial sensitivity.

Use this target instead:

1. The same normalized input produces the same allowed decision path under the written rules.
2. Machine data parses against one schema and canonicalizes before hashing.
3. The end state satisfies the same invariants and acceptance thresholds.
4. Behavior claims name the model, provider, version, settings, runtime, tasks, and trials.
5. Unobserved models are `UNTESTED`, not assumed equivalent.

## Human and agent verdicts

Human `[x]`: a defined operator finds, understands, executes, and verifies the skill with less declared effort and no lost autonomy or accessibility.

Agent `[a]`: a pinned agent executes the candidate with equal or better end-state success and reliability, lower declared cost, and no authority or safety regression.

Research supports the mechanisms and test design. It does not prove either target before matched observations. Use `INSUFFICIENT EVIDENCE` until target trials support a verdict. Never make a universal human or model claim.

## Child-skill decision table

| Question | Yes | No |
|---|---|---|
| Does a current skill own the capability? | Patch or route to that owner | Continue |
| Is the capability usable without the parent? | Continue | Keep it in the parent or a reference |
| Does it have one distinct trigger and outcome? | Continue | Keep related behavior together |
| Can its interface hide internal decisions? | Continue | Fix the boundary before splitting |
| Can it be tested directly and through the parent? | Continue | Do not split |
| Will it change or recur independently? | Continue | Prefer a reference |
| Does reuse exceed discovery and maintenance cost? | Continue | Prefer a reference |
| Does the load graph remain acyclic? | Create only if every normal gate passes | Do not split |

After a split, one owner must hold each invariant. The parent must route by an explicit trigger. No child may load the parent as a required dependency.

## Research basis and limits

The authoring evidence packet freezes source copies, hashes, direct findings, inferences, and excluded sources. Key live sources include:

- U.S. Plain Writing Act: https://www.govinfo.gov/content/pkg/PLAW-111publ274/pdf/PLAW-111publ274.pdf
- Plain Language Guidelines: https://www.plainlanguage.gov/guidelines/
- W3C cognitive accessibility guidance: https://www.w3.org/TR/coga-usable/
- WCAG reading level: https://www.w3.org/WAI/WCAG21/Understanding/reading-level.html
- Progressive disclosure: https://www.nngroup.com/articles/progressive-disclosure/
- Refactoring: https://refactoring.com/
- Essential and accidental complexity: https://www.cs.unc.edu/techreports/86-020.pdf
- SymPy simplification: https://docs.sympy.org/latest/tutorials/intro-tutorial/simplification.html
- Parnas on module decomposition: https://doi.org/10.1145/361598.361623
- Anthropic prompting practices: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct
- OpenAI seeded reproduction: https://cookbook.openai.com/examples/reproducible_outputs_with_the_seed_parameter
- Gemini structured output: https://ai.google.dev/gemini-api/docs/structured-output
- AI Agents That Matter: https://arxiv.org/abs/2407.01502
- tau-bench: https://arxiv.org/abs/2406.12045
- WebArena: https://arxiv.org/abs/2307.13854

Use these sources for mechanisms and boundaries. Recheck live sources before a current factual claim. Use target behavior for acceptance.
