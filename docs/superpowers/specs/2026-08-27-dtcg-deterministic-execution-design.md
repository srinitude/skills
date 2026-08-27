# DTCG Deterministic Execution Appendix

Date: 2026-08-27

Status: Approved for implementation

Parent and backlink: [DTCG Adaptive Source Frontier Design](2026-08-27-dtcg-adaptive-source-frontier-design.md), Deterministic Execution And Vision.

Load trigger: Use this appendix while changing `SKILL.md` Execution or Completion, `references/execution-guide.md`, `references/vision-execution.md`, `references/deterministic-execution.md`, `assets/execution-io-map.json`, `assets/execution-step-contract.json`, `assets/vision-probe-manifest.json`, or their tests. The package files own runtime procedure. This appendix owns the approved clarity, state, routing, and visual-review design.

## Outcome

Another agent must be able to run all 25 steps without guessing what a word means, inventing an input, skipping a record, or treating one deliverable as completion. The instructions must stay short, plain, and easy to scan. Deterministic rules must control state and proof. Vision must control visual judgment.

## Skill Body Shape

`SKILL.md` keeps only the rules needed on every run:

1. Outcome and four deliverables.
2. A command table.
3. The vision requirement.
4. A compact 25-row Execution table.
5. Non-negotiable boundaries.
6. A Completion table with observable done conditions.

The Execution table uses these columns:

| Column | Meaning |
| --- | --- |
| `#` | Fixed step number. |
| `Step` | Short verb phrase and direct link to the exact procedure section. |
| `Use` | Exact reference, asset, or script required by that step. |
| `Produces` | One named saved record that becomes a later input. |

Every row must name at least one relative path under `references/`, `assets/`, or `scripts/`. The row must not compress input, action, save, pass, and blocked text into one cell. Those fields live in the linked procedure.

The Completion table uses these columns:

| Column | Meaning |
| --- | --- |
| `Gate` | Short name for one required result. |
| `Done only when` | Observable condition that decides completion. |
| `Check with` | Exact reference, asset, script, or saved record that owns the check. |

Commands stay in one table. Each command row states accepted input, created output, and claim limit. Shell commands stay in a separate command table in `references/validation.md`; they do not appear inside prose paragraphs.

## Four Fixed Properties

| Property | Exact meaning |
| --- | --- |
| Simple | A reader can find the next action, required input, saved output, pass rule, and recovery without interpreting jargon. |
| Deterministic | The same current inputs, versions, run ID, and seed produce the same route, record order, and checks. Subjective review still records evidence, counterevidence, and uncertainty. |
| Open-ended | An extension record can add a new input, intent, token type, device, method, or design relation without changing the core step contract. A finite catalog never claims to list infinity. |
| Customizable | The user can set purpose, audience, source boundary, contexts, outputs, constraints, experiments, and claim limits. No fixed visual style or proof shell survives across runs. |

Open-ended choice changes content. It does not change required evidence, human invariants, DTCG rules, safety, or completion gates.

## Step Card

Each linked procedure section uses the same six labels. Each label starts on its own line.

**Input**

Name the exact record, path, schema version, and current hash required to start.

**Action**

Give ordered imperative sentences. Each sentence has one verb, one object, and one visible result. Name the required reference, asset, or script at the point of use.

**Save**

Name one output record, its schema, its path, and the fields that the next step consumes.

**Pass**

State an observable predicate. A score, opinion, or file existence check cannot stand in for the required result.

**Blocked**

Name the exact error code, failed predicate, saved evidence, and smallest permitted recovery.

**Feeds**

Name every later step that consumes the saved output. No later step may read an unstated input.

These labels describe a state change:

`verified input -> bounded action -> saved output -> deciding check -> next verified input`

## Plain Language Rules

- Use common words when they preserve the exact rule.
- Define a required term the first time it appears.
- Use one action per sentence.
- State who acts, what is inspected, what is saved, and what decides the result.
- Replace `consider`, `explore`, `improve`, `appropriate`, `interesting`, `high quality`, and similar open verbs with an object, method, and deciding check.
- Do not use a metaphor as an instruction.
- Do not rely on an example to carry a rule.
- Do not require the reader to infer a missing link from the previous step.
- Keep a procedure section below 120 lines. Split it by owner when it exceeds that limit.
- Use lists for actions and tables for mappings, commands, and comparison rules.

The package must not discuss or rank AI system quality. Research findings about uneven execution are converted into the plain rules in this appendix. The only allowed AI-system requirement is the strong-vision gate below.

## Markdown Package Contract

Every Markdown file under `skills/dtcg-tokens/` must pass a machine check and a full human readback. `references/writing-style.md` owns these rules. `scripts/lint_writing.py` checks them across the full Markdown file list.

| Area | Required form |
| --- | --- |
| Structure | One H1, ordered H2 sections, no skipped heading level, and a blank line after each heading. |
| Opening | State purpose and load condition before detailed rules. |
| Paragraphs | One idea per paragraph. Use short blocks. Split a paragraph when it contains separate actions. |
| Sentences | Prefer common words, active voice, literal language, and direct error text. Define every uncommon term. |
| Lists | Use lists for ordered actions or equal items. Do not hide a sequence in prose. |
| Tables | Use tables only for commands, mappings, schemas, or comparisons. Keep them at four columns or fewer when practical. |
| Links | Use meaningful labels and relative paths. State when the linked file must be read or run. |
| Code | Use fenced blocks only for exact commands, schemas, or examples. Put commands in a command table before the block. |
| Line breaks | Use real Markdown lines and blank lines between blocks. Never use HTML break tags. Shorten table cells and move detailed lines to a linked procedure. |
| Density | Keep `SKILL.md` below 200 lines. Review any support file at 150 lines and split it before 200 unless one procedure would become harder to follow. |
| Duplication | One file owns each rule. Other files link to that owner instead of restating it. |

The human readback checks whether headings expose the file's shape, steps scan in order, tables fit without dense prose, labels are consistent, examples clarify a real ambiguity, and the page looks calm rather than crowded. A parser or word metric cannot settle that review.

## State And Routing Rules

1. Step 01 creates the run contract, owner map, dependency graph, and file map.
2. A step starts only when every named input exists, parses, has the expected schema version, and matches its recorded hash.
3. A step reads only the references and assets named by its route.
4. A step saves its output before any dependent step starts.
5. A step cannot mark itself `PASS` from memory. It checks the saved current bytes.
6. A failed step saves `BLOCKED`, the exact predicate, evidence paths, and recovery path.
7. Repair begins at the earliest owner that can change the failed predicate.
8. Every dependent output is invalidated and rerun after an upstream change.
9. Three failed repairs at the same cause stop the run.
10. Step 25 rereads every current deliverable and saved gate. Earlier reports do not prove current state.

`assets/execution-io-map.json` owns the machine-readable edge list. `assets/execution-step-contract.json` owns record fields and status transitions. `references/execution-guide.md` owns the human-readable route. Tests must prove that all three agree.

## Strong Vision Gate

The active model must have strong vision and must inspect the actual source and rendered pixels. If it cannot do that, every source interpretation, design choice, artifact review, taste judgment, originality judgment, and visual claim must be delegated to a model with strong vision. That delegate must pass the same probe. If no passing path exists, return `BLOCKED: E_VISION`.

The package uses `assets/vision-probe-manifest.json`, paired visual fixtures, and a truth record. The probe covers:

| Probe family | Required observation |
| --- | --- |
| Overlap and clipping | Locate unintended collision, crop, hidden content, unsafe occlusion, and edge loss. Separate them from purposeful overlap. |
| Typography | Locate unreadable size, measure, spacing, hierarchy, fallback, missing glyph, and text overflow. |
| Contrast and perception | Locate failed contrast, color-only meaning, weak grouping, false hierarchy, and lost forced-color or grayscale meaning. |
| Responsive behavior | Compare wide, narrow, zoomed, rotated, segmented, and reduced-motion states. |
| Interaction | Locate broken focus, target, drag alternative, state feedback, interruption, recovery, and touch problems. |
| Source identity | Match source-bearing relations against comparable distractors and reject a generic surface match. |
| Taste and originality | Separate objective defects, supported qualitative judgment, uncertainty, and personal preference. |
| Hallucination control | Reject named elements or relations that are absent from the pixels. |

The path passes only when it finds every hard-veto fixture, locates at least 90 percent of major defects, invents no element, classifies fact versus inference versus judgment correctly, and records counterevidence for each qualitative decision. The answer must use region IDs from the fixture manifest. A script may validate record shape and counts. It cannot judge the pixels.

The runtime review uses the same pattern on user artifacts:

1. Inspect the whole frame at native detail.
2. Inspect every required region and state.
3. Record visible facts before conclusions.
4. Test inter-element relationships, not only object presence.
5. Compare at least one matched alternative and one negative control.
6. Record the strongest counterreading.
7. Apply objective vetoes before taste or originality judgment.
8. Rerender after repair and inspect final pixels again.

Captions, OCR, DOM data, accessibility trees, screenshots at reduced detail, metrics, and structural checks may support the review. None may replace the pixel review.

## Reliability Rules Converted Into Procedure

The skill uses these rules without explaining their research origin:

| Observed risk | Required procedure |
| --- | --- |
| Long instructions can hide decisive material. | Keep each step local. Repeat the deciding constraint beside its action and pass check. Load only named records. |
| Conflicting instructions can be applied in the wrong order. | Freeze authority, fixed constraints, forbidden actions, and conflict rules in Step 01. Stop on an unresolved conflict. |
| Long plans can lose preconditions or effects. | Save each step transition. Check preconditions before action and effects after save. |
| New combinations can break even when familiar parts pass. | Test composed token paths, cross-axis cases, and held-out combinations. Do not infer composition from parts. |
| Output syntax may look right while meaning is wrong. | Use schemas for shape, then run semantic and visual checks on current bytes. |
| Self-review can repeat the same error. | Separate authoring, objective checks, counterevidence, and final adjudication. Never accept a worker or prior self-review as proof. |
| Visual systems can name objects but miss relations. | Test overlap, containment, distance, order, alignment, continuity, cause, and state changes explicitly. |
| Text can distract from pixel evidence. | Record visible facts first. Use text and structure as support, not as a substitute for vision. |
| Easy comparisons can inflate success. | Use matched distractors, negative samples, counterfactuals, transformed states, and `none of the above`. |
| More work can create repeated variants. | Deduplicate by source relation, mechanism, predicted effect, screen tuple, and token path before evaluation. |

## Failure And Tests

Return `BLOCKED: E_PROCEDURE` when a step card lacks a label, uses an undefined term, names no owner file, has more than one saved output without an explicit schema, has no deciding predicate, or does not identify its next consumer. Return `BLOCKED: E_MARKDOWN` when any Markdown file fails structure, link, line-break, density, plain-language, duplication, or human readback checks.

Focused tests must reject vague actions, a step with implicit input, a saved record with no consumer, a pass rule based only on file existence, pass and blocked text compressed into an unreadable table cell, commands outside a command table, a distant constraint that is absent from the local step, a visual verdict from captions alone, an unprobed reviewer, malformed headings, HTML break tags, dense tables, undefined terms, duplicate rules, and a final claim based on stale bytes. A positive fixture must trace one run through all 25 step records with exact hashes, routes, outputs, failures, repairs, and final readback. It must also render and pass every Markdown file.

## Research Owner

The [research-basis appendix](2026-08-27-dtcg-research-basis.md) owns the dated evidence behind these plain execution and visual-review rules.
