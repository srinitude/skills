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

This file routes the work. The linked files own the detail. Use the current intake, current sources, current product bytes, and these owners. Do not add a hidden method from memory.

`assets/workflow.json is the only step order.` `assets/execution-ownership.json is the only owner map.` Do not skip, merge, replace, or reorder a required step.

The model has wide room inside its owned work. Give it all current context before judgment. Let it add, split, reverse, mix, or reject options. Keep source rights and vetoes fixed.

The model performs every eye, brain, and touch review. The model checks every bad design, bad output, and bad practice invariant. Scripts check structure. They do not make design judgments.

## Commands

| Command | Result                                                        |
| ------- | ------------------------------------------------------------- |
| `help`  | Show the two commands, needed inputs, output, and stop rules. |
| `run`   | Create, review, or revise a full product and return proof.    |

For `help`, read [examples/help.md](examples/help.md). Match its command list and input names. Do not start a run.

For `run`, record one mode: `create`, `review`, or `revise`. A review changes no product file. A revise run may change only approved files.

Read [examples/run.md](examples/run.md) before the first run. Read it again when a command, path, schema, or printed result changes.

Read [examples/failure-missing-proof.md](examples/failure-missing-proof.md) when an input or proof field is missing. Use its stop shape. Do not guess the field.

## Start every run

1. Read [assets/workflow.json](assets/workflow.json). Keep its action order for the whole run.
2. Read [assets/execution-ownership.json](assets/execution-ownership.json). Give each action to its named owner.
3. Read [references/intake.md](references/intake.md). Write all facts in [assets/run-intake.schema.json](assets/run-intake.schema.json).
4. Validate the intake. Stop only the affected work when a needed fact is absent.
5. Run `python3 scripts/run_pipeline.py start --intake INPUT --run-dir RUN`.
6. Keep `RUN` outside this skill folder. Do not hand-build its files or fields.
7. Read `run.json`, `capabilities.json`, `state-matrix.json`, `review-checklist.json`, `render-plan.json`, and `dependency-manifest.json` before model work. Run the source command named by the review index.

The start script writes stable scaffolds. It does not pick product states. It does not pick design rules, options, or results.

## Required action order

Follow every action from [assets/workflow.json](assets/workflow.json). Use this map to load the right owner and support.

1. `freeze_intake`: Use [references/intake.md](references/intake.md) and [assets/run-intake.schema.json](assets/run-intake.schema.json).
2. `list_capabilities`: Read `capabilities.json`. Mark web, browser, render, capture, motion, and sight gaps.
3. `source_meaning`: Read [references/research.md](references/research.md). Build and record a `source_meaning` packet.
4. `state_judgment`: Read the open state matrix and rich checklist. Use [assets/state-record.schema.json](assets/state-record.schema.json).
5. `select_rules`: Use [assets/simplicity-contract.json](assets/simplicity-contract.json). Read [references/decisions.md](references/decisions.md) for conflicts.
6. `atom_judgment`: Read [references/build.md](references/build.md). Run the full atom owner named there.
7. `part_design`: Build molecules, organisms, and templates from proved low parts.
8. `screen_design`: Build screens and flows from proved templates. Do not add a one-off low rule.
9. `motion_judgment`: Judge change, timing, calm paths, input response, sound, and touch feedback.
10. `visual_review`: Read [references/review.md](references/review.md). Use [assets/review-record.schema.json](assets/review-record.schema.json).
11. `plain_readback`: Read every user-facing word. Use [assets/model-record.schema.json](assets/model-record.schema.json).
12. `check_lineage`: Use [assets/lineage.schema.json](assets/lineage.schema.json). Run `python3 scripts/check_lineage.py MANIFEST`.
13. `final_check`: Check all records, links, rules, renders, stale parts, bytes, and vetoes.

## Build each model packet

Run `python3 scripts/run_pipeline.py packet --run-dir RUN --action ACTION`. Load the packet before doing that action.

The packet names the frozen intake, source paths, found states, view plan, checklist, proved parts, stale links, rules, and vetoes. Read every named context file that applies.

Creative packets require four unlike directions as a floor. There is no option ceiling. Start with a known pattern, a product-shaped form, a true reverse, and an experimental edge.

Those four starts are not boxes. The model may add, split, mix, or reverse directions. It may explore state, structure, order, words, action, visual form, motion, sound, touch, access, platform fit, and service effects.

Give each option a concrete scene, claim, product fit, evidence, tradeoffs, veto check, test, and novelty note. Keep a bold option until evidence or a veto rejects it.

The model chooses and explains the direction. A script may check that options and reasons exist. A script must not rank, score, or choose them.

## Discover product states

Product states are found, not picked from a closed list. They may overlap, nest, appear for one person, or change during use.

Find states from the person, goal, task, prior act, data, and system. Check place, device, input, access, time, content, people, and risk. Record each cause and change.

No content, wait, partial result, failure, repair, offline, permission, interruption, and success are prompts. They are not the state set. Skip one that does not fit. Add any state the evidence reveals.

For each kept state, make response options before one choice. Record unknown, mixed, stale, short-lived, and concurrent states without false certainty.

## Run every review invariant

[scripts/review_checklist.py](scripts/review_checklist.py) owns the full stable checklist. The start script writes its exact IDs, rules, commands, and source links to `review-checklist.json`. Run its named source command before review.

[scripts/human_capability_sweep.py](scripts/human_capability_sweep.py) owns the open human sweep. Apply every named eye, brain, and touch factor to every check. Add any factor found in current proof.

Every eye, brain, and touch invariant must always be reviewed. Its answer stays bound to the state and context. A common answer is not a fixed rule.

The eye checks first sight, order, groups, state change, reading, color, focus, view range, motion, and content range.

The brain checks current truth, next action, cause and effect, memory, choice, language, feedback, risk, context, and unknowns.

Touch checks targets, spacing, reach, input modes, use cues, response, gestures, repair, settings, and effort.

Objective checks cover text and image clashes, clipped meaning, and blocked controls. They also cover lost work, target clashes, focus traps, lost cues, state conflicts, and dead ends. These need direct render and input proof.

Bad design checks cover hidden state, false rank, false controls, and silence. They also cover lost work, blocked access, unsafe acts, fixed context, broken parts, and shifted burden.

Bad output checks cover weak claims, unseen passes, missed states, and closed state lists. They also cover missed checks, weak options, script judgment, old proof, broken links, and vague results.

Bad work checks cover style-first work, surface copy, screen-first rules, and early choice. They also cover one-sided proof, happy-path tests, late access, hidden cost, weak metrics, and false polish.

Each model answer starts with the rich scene prompt. It must then give observation, evidence, decision, reason, alternatives, and doubt.

Use exact words, positions, sizes, timing, paths, touch, motion, sound, and feedback when seen. Mark estimates. Keep fact, sight, inference, and proposed change apart.

Use `NOT_APPLICABLE` only with evidence and a reason. Missing sight, motion, touch, or use proof means `BLOCKED` for that claim.

## Build from proved parts

Read [references/build.md](references/build.md) before atom or part work. Use this one-way chain:

`token proof -> tokens -> atoms -> molecules -> organisms -> templates -> screens -> flows`

Run the current `dtcg-tokens` skill for all source tokens and atoms. Do not copy or restate its process here. Stop at the atom gate if that skill or its proof is absent.

When a low part changes, mark each linked high part stale. Rebuild and review all affected parts. A screen may not invent a color, type, space, icon, word rule, motion, or action.

Run `python3 scripts/check_lineage.py MANIFEST`. The script checks links, order, cycles, stale parts, and unused parts. It does not judge product quality.

## Record model work

Save the result with the packet's named schema. Use [assets/model-record.schema.json](assets/model-record.schema.json) for normal judgment records.

Use [assets/state-record.schema.json](assets/state-record.schema.json) for `state_judgment`. Use [assets/review-record.schema.json](assets/review-record.schema.json) for `visual_review`.

Run `python3 scripts/run_pipeline.py record --run-dir RUN --result RESULT`. The script checks required fields, exact invariant IDs, options, and owner boundaries.

The script cannot turn a filled record into a good design claim. The model must support each result with current proof and the fixed veto order.

## Veto and failure rules

Safety comes first. Access comes next. Then check understanding, agency, task success, convention, expression, novelty, and build cost.

Do not trade away safety, access, understanding, or agency. Do not hide cost, risk, work, or control to make one view look calm.

Read [references/failure.md](references/failure.md) when a fact, right, source, sight tool, atom proof, low part, or check is missing. Also read it for stale rules, source clashes, and low-part change.

Return `BLOCKED` for the affected claim. Name the failed gate, missing proof, linked parts, safe finished work, and smallest way to resume.

## Reading and package owners

[assets/reading-contract.json](assets/reading-contract.json) owns public grade and sentence checks. [assets/reading-exceptions.json](assets/reading-exceptions.json) owns the sole exact-copy exception.

Read [references/generation-contract.md](references/generation-contract.md) only when this public skill changes. Its unchanged copy is the only full-file reading exception.

[assets/file-manifest.json](assets/file-manifest.json) owns every public file role. [evals/source-lineage.json](evals/source-lineage.json) owns public hashes and source claim links.

Run `mise run ci` from this skill root. Use direct checks only when that runner is absent. State that limit in the result.

## Exact support map

Run shape comes from [scripts/run_scaffold.py](scripts/run_scaffold.py), [scripts/run_pipeline.py](scripts/run_pipeline.py), [assets/workflow.json](assets/workflow.json), and [assets/execution-ownership.json](assets/execution-ownership.json).

Package facts come from [scripts/skill_info.py](scripts/skill_info.py), [scripts/build_examples.py](scripts/build_examples.py), [scripts/build_file_manifest.py](scripts/build_file_manifest.py), [scripts/build_lineage.py](scripts/build_lineage.py), and [assets/file-manifest.json](assets/file-manifest.json).

Validation comes from [scripts/validate_skill.py](scripts/validate_skill.py), [scripts/check_code_rules.py](scripts/check_code_rules.py), [scripts/check_placeholders.py](scripts/check_placeholders.py), [scripts/lint_writing.py](scripts/lint_writing.py), and [scripts/check_reading.py](scripts/check_reading.py). Load `scripts/tests/` only when behavior or checks change. [mise.toml](mise.toml) owns the local task graph. [.github/workflows/ci.yml](.github/workflows/ci.yml) calls that same graph.

Owner and source proof comes from [scripts/audit_directories.py](scripts/audit_directories.py), [scripts/audit_ownership.py](scripts/audit_ownership.py), [scripts/check_source_lineage.py](scripts/check_source_lineage.py), and [scripts/check_evals.py](scripts/check_evals.py).

## Eval owner map

Load eval files only when an eval runs or changes. Read [evals/manifest.json](evals/manifest.json) first.

[evals/contract.md](evals/contract.md) owns test method. [evals/rubric.md](evals/rubric.md) owns human grading. [assets/eval-case-template.json](assets/eval-case-template.json) owns new case shape.

[evals/cases.json](evals/cases.json) owns act cases. [evals/trigger-cases.json](evals/trigger-cases.json) owns trigger pairs. `evals/evals.json` and `evals/trigger-queries.json` own local checks.

`evals/speed-budgets.json` owns cold and warm timing. [evals/source-lineage.json](evals/source-lineage.json) and `evals/source-mapping.json` own source proof.

Use `evals/files/valid-intake.json` and `evals/files/missing-proof.json` for run gates. Use `evals/files/valid-lineage.json` and `evals/files/skipped-lineage.json` for part gates.

Fixture passes prove the runner only. They do not prove sight, use, access, taste, product value, or a good choice.

## Return and done

Return the product files and run proof. Name the result, sources, source gaps, found states, options, and choice. Name all reviews, atom proof, part links, stale parts, and vetoes.

Use only `PASS`, `STALE`, or `BLOCKED` as the final run state. Never turn a code pass into a claim about pixels, use, access, or value.

Run `python3 scripts/run_pipeline.py check --run-dir RUN`. Then run `mise run ci`.

Return `PASS` only when every model record exists and every script gate passes. Each needed view must be seen. No veto may stay open.
