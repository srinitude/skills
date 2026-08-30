# Section support

Parent and backlink: [SKILL.md](../SKILL.md), every heading.

Read this file before entering any body section. It explains how each section gains its full working context.

## One direct route

Every heading owns one record in [section-support.json](../assets/section-support.json). The record order must match the body heading order.

A direct route appears before the next heading. A route below another heading cannot satisfy the current section.

Run [check_section_support.py](../scripts/check_section_support.py) after any body heading, route, or support file changes.

The schema fixes record shape. The map fills that shape with section-specific guidance. The checker tests only that structure.

## Load chain

1. Match the current body heading to its exact `heading` value.
2. Confirm the section purpose matches the task now being done.
3. Test each `load_when` against current facts.
4. Load applicable paths in `load_order`.
5. Use each path only for its named `contribution`.
6. Follow every listed `action` in order.
7. Gather every named kind of `evidence`.
8. Save the named `output` outside the skill folder.
9. Keep every `fixed_constraint` unchanged.
10. Use `model_freedom` only after the fixed bars hold.
11. Apply every `wall_clock` rule without changing order, proof, scope, or ownership.
12. Stop on any true `blocked_when` item.

Do not read every support file by habit. Read each file only when its load rule matches.

If two routes apply, preserve each route's order. Resolve shared files once, then keep both contribution notes.

If two files conflict, stop the affected claim. Name both paths and the exact conflict.

## Support roles

References explain meaning, questions, judgment frames, and stop rules. They do not decide the result.

Scripts create fields, packets, indexes, and structural checks. They do not see, feel, choose, rank, or judge.

Assets fix shapes, owner maps, input fields, and stable data. They do not turn fields into truth.

Examples remove guesses about commands, output, files, and blocked branches. They are not patterns to copy blindly.

Evals test required and forbidden acts. They do not prove taste, value, access, sight, touch, or use.

## Model judgment

The model owns every context-shaped choice. It observes, frames options, tests vetoes, weighs tradeoffs, and chooses a direction.

The model may add, split, mix, reverse, or reject options. It may find facts that no support file names.

The model records visible reasons, evidence, alternatives, tradeoffs, doubt, and the chosen result. It never exposes private reasoning traces.

The model cannot change source rights, workflow order, owner boundaries, safety bars, access bars, truth bars, or agency bars.

## Section record questions

Ask why this section exists. Ask what event opens it. Ask which file resolves each possible doubt.

Ask what each file contributes. Ask what order avoids premature choice. Ask what direct proof the claim needs.

Ask what artifact ends the section. Ask which choices stay open. Ask which rules cannot move.

Ask what the listed files cannot replace. Ask what missing fact, proof, or right must stop work.

## Structural limits

One section record has one intended meaning. Each field has one job. Do not use one field as another.

`purpose` names the section's result. `enter_when` names the event that opens the section.

`support` names files, load rules, and exact contributions. `load_order` fixes only file reading order.

`actions` names work the model must perform. `evidence` names proof the work must gather.

`output` names the saved result. `judgment_owner` stays `model`.

`deterministic_scope` names what tools may fix or check. `model_freedom` names open choices.

`fixed_constraints` names rules the model cannot move. `do_not_substitute` names false replacements.

`wall_clock` names the earliest safe start, allowed batching, serial gates, writer limits, and invalidation rules.

`blocked_when` names exact stop conditions. It cannot serve as a hidden design score.

The record may shape judgment. It must never contain a chosen state, direction, rank, score, or design verdict.
