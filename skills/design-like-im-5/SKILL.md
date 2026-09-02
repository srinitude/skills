---
name: design-like-im-5
description: 'Use when creating, reviewing, or revising a digital product, full flow, design system, or screen set. It keeps the user-facing core simple across parts, states, access needs, inputs, and screen sizes. Use it for product design, UX, UI, interaction, motion, or design review work.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.2.0'
---

# Design like I am five

Make a usable product without hiding truth, cost, risk, state, or control. Route full support through [references/section-support.md](references/section-support.md) and `mise run section-support`.

## One contract

- Minimize elapsed time to a verified owning-artifact change. Preserve exploratory and experimental breadth, correctness, every gate, and same-executor vision.
- [assets/speed-policy.json](assets/speed-policy.json), [assets/speed-policy.schema.json](assets/speed-policy.schema.json), and [evals/speed-budgets.json](evals/speed-budgets.json) own safe scheduling and bounds through `mise run complete`.
- [assets/workflow.json](assets/workflow.json) is the only step order. [assets/execution-ownership.json](assets/execution-ownership.json) is the only owner map. Check both through `mise run task-graph` and `mise run ownership`. Do not skip, merge, replace, or reorder a required step.
- [assets/context-routing.json](assets/context-routing.json), [assets/context-routing.schema.json](assets/context-routing.schema.json), and [assets/context-bundle.schema.json](assets/context-bundle.schema.json) own routes and packet shape through `mise run context-routing`. [assets/section-support.json](assets/section-support.json) and [assets/section-support.schema.json](assets/section-support.schema.json) own heading support through `mise run section-support`. Read [references/context-routing.md](references/context-routing.md) and [references/section-support.md](references/section-support.md) through those tasks. Recheck after route changes.
- The model may add, split, mix, reverse, or reject options inside rights and vetoes. The model performs every eye, brain, and touch review. The model checks all bad design, bad output, and bad practice rules. It reads [references/review.md](references/review.md) through `mise run human-sweep` and keeps canvases clean. Scripts cannot grant design or cleanliness `PASS`.
- Truth, access, task, perception, familiarity, standards, uniqueness, craft, and resilience pass separately. Start from zero trust. Mark inherited work `STALE`, observe first, retain passes, and reject needless redesign. Bind claims to evidence; never average away failure.
- The paramount visual-proof rule makes direct sight final after measured gates. The same invoking strong vision-capable executor inspects current pixels through every applicable available vision capability. Inspect whole views and details across states, viewports, input paths, before and after each change and invalidation. Proxies may veto, never grant visual `PASS`; missing sight is `BLOCKED`.
- In multipage work, justify one canonical page per depth-one owner and inspect its descendants. Wrong placement, duplicates, orphans, stale work, and moves block affected views. Current eye, brain, and touch judgment must pass.
- Inspect each mobile and tablet layer in portrait and landscape, including rotation when supported. Prove hierarchy, reach, safe areas, wrapping, density, spacing, state, and input. Add orientation APIs only when anatomy or behavior changes; otherwise keep one owner and prove both contexts.
- `skill-factory` update mode owns package changes. Run `mise run domain-research-policy`, `mise run use-case-policy`, `mise run mise-primitives-policy`, `mise run primitive-lifecycle-policy`, `mise run task-graph-policy`, `mise run decision-policy`, and `mise run improvement-policy`. Use `mise run agentic-request` for long prompts and open product-design work. Mise tasks check structure. They do not make design judgments.
- During Computer Use audits, use `computer-use` as the platform-neutral local application-control capability. The same executor must directly inspect the active design application, including Figma, and own every disposition; otherwise the item is `BLOCKED`. A Figma audit also needs its lifecycle receipt and one source record per item. Outside that audit, this skill stays standalone.

## Ordered workflow

Follow [examples/run.md](examples/run.md) through `mise run examples` for one full use. [assets/workflow.json](assets/workflow.json) keeps the run in one order through `mise run task-graph`.

### Commands

- **`help`:** Explain inputs, outputs, routes, tasks, and stops. Match [examples/help.md](examples/help.md) through `mise run run-help`. Do not start work.
- **`run`:** Create, review, or revise. Reviews change no product file. Revisions change only approved files.
- **Before model work:** Read [examples/run.md](examples/run.md) and [examples/context-packets.md](examples/context-packets.md) through `mise run examples` before the first run and after any task, path, packet, or output change.
- **When context is incomplete:** Compare [evals/files/valid-context-record.json](evals/files/valid-context-record.json) with [evals/files/missing-context-record.json](evals/files/missing-context-record.json) through `mise run evals`. Use [examples/failure-missing-proof.md](examples/failure-missing-proof.md) through `mise run examples` when a fact or proof field is missing. Do not guess.

### Prepare the run

**Run checklist:**

- [ ] **1.** Read [assets/workflow.json](assets/workflow.json), [assets/execution-ownership.json](assets/execution-ownership.json), and [assets/context-routing.json](assets/context-routing.json) through `mise run run-scaffold`. Keep their order, owners, routes, and route hash fixed.
- [ ] **2.** Read [references/intake.md](references/intake.md) and write facts in [assets/run-intake.schema.json](assets/run-intake.schema.json) through `mise run run-start`. Stop only affected work when a needed fact is absent.
- [ ] **3.** Run `mise run run-start --intake INPUT --run-dir RUN`.
- [ ] **4.** Keep `RUN` outside this skill folder. Do not hand-build its files or fields.
- [ ] **5.** Read every path named by the next packet.
- [ ] **6.** Run both review tasks when the packet calls for human review.
- [ ] **7.** Keep one writer for each run file.

> The task writes fixed run forms and a route hash. It does not pick states, rules, options, or results.

### Complete all actions in order

- Follow every action in [assets/workflow.json](assets/workflow.json) through `mise run task-graph`. Load each named source before acting. Save the named proof.
- Each run task rejects work before its turn.
- Inside one action, batch independent reads, renders, captures, and checks after their inputs are fixed.
- `run-start` completes actions 1 and 2. Its next action must be `source_meaning`.

1. **[CTX-FREEZE-INTAKE] `freeze_intake`.** Mise: `mise run run-start` checks and freezes the intake. Model: apply [references/intake.md](references/intake.md) and [evals/files/missing-proof.json](evals/files/missing-proof.json) through that task; never invent a fact.
2. **[CTX-LIST-CAPABILITIES] `list_capabilities`.** Mise: `mise run run-scaffold` exposes the fixed capability form. Model: apply [references/failure.md](references/failure.md) through that task and never treat structure as sight or touch proof.
3. **[CTX-SOURCE-MEANING] `source_meaning`.** Mise: `mise run run-packet` routes [references/research.md](references/research.md), [evals/source-mapping.json](evals/source-mapping.json), and [evals/context-cases.json](evals/context-cases.json). Model: record source meaning and counterevidence.
4. **[CTX-STATE-JUDGMENT] `state_judgment`.** Mise: run `mise run run-packet`, `mise run review-checklist`, and `mise run human-sweep`. Model: apply [references/product-states.md](references/product-states.md) through those tasks and discover product states.
5. **[CTX-SELECT-RULES] `select_rules`.** Mise: run `mise run run-select-rules --run-dir RUN`. Model: apply [assets/simplicity-contract.json](assets/simplicity-contract.json) and [references/decisions.md](references/decisions.md) through that task and keep the fixed veto order.
6. **[CTX-ATOM-JUDGMENT] `atom_judgment`.** Mise: run `mise run run-packet`. Model: apply [assets/lineage.schema.json](assets/lineage.schema.json) and [evals/files/valid-lineage.json](evals/files/valid-lineage.json) through that task and judge only proved atoms.
7. **[CTX-PART-DESIGN] `part_design`.** Mise: run `mise run run-packet` and `mise run lineage-file MANIFEST`. Model: apply [evals/files/skipped-lineage.json](evals/files/skipped-lineage.json) through those tasks and build only from locked lower owners.
8. **[CTX-SCREEN-DESIGN] `screen_design`.** Mise: run `mise run run-packet`. Model: apply [references/build.md](references/build.md) and [examples/context-packets.md](examples/context-packets.md) through that task and build screens from proved parts.
9. **[CTX-MOTION-JUDGMENT] `motion_judgment`.** Mise: run `mise run run-packet` and `mise run human-sweep`. Model: apply [references/review.md](references/review.md) through those tasks. Never infer motion from a still.
10. **[CTX-VISUAL-REVIEW] `visual_review`.** Mise: run `mise run run-packet`, `mise run review-checklist`, and `mise run human-sweep`. Model: apply [assets/review-record.schema.json](assets/review-record.schema.json) through those tasks and inspect current pixels and use.
11. **[CTX-PLAIN-READBACK] `plain_readback`.** Mise: run `mise run run-packet`. Model: apply [evals/cases.json](evals/cases.json) through that task. Never accept clear words in a false state.
12. **[CTX-CHECK-LINEAGE] `check_lineage`.** Mise: run `mise run lineage-file MANIFEST --run-dir RUN` with [assets/lineage.schema.json](assets/lineage.schema.json). Model: keep the result bounded to links and proof, never design quality.
13. **[CTX-FINAL-CHECK] `final_check`.** Mise: run `mise run run-check --run-dir RUN`, then `mise run complete` with [evals/contract.md](evals/contract.md) and [evals/rubric.md](evals/rubric.md). Model: reject any attempt to turn task proof into design proof.

### Build each model packet

- Run `mise run run-packet --run-dir RUN --action ACTION`. Apply [assets/context-bundle.schema.json](assets/context-bundle.schema.json), load its routes, and record used or missing context. Missing required context is `BLOCKED`.
- Create at least four unlike starts: known, product-shaped, reversed, and strange. Add, split, mix, or reverse them across state, structure, words, action, motion, sound, touch, access, platform, and service effects. Give each a scene, claim, proof, cost, veto, test, and novelty note. Keep a bold option until evidence or a veto rejects it.
- Before retaining a design layer, apply [references/controlled-comparisons.md](references/controlled-comparisons.md) through `mise run test`. Compare material directions and freeze evidence before sight. Current eye, brain, touch, bad-design, bad-output, and bad-practice judgment chooses. Small optimization needs request, defect, or threshold proof.
- Create the canonical focus-intent record in [references/build.md](references/build.md) through `mise run test`. Judge what the person should notice, where, when, how, why, and in what order. Fields and prominence do not prove success.
- Save the result before any next action with `mise run run-record --run-dir RUN --result RESULT`.

## Judge the design

Use [references/decisions.md](references/decisions.md) with [assets/simplicity-contract.json](assets/simplicity-contract.json) through `mise run run-select-rules`. The model owns every design choice.

### Veto and failure rules

- Apply vetoes in this order: safety, access, understanding, agency, task success, convention, expression, novelty, then build cost.
- Do not trade away safety, access, understanding, or agency. Do not hide cost, risk, work, or control.
- Read [references/failure.md](references/failure.md) through `mise run run-check` for missing facts, rights, sources, sight, atom proof, context, clashes, and change.
- Return `BLOCKED` for the affected claim. Name the failed gate, missing proof, linked parts, safe work, and smallest way to resume.
- Diagnose observed work as `DEFECT`, `MEDIOCRE`, `SLOP`, or `PASS`, not its creator. A passed floor, familiar convention, unusual style, build convenience, or numeric average cannot cancel another failed gate.

### Discover product states

- Read [references/product-states.md](references/product-states.md), [assets/state-record.schema.json](assets/state-record.schema.json), [examples/product-states.md](examples/product-states.md), and [evals/section-support-cases.json](evals/section-support-cases.json) through `mise run run-packet`, then run `mise run review-checklist` and `mise run human-sweep`.
- Discover states from proof, not a closed list. Check person, goal, past act, data, system, place, device, input, time, content, people, and risk. States may overlap, nest, conflict, or change.
- Create unlike responses. Record causes, links, proof, doubt, tradeoffs, and choice. Keep unknown, mixed, stale, short-lived, and concurrent states open. Never request private chain-of-thought.

### Run every review invariant

- Run `mise run review-checklist` for fixed IDs and `mise run human-sweep` for open prompts. Apply [references/review.md](references/review.md) through that task.
- **Eye, brain, touch:** Check sight order, groups, change, content, truth, action, memory, and language. Also check feedback, risk, targets, gaps, reach, cues, gestures, repair, and effort.
- **Failures:** Reject overlap, clipping, blocked controls, lost work, dead ends, and false focus. Reject hidden state, old proof, weak options, residue, mixed-status zones, and deferred cleanup.
- **Evidence:** Separate fact, sight, inference, and change. `NOT_APPLICABLE` needs proof; missing proof is `BLOCKED`. A source or product change invalidates affected captures and checks.
- **Answer:** Give scene, observation, proof, choice, reason, options, costs, vetoes, doubt, and marked estimates.
- **Quality:** Use [references/review.md](references/review.md) through `mise run human-sweep`. Require uniqueness, standards, and familiarity after truth, access, task, and perception. Keep eye, brain, touch, whole-view, detail, responsive, and input-path evidence.

### Build from proved parts

- Read [references/build.md](references/build.md) through `mise run lineage-file` before atom or part work.
- Use `token proof -> tokens -> atoms -> molecules -> organisms -> UI composition templates -> screens -> flows`.
- A UI composition template is reusable screen structure. A Code Connect mapping template is a repository mapping artifact. It is not a product-design layer, and neither class proves the other.
- Run the current `dtcg-tokens` skill for all source tokens and atoms. Do not restate its method.
- Stop at the atom gate when that skill or proof is absent. A screen may not invent a low rule.
- Mark linked high parts stale after a low change. Rebuild and review every affected part.
- Run `mise run lineage-file MANIFEST`. It checks links, order, loops, stale parts, and unused parts. It does not judge quality.

## Prove and finish

Use [assets/model-record.schema.json](assets/model-record.schema.json) for saved proof through `mise run run-record`. Use [evals/contract.md](evals/contract.md) through `mise run evals` for the final gate.

### Record model work

- Route normal, state, and visual records through `mise run run-record` using [assets/model-record.schema.json](assets/model-record.schema.json), [assets/state-record.schema.json](assets/state-record.schema.json), and [assets/review-record.schema.json](assets/review-record.schema.json).
- Run `mise run run-record --run-dir RUN --result RESULT`. It checks shape only. The model supplies current proof, visible reasons, options, costs, vetoes, and doubt.

### Reading and package owners

- [assets/reading-contract.json](assets/reading-contract.json) and [assets/reading-exceptions.json](assets/reading-exceptions.json) own reading rules through `mise run reading`. `SKILL.md` uses a standard YAML header and portable CommonMark only. Read [references/generation-contract.md](references/generation-contract.md) through `mise run generate` only after public change.
- [assets/file-manifest.json](assets/file-manifest.json) owns roles through `mise run file-manifest`; [evals/source-lineage.json](evals/source-lineage.json) owns hashes through `mise run source-lineage`; [assets/workflow.json](assets/workflow.json) and [assets/execution-ownership.json](assets/execution-ownership.json) own run shape through `mise run run-scaffold`.
- [mise.toml](mise.toml) owns tasks through `mise run task-graph`; [.github/workflows/ci.yml](.github/workflows/ci.yml) calls `mise run ci`. Keep UTF-8, LF, ATX headings, blank block spacing, and relative links. Every block stays clean, readable, and agent-parsable.
- Run `mise run skill-info`, regenerate changed public sources with `mise run generate`, and finish with `mise run complete`. Mise runs independent checks in parallel and never caches or skips a required task.

### Eval owner map

- Load eval files only for eval work. [evals/manifest.json](evals/manifest.json), [evals/contract.md](evals/contract.md), [evals/rubric.md](evals/rubric.md), [assets/eval-case-template.json](assets/eval-case-template.json), [evals/cases.json](evals/cases.json), [evals/trigger-cases.json](evals/trigger-cases.json), [evals/evals.json](evals/evals.json), [evals/trigger-queries.json](evals/trigger-queries.json), [evals/section-support-cases.json](evals/section-support-cases.json), [evals/context-cases.json](evals/context-cases.json), and [evals/speed-budgets.json](evals/speed-budgets.json) run through `mise run evals`.
- [references/proof-ladder.md](references/proof-ladder.md), [assets/proof-ladder.json](assets/proof-ladder.json), [examples/proof-ladder.md](examples/proof-ladder.md), and [evals/pilot-cases.json](evals/pilot-cases.json) run through `mise run proof-ladder`. Run pilots twice; invariant clashes are `STALE`.
- [evals/source-lineage.json](evals/source-lineage.json) and [evals/source-mapping.json](evals/source-mapping.json) own source proof through `mise run source-lineage`. [evals/files/valid-intake.json](evals/files/valid-intake.json) and [evals/files/missing-proof.json](evals/files/missing-proof.json) run through `mise run run-start`; [evals/files/valid-lineage.json](evals/files/valid-lineage.json) and [evals/files/skipped-lineage.json](evals/files/skipped-lineage.json) run through `mise run lineage-file`.
- Fixture passes prove only the task, never sight, use, access, taste, product value, or choice.

### Return and done

**Completion checklist:**

- [ ] Return product files and run proof. Name sources, gaps, states, options, choice, reviews, atom proof, links, stale parts, context gaps, and vetoes. Follow [examples/run.md](examples/run.md) and the stop shape in [examples/failure-missing-proof.md](examples/failure-missing-proof.md) through `mise run examples`.
- [ ] Use only `PASS`, `STALE`, or `BLOCKED`. Never turn task passes into claims about pixels, use, access, or value. Confirm that every record and context path is present, each needed view was seen, and no veto remains open.
- [ ] Run `mise run run-check --run-dir RUN`. Then run `mise run complete`.
- [ ] Return `PASS` only after `mise run complete` exits with code `0`.
- [ ] **Optional final step:** After required product work passes, run `mise run improvement-policy`, change one named part at its smallest owner, and rerun `mise run complete`. Keep it only if that part gets better. Speed, truth, sight, choice, tests, and every current rule must not get worse. If any part gets worse, restore the last passed version and check its digest.
