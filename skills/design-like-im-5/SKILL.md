---
name: design-like-im-5
description: 'Use when creating, reviewing, or revising a digital product, full flow, design system, or screen set. It keeps the user-facing core simple across parts, states, access needs, inputs, and screen sizes. Use it for product design, UX, UI, interaction, motion, or design review work.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.1.0'
---

# Design like I am five

Make a full product that feels clear, capable, and easy to use. Keep hard system work behind the screen. Do not hide truth, cost, risk, state, or control.

## One contract

This file routes the work. The linked files own the detail. Use the current intake, sources, product bytes, and named owners. Do not add a hidden method from memory.

`assets/workflow.json is the only step order.` `assets/execution-ownership.json is the only owner map.` Do not skip, merge, replace, or reorder a required step.

[assets/context-routing.json](assets/context-routing.json) binds each action to its full context. [assets/context-routing.schema.json](assets/context-routing.schema.json) fixes route shape. [assets/context-bundle.schema.json](assets/context-bundle.schema.json) fixes packet shape.

Read [references/context-routing.md](references/context-routing.md) before using a route. Run [scripts/check_context_routing.py](scripts/check_context_routing.py) after changing any route, support file, packet, or body anchor.

The model has wide room inside its owned work. Give it all current context before judgment. It may add, split, reverse, mix, or reject options. Keep source rights and vetoes fixed.

The model performs every eye, brain, and touch review. The model checks every bad design, bad output, and bad practice invariant. Scripts check structure. They do not make design judgments.

## Commands

| Command | Result                                                          |
| ------- | --------------------------------------------------------------- |
| `help`  | Show commands, inputs, outputs, context routes, and stop rules. |
| `run`   | Create, review, or revise a full product and return proof.      |

For `help`, read [examples/help.md](examples/help.md). Match its commands and input names. Do not start a run.

For `run`, record `create`, `review`, or `revise`. A review changes no product file. A revise run changes only approved files.

Read [examples/run.md](examples/run.md) before the first run. Read it again after any command, path, schema, packet, or output change.

Read [examples/context-packets.md](examples/context-packets.md) before model work. It shows context use, missing context, and the limit on script claims.

Compare `evals/files/valid-context-record.json` with `evals/files/missing-context-record.json`. They fix complete and blocked context accounting.

Read [examples/failure-missing-proof.md](examples/failure-missing-proof.md) when an input or proof field is missing. Use its stop shape. Do not guess.

## Start every run

1. Read [assets/workflow.json](assets/workflow.json). Keep its action order for the whole run.
2. Read [assets/execution-ownership.json](assets/execution-ownership.json). Give each action to its named owner.
3. Read [assets/context-routing.json](assets/context-routing.json). Keep its hash and action routes fixed for the run.
4. Read [references/intake.md](references/intake.md). Write facts in [assets/run-intake.schema.json](assets/run-intake.schema.json).
5. Validate the intake. Stop only affected work when a needed fact is absent.
6. Run `python3 scripts/run_pipeline.py start --intake INPUT --run-dir RUN`.
7. Keep `RUN` outside this skill folder. Do not hand-build its files or fields.
8. Read every run file named by the next packet. Run each source command named by the review index.

The start script writes stable scaffolds and a route hash. It does not pick states, rules, options, or results.

## Required action order

Follow every action from [assets/workflow.json](assets/workflow.json). Each capsule names what its files add. Read every applicable item before acting.

1. **[CTX-FREEZE-INTAKE] `freeze_intake`.** Read `references/intake.md` for fact and stop rules. Run `scripts/run_pipeline.py`. Use `assets/run-intake.schema.json`. Compare `examples/failure-missing-proof.md`. Test `evals/files/valid-intake.json`, `evals/files/missing-proof.json`, and `evals/context-cases.json`. Produce `run.json`. Never invent a fact.
2. **[CTX-LIST-CAPABILITIES] `list_capabilities`.** Read `references/failure.md` for proof gaps. Run `scripts/run_scaffold.py`. Use `assets/execution-ownership.json`. Compare `examples/context-packets.md`. Test `evals/context-cases.json`. Produce `capabilities.json`. Never treat structure as sight or input proof.
3. **[CTX-SOURCE-MEANING] `source_meaning`.** Read `references/research.md` for rights, age, place, gaps, and meaning. Run `scripts/run_pipeline.py`. Use `assets/model-record.schema.json`. Compare `examples/context-packets.md`. Test `evals/source-mapping.json` and `evals/context-cases.json`. Produce `source_meaning`. Never replace a source with memory or surface copy.
4. **[CTX-STATE-JUDGMENT] `state_judgment`.** Read `references/decisions.md` for open options and conflicts. Run `scripts/review_checklist.py` and `scripts/human_capability_sweep.py`. Use `assets/state-record.schema.json`. Compare `examples/context-packets.md`. Test `evals/evals.json` and `evals/context-cases.json`. Produce `state_judgment`. Never close the state set.
5. **[CTX-SELECT-RULES] `select_rules`.** Read `references/decisions.md` for the veto order. Run `scripts/run_pipeline.py`. Use `assets/simplicity-contract.json`. Compare `examples/run.md`. Test `evals/cases.json` and `evals/context-cases.json`. Produce rule IDs. Never treat one rule as the whole design.
6. **[CTX-ATOM-JUDGMENT] `atom_judgment`.** Read `references/build.md` for the atom gate. Run `scripts/check_lineage.py`. Use `assets/lineage.schema.json` and `assets/model-record.schema.json`. Compare `examples/context-packets.md`. Test `evals/files/valid-lineage.json` and `evals/context-cases.json`. Produce proved atoms and links. Never let a screen invent an atom.
7. **[CTX-PART-DESIGN] `part_design`.** Read `references/build.md` for reuse and rebuild rules. Run `scripts/check_lineage.py`. Use `assets/model-record.schema.json`. Compare `examples/run.md`. Test `evals/files/skipped-lineage.json` and `evals/context-cases.json`. Produce reusable parts and dependency effects. Never hide a one-off rule in a part.
8. **[CTX-SCREEN-DESIGN] `screen_design`.** Read `references/build.md`, `references/decisions.md`, and `references/context-routing.md`. Run `scripts/run_pipeline.py`. Use `assets/simplicity-contract.json`. Compare `examples/context-packets.md` without surface copy. Test `evals/evals.json` and `evals/context-cases.json`. Produce screens and flows from proved templates. Never choose the first known pattern.
9. **[CTX-MOTION-JUDGMENT] `motion_judgment`.** Read `references/review.md` for motion proof. Run `scripts/human_capability_sweep.py`. Use `assets/model-record.schema.json`. Compare `examples/context-packets.md`. Test `evals/cases.json` and `evals/context-cases.json`. Produce motion, sound, touch, access, and repair judgment. Never infer motion from a still.
10. **[CTX-VISUAL-REVIEW] `visual_review`.** Read `references/review.md` for whole, close, state, input, and rerender checks. Run `scripts/review_checklist.py` and `scripts/human_capability_sweep.py`. Use `assets/review-record.schema.json`. Compare `examples/context-packets.md`. Test `evals/evals.json` and `evals/context-cases.json`. Produce a current review. Never replace direct sight and input proof with code or captions.
11. **[CTX-PLAIN-READBACK] `plain_readback`.** Read `references/review.md` for state and view context. Run `scripts/run_pipeline.py`. Use `assets/model-record.schema.json`. Compare `examples/context-packets.md`. Test `evals/cases.json` and `evals/context-cases.json`. Produce a full word and meaning readback. Never accept clear words in a false state.
12. **[CTX-CHECK-LINEAGE] `check_lineage`.** Read `references/build.md` for the part chain. Run `scripts/check_lineage.py`. Use `assets/lineage.schema.json`. Compare `examples/run.md`. Test `evals/files/valid-lineage.json`, `evals/files/skipped-lineage.json`, and `evals/context-cases.json`. Produce current lineage proof. Never turn sound links into a design verdict.
13. **[CTX-FINAL-CHECK] `final_check`.** Read `references/failure.md`, `references/review.md`, and `references/context-routing.md`. Run `scripts/run_pipeline.py`, `scripts/check_context_routing.py`, and `scripts/check_lineage.py`. Use `assets/workflow.json`, `assets/execution-ownership.json`, and `assets/context-routing.json`. Compare `examples/failure-missing-proof.md`. Test `evals/contract.md`, `evals/rubric.md`, and `evals/context-cases.json`. Produce one current result. Never turn script proof into a pixel, use, access, or value claim.

## Build each model packet

Run `python3 scripts/run_pipeline.py packet --run-dir RUN --action ACTION`. Load the packet before doing that action.

The packet carries its route ID, route hash, load condition, five support classes, path contributions, output, and barred substitution. Read every required path.

Record used paths in `context_acknowledgements`. Record unavailable or unfit paths in `missing_context`. Use `BLOCKED` when missing context prevents the claim.

Creative packets require four unlike directions as a floor. There is no option ceiling. Start with a known pattern, product-shaped form, true reverse, and experimental edge.

Those starts are not boxes. The model may add, split, mix, or reverse directions. It may explore state, structure, order, words, action, form, motion, sound, touch, access, platform fit, and service effects.

Give each option a scene, claim, product fit, evidence, tradeoffs, veto check, test, and novelty note. Keep a bold option until evidence or a veto rejects it.

The model chooses and explains the direction. A script may check fields and reasons. A script must not rank, score, or choose options.

## Discover product states

Product states are found, not picked from a closed list. They may overlap, nest, affect one person, or change during use.

Find states from the person, goal, task, prior act, data, and system. Check place, device, input, access, time, content, people, and risk. Record each cause and change.

No content, wait, partial result, failure, repair, offline, permission, interruption, and success are prompts. Skip any that do not fit. Add states revealed by evidence.

For each kept state, make response options before one choice. Record unknown, mixed, stale, short-lived, and concurrent states without false certainty.

## Run every review invariant

[scripts/review_checklist.py](scripts/review_checklist.py) owns stable check IDs, rules, commands, and source links. [scripts/human_capability_sweep.py](scripts/human_capability_sweep.py) owns the open human sweep.

Apply every eye, brain, and touch factor to every check. Add any factor found in current proof. A common answer is not a fixed rule.

Eye checks cover first sight, order, groups, change, reading, color, focus, range, motion, and content. Brain checks cover truth, action, cause, memory, choice, language, feedback, risk, context, and unknowns. Touch checks cover targets, spacing, reach, inputs, cues, response, gestures, repair, settings, and effort.

Objective checks cover text and image clashes, clipped meaning, blocked controls, and lost work. Also check targets, focus, cues, states, and dead ends. Use direct render and input proof.

Bad design checks cover hidden state, false rank, false controls, silence, and lost work. Also check access, unsafe acts, fixed context, broken parts, and shifted burden.

Bad output checks cover weak claims, unseen passes, missed states, closed state lists, and missed checks. Also check weak options, script judgment, old proof, broken links, and vague results.

Bad work checks cover style-first work, surface copy, screen-first rules, early choice, and one-sided proof. Also check happy paths, late access, hidden cost, weak metrics, and false polish.

Each model answer gives the scene, observation, evidence, decision, reason, alternatives, and doubt. Use exact words, positions, sizes, timing, paths, touch, motion, sound, and feedback when seen. Mark estimates.

Keep fact, sight, inference, and proposed change apart. Use `NOT_APPLICABLE` only with evidence and a reason. Missing sight, motion, touch, or use proof means `BLOCKED` for that claim.

## Build from proved parts

Read [references/build.md](references/build.md) before atom or part work. Use `token proof -> tokens -> atoms -> molecules -> organisms -> templates -> screens -> flows`.

Run the current `dtcg-tokens` skill for all source tokens and atoms. Do not restate its process. Stop at the atom gate when that skill or proof is absent.

Mark linked high parts stale after a low-part change. Rebuild and review every affected part. A screen may not invent a low rule.

Run `python3 scripts/check_lineage.py MANIFEST`. It checks links, order, cycles, stale parts, and unused parts. It does not judge quality.

## Record model work

Use [assets/model-record.schema.json](assets/model-record.schema.json) for normal records. Use [assets/state-record.schema.json](assets/state-record.schema.json) for states. Use [assets/review-record.schema.json](assets/review-record.schema.json) for visual review.

Run `python3 scripts/run_pipeline.py record --run-dir RUN --result RESULT`. It checks fields, context acknowledgement, exact checks, options, and owner boundaries.

A filled record is not a good claim by itself. The model must support each result with current proof and the fixed veto order.

## Veto and failure rules

Safety comes first. Access comes next. Then check understanding, agency, task success, convention, expression, novelty, and build cost.

Do not trade away safety, access, understanding, or agency. Do not hide cost, risk, work, or control to make one view look calm.

Read [references/failure.md](references/failure.md) for missing facts, rights, sources, sight, atom proof, low parts, checks, context, stale rules, clashes, and change.

Return `BLOCKED` for the affected claim. Name the failed gate, missing proof, linked parts, safe work, and smallest way to resume.

## Reading and package owners

[assets/reading-contract.json](assets/reading-contract.json) owns public grade and sentence checks. [assets/reading-exceptions.json](assets/reading-exceptions.json) owns the sole exact-copy exception.

Read [references/generation-contract.md](references/generation-contract.md) only when this public skill changes. Its unchanged copy is the only full-file reading exception.

[assets/file-manifest.json](assets/file-manifest.json) owns public file roles. [evals/source-lineage.json](evals/source-lineage.json) owns public hashes and source links.

Run shape comes from [scripts/run_scaffold.py](scripts/run_scaffold.py), [scripts/run_pipeline.py](scripts/run_pipeline.py), [assets/workflow.json](assets/workflow.json), and [assets/execution-ownership.json](assets/execution-ownership.json).

Package facts come from [scripts/skill_info.py](scripts/skill_info.py), [scripts/build_examples.py](scripts/build_examples.py), [scripts/build_file_manifest.py](scripts/build_file_manifest.py), [scripts/build_lineage.py](scripts/build_lineage.py), and [assets/file-manifest.json](assets/file-manifest.json).

Validation comes from [scripts/validate_skill.py](scripts/validate_skill.py), [scripts/check_code_rules.py](scripts/check_code_rules.py), [scripts/check_placeholders.py](scripts/check_placeholders.py), [scripts/lint_writing.py](scripts/lint_writing.py), [scripts/check_reading.py](scripts/check_reading.py), and [scripts/check_context_routing.py](scripts/check_context_routing.py).

Load `scripts/tests/` only when behavior or checks change. [mise.toml](mise.toml) owns the task graph. [.github/workflows/ci.yml](.github/workflows/ci.yml) calls the same graph.

Owner and source proof comes from [scripts/audit_directories.py](scripts/audit_directories.py), [scripts/audit_ownership.py](scripts/audit_ownership.py), [scripts/check_source_lineage.py](scripts/check_source_lineage.py), and [scripts/check_evals.py](scripts/check_evals.py).

## Eval owner map

Load eval files only when an eval runs or changes. Read [evals/manifest.json](evals/manifest.json) first.

[evals/contract.md](evals/contract.md) owns method. [evals/rubric.md](evals/rubric.md) owns human grading. [assets/eval-case-template.json](assets/eval-case-template.json) owns new case shape.

[evals/cases.json](evals/cases.json) owns act cases. [evals/trigger-cases.json](evals/trigger-cases.json) owns trigger pairs. `evals/evals.json` and `evals/trigger-queries.json` own local checks.

[evals/context-cases.json](evals/context-cases.json) owns context-loss cases. `evals/speed-budgets.json` owns timing. [evals/source-lineage.json](evals/source-lineage.json) and `evals/source-mapping.json` own source proof.

Use `evals/files/valid-intake.json` and `evals/files/missing-proof.json` for run gates. Use `evals/files/valid-lineage.json` and `evals/files/skipped-lineage.json` for part gates.

Fixture passes prove the runner only. They do not prove sight, use, access, taste, product value, or a good choice.

## Return and done

Return product files and run proof. Name sources, gaps, states, options, choice, reviews, atom proof, links, stale parts, context gaps, and vetoes.

Use only `PASS`, `STALE`, or `BLOCKED` as the final run state. Never turn code or route passes into claims about pixels, use, access, or value.

Run `python3 scripts/run_pipeline.py check --run-dir RUN`. Run `python3 scripts/check_context_routing.py .`. Then run `mise run ci`.

Return `PASS` only when every record exists, every context path is accounted for, and every script gate passes. Each needed view must be seen. No veto may stay open.
