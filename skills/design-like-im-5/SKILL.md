---
name: design-like-im-5
description: 'Use when creating, reviewing, or revising a digital product, full flow, design system, or screen set. It keeps the user-facing core simple across parts, states, access needs, inputs, and screen sizes. Use it for product design, UX, UI, interaction, motion, or design review work.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
---

# Design like I am five

Make a full product that feels clear, able, and easy to use. Keep hard system work behind the screen. Do not hide truth, cost, risk, state, or control. Read [references/section-support.md](references/section-support.md) for the full support chain.

## One contract

- This file routes work. Its linked files own detail. Use current facts, sources, product files, and named owners.
- Minimize wall time only after every rule and proof stays fixed. Do not skip work, cut proof, or overlap required actions.
- [assets/speed-policy.json](assets/speed-policy.json) owns safe parallel work, serial work, reuse, and timing. [assets/speed-policy.schema.json](assets/speed-policy.schema.json) fixes its shape. [evals/speed-budgets.json](evals/speed-budgets.json) owns numeric bounds.
- [assets/workflow.json](assets/workflow.json) is the only step order. [assets/execution-ownership.json](assets/execution-ownership.json) is the only owner map. Do not skip, merge, replace, or reorder a required step.
- [assets/context-routing.json](assets/context-routing.json) binds each action to full context. [assets/context-routing.schema.json](assets/context-routing.schema.json) fixes route shape.
- [assets/context-bundle.schema.json](assets/context-bundle.schema.json) fixes packet shape. [assets/section-support.json](assets/section-support.json) owns support for each heading.
- [assets/section-support.schema.json](assets/section-support.schema.json) fixes that owner shape. Read [references/context-routing.md](references/context-routing.md) and [references/section-support.md](references/section-support.md) before work.
- Run `mise run context-routing` after a route change.
- The model has wide room only inside its owned work. It may add, split, reverse, mix, or reject options. Keep source rights, fixed rules, and vetoes.
- The model performs every eye, brain, and touch review. The model checks every bad design, bad output, and bad practice invariant.
- Mise tasks check structure. They do not make design judgments.

## Use the skill

Follow [examples/run.md](examples/run.md) for one full use. [assets/workflow.json](assets/workflow.json) keeps the run in one order.

### Commands

- **`help`:** Explain inputs, outputs, routes, tasks, and stops. Match [examples/help.md](examples/help.md). Do not start work.
- **`run`:** Create, review, or revise. Reviews change no product file. Revisions change only approved files.
- **Before model work:** Read [examples/run.md](examples/run.md) before the first run and after any task, path, packet, or output change. Read [examples/context-packets.md](examples/context-packets.md) for full, missing, and unfit context.
- **When context is incomplete:** Compare [evals/files/valid-context-record.json](evals/files/valid-context-record.json) with [evals/files/missing-context-record.json](evals/files/missing-context-record.json). These fixtures fix context accounting. Use [examples/failure-missing-proof.md](examples/failure-missing-proof.md) when a fact or proof field is missing. Do not guess.

### Prepare the run

**Run checklist:**

- [ ] **1.** Read [assets/workflow.json](assets/workflow.json), [assets/execution-ownership.json](assets/execution-ownership.json), and [assets/context-routing.json](assets/context-routing.json). Keep their order, owners, routes, and route hash fixed.
- [ ] **2.** Read [references/intake.md](references/intake.md). Write facts in [assets/run-intake.schema.json](assets/run-intake.schema.json). Validate the intake. Stop only affected work when a needed fact is absent.
- [ ] **3.** Run `mise run run-start --intake INPUT --run-dir RUN`.
- [ ] **4.** Keep `RUN` outside this skill folder. Do not hand-build its files or fields.
- [ ] **5.** Read every path named by the next packet.
- [ ] **6.** Run both review tasks when the packet calls for human review.
- [ ] **7.** Keep one writer for each run file.

> The task writes fixed run forms and a route hash. It does not pick states, rules, options, or results.

### Complete all actions in order

- Follow every action in [assets/workflow.json](assets/workflow.json). Load each named source before acting. Save the named proof.
- Each runtime task rejects an action before its exact turn.
- Inside one action, batch independent reads, renders, captures, and checks after their inputs are fixed.
- `run-start` completes actions 1 and 2. Its next action must be `source_meaning`.

1. **[CTX-FREEZE-INTAKE] `freeze_intake`.** `run-start` completes this action. Apply [references/intake.md](references/intake.md) and [evals/files/missing-proof.json](evals/files/missing-proof.json). Never invent a fact.
2. **[CTX-LIST-CAPABILITIES] `list_capabilities`.** `run-start` completes this action. Use `mise run run-scaffold` to inspect its output. Apply [references/failure.md](references/failure.md). Never treat structure as sight or touch proof.
3. **[CTX-SOURCE-MEANING] `source_meaning`.** Use `mise run run-packet`. Apply [references/research.md](references/research.md), [evals/source-mapping.json](evals/source-mapping.json), and [evals/context-cases.json](evals/context-cases.json). The model records source meaning.
4. **[CTX-STATE-JUDGMENT] `state_judgment`.** Use `mise run run-packet`, `mise run review-checklist`, and `mise run human-sweep`. Apply [references/product-states.md](references/product-states.md). The model finds states.
5. **[CTX-SELECT-RULES] `select_rules`.** Run `mise run run-select-rules --run-dir RUN`. Apply [assets/simplicity-contract.json](assets/simplicity-contract.json) and [references/decisions.md](references/decisions.md). Keep the fixed veto order.
6. **[CTX-ATOM-JUDGMENT] `atom_judgment`.** Use `mise run run-packet`. Apply [assets/lineage.schema.json](assets/lineage.schema.json) and [evals/files/valid-lineage.json](evals/files/valid-lineage.json). The model judges proved atoms.
7. **[CTX-PART-DESIGN] `part_design`.** Use `mise run run-packet` and `mise run lineage-file MANIFEST`. Apply [evals/files/skipped-lineage.json](evals/files/skipped-lineage.json). The model builds linked parts.
8. **[CTX-SCREEN-DESIGN] `screen_design`.** Use `mise run run-packet`. Apply [references/build.md](references/build.md) and [examples/context-packets.md](examples/context-packets.md). The model builds from proved parts.
9. **[CTX-MOTION-JUDGMENT] `motion_judgment`.** Use `mise run run-packet` and `mise run human-sweep`. Apply [references/review.md](references/review.md). The model judges live motion. Never infer motion from a still.
10. **[CTX-VISUAL-REVIEW] `visual_review`.** Use `mise run run-packet`, `mise run review-checklist`, and `mise run human-sweep`. Apply [assets/review-record.schema.json](assets/review-record.schema.json). The model reviews current pixels and use.
11. **[CTX-PLAIN-READBACK] `plain_readback`.** Use `mise run run-packet`. Apply [evals/cases.json](evals/cases.json). The model reads all visible words in context. Never accept clear words in a false state.
12. **[CTX-CHECK-LINEAGE] `check_lineage`.** Use `mise run lineage-file MANIFEST --run-dir RUN`. Apply [assets/lineage.schema.json](assets/lineage.schema.json). The task checks links, records proof, and advances no design claim.
13. **[CTX-FINAL-CHECK] `final_check`.** Run `mise run run-check --run-dir RUN`, then `mise run complete`. Apply [evals/contract.md](evals/contract.md) and [evals/rubric.md](evals/rubric.md). Never turn task proof into design proof.

### Build each model packet

- Run `mise run run-packet --run-dir RUN --action ACTION`. Load the packet before that action.
- Follow [assets/context-bundle.schema.json](assets/context-bundle.schema.json). Keep the packet's route, hash, support, output, and barred swaps.
- Record used paths in `context_acknowledgements`. Record unavailable or unfit paths in `missing_context`. Use `BLOCKED` when missing context prevents the claim.
- Create four unlike starts: known, product-shaped, reversed, and strange. There is no option cap. These starts are prompts, not boxes.
- Add, split, mix, or reverse starts. Explore state, structure, order, words, action, form, motion, sound, touch, access, platform fit, and service effects.
- Give each option a scene, claim, fit, proof, costs, veto check, test, and novelty note. Keep a bold option until evidence or a veto rejects it.
- The model chooses and explains the direction. A Mise task may check fields. It must not rank, score, or choose.
- Run `mise run run-record --run-dir RUN --result RESULT`. Save that result before any next action.

## Judge the design

Use [references/decisions.md](references/decisions.md) with [assets/simplicity-contract.json](assets/simplicity-contract.json). The model owns every design choice.

### Veto and failure rules

- Apply vetoes in this order: safety, access, understanding, agency, task success, convention, expression, novelty, then build cost.
- Do not trade away safety, access, understanding, or agency. Do not hide cost, risk, work, or control.
- Read [references/failure.md](references/failure.md) for missing facts, rights, sources, sight, atom proof, context, clashes, and change.
- Return `BLOCKED` for the affected claim. Name the failed gate, missing proof, linked parts, safe work, and smallest way to resume.

### Discover product states

- Read [references/product-states.md](references/product-states.md), use [assets/state-record.schema.json](assets/state-record.schema.json), and compare [examples/product-states.md](examples/product-states.md).
- Use [evals/section-support-cases.json](evals/section-support-cases.json) to reject closed lists and task-owned choices. Run `mise run review-checklist` and `mise run human-sweep`.
- Find product states instead of picking them from a closed list. States may overlap, nest, mix, conflict, or change during use.
- Check the person, goal, past act, data, system, place, device, input, time, content, people, and risk.
- Treat common states as prompts only. Skip unfit prompts. Add any state shown by proof.
- Make unlike response options for each state. Record causes, links, change, proof, doubts, tradeoffs, and the model's choice.
- Keep unknown, mixed, stale, short-lived, and concurrent states open. Do not ask for private chain-of-thought.

### Run every review invariant

- Run `mise run review-checklist` for fixed check IDs. Run `mise run human-sweep` for open eye, brain, and touch prompts.
- Read [references/review.md](references/review.md) for proof rules. Apply every relevant human factor to every check.
- **Eye:** Check first sight, order, groups, change, text, color, focus, range, motion, and content.
- **Brain:** Check truth, action, cause, memory, choice, language, feedback, risk, context, and unknowns.
- **Touch:** Check targets, gaps, reach, inputs, cues, response, gestures, repair, settings, and effort.
- **Objective failures:** Reject text or image overlap, clipped meaning, blocked controls, lost work, dead ends, false focus, and false cues.
- **Bad work:** Check bad design, output, and practice. Include hidden state, false control, old proof, weak options, surface copy, and early choice.
- **Answer shape:** Give the scene, observation, proof, choice, reason, options, costs, vetoes, and doubt. Mark estimates.
- **Evidence state:** Keep fact, sight, inference, and change apart. `NOT_APPLICABLE` needs proof. Missing needed proof means `BLOCKED` for that claim.
- **Invalidation:** A source or product change invalidates affected captures and checks.

### Build from proved parts

- Read [references/build.md](references/build.md) before atom or part work.
- Use `token proof -> tokens -> atoms -> molecules -> organisms -> templates -> screens -> flows`.
- Run the current `dtcg-tokens` skill for all source tokens and atoms. Do not restate its method.
- Stop at the atom gate when that skill or proof is absent. A screen may not invent a low rule.
- Mark linked high parts stale after a low change. Rebuild and review every affected part.
- Run `mise run lineage-file MANIFEST`. It checks links, order, loops, stale parts, and unused parts. It does not judge quality.

## Prove and finish

Use [assets/model-record.schema.json](assets/model-record.schema.json) for saved proof. Use [evals/contract.md](evals/contract.md) for the final gate.

### Record model work

- Use [assets/model-record.schema.json](assets/model-record.schema.json) for normal work.
- Use [assets/state-record.schema.json](assets/state-record.schema.json) for states.
- Use [assets/review-record.schema.json](assets/review-record.schema.json) for visual review.
- Run `mise run run-record --run-dir RUN --result RESULT`.
- The task checks fields, context use, options, and owner lines. A filled record is not a good claim by itself.
- The model must support each result with current proof. Record visible reasons, options, costs, vetoes, and doubt.

### Reading and package owners

- [assets/reading-contract.json](assets/reading-contract.json) owns public grade and sentence checks. [assets/reading-exceptions.json](assets/reading-exceptions.json) owns the sole exact-copy exception.
- `SKILL.md` uses standard YAML frontmatter and portable CommonMark only.
- Read [references/generation-contract.md](references/generation-contract.md) only when this public skill changes. Its unchanged copy is the sole full-file reading exception.
- [assets/file-manifest.json](assets/file-manifest.json) owns public file roles. [evals/source-lineage.json](evals/source-lineage.json) owns public hashes and source links.
- Run shape comes from [assets/workflow.json](assets/workflow.json) and [assets/execution-ownership.json](assets/execution-ownership.json). Run `mise run run-scaffold` to view it.
- [mise.toml](mise.toml) owns all executable tasks and links. [.github/workflows/ci.yml](.github/workflows/ci.yml) runs the same check graph.
- Keep UTF-8, LF newlines, ATX headings, blank block spacing, one-line blocks, and relative local links. Every block stays clean, readable, and agent-parsable.
- Run `mise run skill-info` for package facts. Run `mise run generate` after public sources change.
- Run `mise run complete` for the full fixed gate. Its acyclic links force every needed check to run.
- Mise runs independent read-only checks in parallel and never caches or skips a required task.

### Eval owner map

- Load eval files only when an eval runs or changes.
- Read [evals/manifest.json](evals/manifest.json), [evals/contract.md](evals/contract.md), [evals/rubric.md](evals/rubric.md), and [assets/eval-case-template.json](assets/eval-case-template.json) first.
- Read [references/proof-ladder.md](references/proof-ladder.md), [assets/proof-ladder.json](assets/proof-ladder.json), [examples/proof-ladder.md](examples/proof-ladder.md), and [evals/pilot-cases.json](evals/pilot-cases.json). Run `mise run proof-ladder`.
- Run each pilot twice from clean context. Compare action order, context use, proof classes, vetoes, and status. Any clash is `STALE`. Wording and safe creative directions may differ.
- [evals/cases.json](evals/cases.json) and [evals/trigger-cases.json](evals/trigger-cases.json) own act and trigger cases.
- [evals/evals.json](evals/evals.json), [evals/trigger-queries.json](evals/trigger-queries.json), and [evals/section-support-cases.json](evals/section-support-cases.json) own local checks.
- [evals/context-cases.json](evals/context-cases.json) owns context-loss cases. [evals/speed-budgets.json](evals/speed-budgets.json) owns timing.
- [evals/source-lineage.json](evals/source-lineage.json) and [evals/source-mapping.json](evals/source-mapping.json) own source proof.
- Use [evals/files/valid-intake.json](evals/files/valid-intake.json) and [evals/files/missing-proof.json](evals/files/missing-proof.json) for run gates.
- Use [evals/files/valid-lineage.json](evals/files/valid-lineage.json) and [evals/files/skipped-lineage.json](evals/files/skipped-lineage.json) for part gates.
- Fixture passes prove the task only. They do not prove sight, use, access, taste, product value, or a good choice.

### Return and done

**Completion checklist:**

- [ ] Return product files and run proof. Follow [examples/run.md](examples/run.md) and the stop shape in [examples/failure-missing-proof.md](examples/failure-missing-proof.md).
- [ ] Name sources, gaps, states, options, choice, reviews, atom proof, links, stale parts, context gaps, and vetoes.
- [ ] Use only `PASS`, `STALE`, or `BLOCKED`. Never turn task passes into claims about pixels, use, access, or value.
- [ ] Run `mise run run-check --run-dir RUN`. Then run `mise run complete`.
- [ ] Return `PASS` only after `mise run complete` exits with code `0`.
- [ ] Confirm that every record and context path is present. See each needed view. Leave no veto open.
