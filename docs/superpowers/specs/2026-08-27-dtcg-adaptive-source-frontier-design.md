# DTCG Adaptive Source Frontier Design

Date: 2026-08-27

Status: Approved for implementation

## Decision

Implement Option 2, an adaptive source frontier. Every run starts from versioned catalogs of creative mechanisms, source domains, modalities, intents, and DTCG token possibilities, then records any needed extension. It searches current and structurally distant sources, records each transfer and experiment, then narrows only after coverage, falsification, and diminishing-return gates pass. The process is fixed. Domains, source-identity relations, tokens, visual language, and proof remain input-specific.

## Outcome

`dtcg-tokens` must turn any inspectable multimodal input into source-specific DTCG 2025.10 tokens and a proof artifact. It starts from the full applicable possibility space, retains experimental tokens, and rejects defective, generic, weakly justified, or visually poor output. The run separately tests source specificity, originality, identifiability, corpus uniqueness, memorability when claimed, and bounded one-of-a-kind status.

The package must not compare execution systems. A strong-vision path owns each visual judgment. If the active path lacks strong vision, all judgment work goes to a strong-vision delegate. Checks, scores, hashes, and worker verdicts cannot replace rendered-pixel inspection.

## Boundaries

- Keep the existing 25-step pipeline and four deliverables.
- Keep every prior conformance, evidence, source-specificity, visual-review, claim, and completion gate.
- Do not add a universal creativity score or claim global uniqueness.
- Do not copy a source's surface style or treat loudness, complexity, novelty, polish, or memorability as proof of originality.
- Do not let one high score compensate for a failed DTCG, visual-defect, accessibility, touch, evidence, identifiability, or source-fit gate.
- Do not require the same framework, domain, token values, visual structure, or proof-artifact styling on every run.
- Do not commit or push this work.

## Retained Conversation Contract

The [conversation-requirements appendix](2026-08-27-dtcg-conversation-requirements.md) retains this full conversation. Load it before any package change or approval. Map each change to a requirement ID. Simplification cannot remove a requirement.

## Architecture

The feature has eleven independent owners. Each planned support file must be linked from the relevant `SKILL.md` Execution and Completion route, with its load condition stated there.

| Owner | Purpose | Planned package file |
| --- | --- | --- |
| Source frontier | Enumerate domains, mechanisms, distance rules, freshness, and stopping criteria. | `assets/creative-source-frontier.json` |
| Transfer contract | Turn a distant source relation into a falsifiable token decision without surface imitation. | `references/creative-transfer.md` |
| Experiment contract | Define hypotheses, variables, controls, falsifiers, evidence, and retained experimental tokens. | `assets/experiment-contract.json` and `references/experimental-decision.md` |
| Source identity | Build and falsify a modality-aware graph of source-specific observations and relationships. | `assets/originality-analysis-contract.json` and `references/multimodal-originality.md` |
| Screen possibility space | Enumerate visual output, physical interaction, device, body, environment, and accessibility axes before narrowing. | `assets/screen-possibility-space.json` and `references/screen-decision.md` |
| Exploration corpus | Supply typed primitives, operators, mechanisms, concepts, themes, tensions, constraints, questions, and negative patterns for deterministic synthesis. | `assets/exploration-corpus/` and `references/exploration-synthesis.md` |
| Deterministic execution | Make every step and Markdown file explicit, readable, cleanly formatted, stateful, routed, and testable; qualify the strong-vision path. | Existing execution records, `scripts/run_pipeline.py`, `scripts/lint_writing.py`, `references/writing-style.md`, and `assets/vision-probe-manifest.json` |
| Runtime orchestration | Define a dependency graph, bounded worker packets, one-writer ownership, handoffs, conflicts, and fallback. | `assets/subagent-task-contract.json` and `references/subagent-orchestration.md` |
| Research capture | Produce a dated, reproducible source record and record blocked access. | `scripts/prepare_creative_research.py` |
| Deterministic validation | Validate coverage, records, claims, orchestration, experiments, and output agreement. | `scripts/validate_exploration.py` and focused tests |
| Pipeline routing | Connect all owners to the 25 steps and Completion. | Existing execution references, evidence schema, evals, and examples |

## Identity And Orchestration

The lead owns a dependency graph, one-writer boundaries, integration, current-byte readback, claim scope, and final strong-vision judgment. Eligible independent work must be delegated when runtime support exists and must use the same typed records sequentially when it does not. Worker verdicts never replace lead verification.

Originality, identifiability, corpus uniqueness, memorability, provenance, and bounded one-of-a-kind status remain separate claims. Source identity uses located multimodal relationships, counterfactuals, matched distractors, transformations, open-set rejection, and multiple similarity representations. Global uniqueness is never claimed.

The task packets, strong-vision boundary, claim table, source-identity graph, negative controls, and matching tests are owned by the [identity and orchestration appendix](2026-08-27-dtcg-identity-and-orchestration-design.md). Load it while implementing or reviewing the source-identity or runtime-orchestration owners, `E_DELEGATION`, `E_HANDOFF`, `E_CONFLICT`, `E_VISION`, `E_SOURCE_IDENTITY`, `E_IDENTIFIABILITY`, `E_CLAIM`, or their tests.

## Deterministic Execution And Vision

`SKILL.md` must remain short and plain. Commands stay in one table. Its 25-row Execution table gives each step one purpose, one direct support-file link, and one named output. The linked procedure places `Input`, `Action`, `Save`, `Pass`, `Blocked`, and `Feeds` on separate real Markdown lines and defines each term once. HTML break tags are forbidden. Completion uses a table of observable done conditions and exact checks. Every Markdown file must follow the same heading, paragraph, list, table, link, code, and line-break rules and pass a full human readback.

The package map defines each file class and its exact load rule. A directory name never loads a file. `scripts/run_pipeline.py` owns step state, packets, hashes, dependency checks, and recorded transitions for all 25 steps. Scripts own every other safe mechanical operation. They prepare and verify judgment records but never decide taste, originality, source fit, or visual quality.

Every step checks current named inputs, performs bounded actions, saves one typed output, applies an observable gate, and names the next consumers. No agent may infer an input, rely on an earlier unsaved decision, compress several judgments into one score, or stop after one deliverable. A procedure that uses vague verbs, undefined terms, hidden dependencies, or file existence as proof fails with `E_PROCEDURE`.

The strong-vision gate uses paired fixtures for overlap, clipping, type, contrast, responsive states, interaction, source identity, taste, originality, and hallucinated visual relations. The active visual path must pass before judgment work begins. A non-passing path delegates every judgment task to a model with strong vision that passes the same probe. If no such path is available, the run returns `BLOCKED: E_VISION`.

The full step-card format, plain-language and Markdown rules, state transitions, open extension boundary, vision probe, research-to-procedure conversions, and tests are owned by the [deterministic-execution appendix](2026-08-27-dtcg-deterministic-execution-design.md). Load it while changing `SKILL.md` Execution or Completion, any Markdown file, execution reference or record, the vision path, `E_PROCEDURE`, `E_MARKDOWN`, `E_VISION`, or their tests.

## Screen Possibility Space

Before choosing token families, the run enumerates tuples across screen, composition, time, state, input, action, feedback, body, environment, access, task, and source intent. Each core family receives `applicable`, `not_applicable`, or `unknown`. Every applicable family produces an invariant, experiment, or token decision and stays recorded through narrowing.

Each tuple records its source relation, predicted effect, physical basis, device needs, fallbacks, risks, falsifier, token paths, and proof specimens. Sight, perception, touch, access, safety, and recovery checks veto failed use without choosing an aesthetic.

The full taxonomy, extension rule, decision record, and research-backed checks are owned by the [screen possibility-space appendix](2026-08-27-dtcg-screen-possibility-space-design.md). Load it while implementing or reviewing `assets/screen-possibility-space.json`, `references/screen-decision.md`, Step 07, `E_SCREEN_SPACE`, or their tests.

## Exploration Corpus

Exploration must use a typed, versioned corpus rather than an open request for interesting references. Primitives are controllable atoms; operators transform them; mechanisms predict cause and effect; concepts arrange them for a purpose; themes are source-backed propositions; tensions hold opposing forces; constraints define boundaries; questions can change decisions; and ideas are run-specific falsifiable hypotheses. Static corpus entries cannot be finished styles, templates, generic moods, or random prompts.

Step 08 builds a run-local corpus from the source identity graph, intent, applicable screen axes, distant mechanisms, active themes and antitheses, recent technology records, and rejected precedents. It then freezes at least twelve distinct candidates across combinational, exploratory, transformational, and antithetical lanes before taste filtering. Each candidate needs source relations, a primitive, operator, mechanism, theme or tension, constraint, question, predicted effect, falsifier, and candidate token paths.

The shard design, entry schema, four-lane synthesis, recorded seed, anti-fixation rules, and lineage tests are owned by the [exploration-corpus appendix](2026-08-27-dtcg-exploration-corpus-design.md). Load it while implementing or reviewing `assets/exploration-corpus/`, `references/exploration-synthesis.md`, Step 08, `E_CORPUS`, or their tests.

## Source Frontier And Research Protocol

Every run starts from the full domain catalog. It must cover at least six mechanism families, three domains structurally distant from the input, one antithetical source, and one current research source. Families include structure mapping, generative constraints, combinatorial search, inversion, exploration and exploitation, quality diversity, redundancy and feedback, selective retention, experimental controls, topology and movement, adversarial testing, and perceptual, motor, and contextual judgment.

The domain catalog includes cognitive science, experimental science, optimization, ecology, cybernetics, immunology, literature, music, movement, weaving, food pairing, architecture, aviation, engineering, organizations, and input-specific additions. Labels do not prove distance. Each record names the shared structure, surface differences, transfer, prediction, and falsifier. Search stops after quotas pass and two additions yield no new mechanism, variable, failure, identity relation, or token decision. Budget exhaustion returns `BLOCKED`.

The research record stores run and retrieval dates, query, URL, publisher, publication date, source class, version, extracted mechanism, counterevidence, and access limits. Search snippets are leads only. No finite search can inspect all arXiv records, so every run uses a broad, reproducible, multi-query sweep across relevant categories and dates, then records coverage and stopping limits. Recent preprints may propose tests but cannot alone settle a design rule.

The dated sources, evidence classes, counterarguments, and design consequences are owned by the [research-basis appendix](2026-08-27-dtcg-research-basis.md). Load it when changing a research-derived requirement or refreshing current evidence.

## Transfer And Experiment Contracts

Every transfer preserves a source relation while forbidding surface imitation. Every experiment freezes its question, variables, controls, predictions, measures, vetoes, stop rule, and rollback before confirmation. The final set retains at least three experimental tokens from three mechanism families, including one inversion or antithetical result.

The full fields, method-choice rules, retention boundary, failures, and tests are owned by the [transfer-and-experiment appendix](2026-08-27-dtcg-transfer-and-experiment-design.md). Load it while changing `references/creative-transfer.md`, `assets/experiment-contract.json`, `references/experimental-decision.md`, Step 08, `E_TRANSFER`, `E_EXPERIMENT`, `E_EXPLORATION`, or their tests.

## Selection And Vision Review

Layer 1 is non-compensatory. Any DTCG error, broken reference, unsupported claim, clipped or overlapping content, unreadable text, failed touch or input invariant, inaccessible state, missing permutation, misleading affordance, generic proof shell, source-fit failure, identity-graph failure, or invalid test vetoes the affected claim.

Layer 2 compares Layer 1 survivors side by side. Strong vision judges contextual fit, coherence, taste, originality, recognizability, purposeful irregularity, anti-fixation, repeated generated-design patterns, and source identity. Each judgment must locate evidence, name counterevidence, compare a matched alternative, and state uncertainty. The run retains a quality-diversity archive of non-dominated experiments instead of collapsing dimensions into one score. Simpler candidates win exact ties.

## Pipeline Data Flow

Step 01 freezes the run contract, owner map, and dependency graph. Steps 02 through 05 inventory modality and intent, probe each visual reviewer, and collect source observations. Step 06 builds and falsifies the source identity graph and scopes each claim. Step 07 enumerates the token universe and screen possibility space. Step 08 runs current research, builds the run-local corpus, freezes twelve or more candidates across four lanes, then creates transfers and experiments. Steps 09 and 10 integrate retained results into context requirements and signature decisions. Step 11 has one token writer. Steps 12 and 13 validate tokens and write evidence. Step 14 has one strong-vision proof author. Steps 15 and 18 through 21 may run independent read-only checks in parallel before lead adjudication. Step 22 repairs the earliest failed owner. Steps 23 and 24 package and validate. Step 25 performs current-byte readback and returns only supported claims.

No later step may invent missing evidence, transfers, experiments, observations, or results. Repair restarts at the earliest changed owner and reruns every dependent task.

## Error Handling

| Condition | Result |
| --- | --- |
| Current-source quota cannot pass | `BLOCKED: E_SOURCE_CURRENT` |
| Domain distance or transfer cannot be supported | `BLOCKED: E_SOURCE_DISTANCE` or `BLOCKED: E_TRANSFER` |
| Font catalog, rarity, license, or embedded bytes fail | `BLOCKED: E_FONT_CURRENT`, `E_FONT_RARITY`, or `E_FONT_ASSET` |
| Eligible delegation is skipped or a worker contract is invalid | `BLOCKED: E_DELEGATION` |
| Handoff schema, input hash, or output hash is missing or stale | `BLOCKED: E_HANDOFF` |
| Worker conflicts remain unresolved | `BLOCKED: E_CONFLICT` |
| Visual judgment lacks a qualified strong-vision owner | `BLOCKED: E_VISION` |
| A step is vague, unrouted, untyped, or lacks an input-to-output link | `BLOCKED: E_PROCEDURE` |
| A Markdown file is unclear, malformed, crowded, duplicated, or renders incorrectly | `BLOCKED: E_MARKDOWN` |
| A screen-space family is omitted, lacks a disposition, or loses its required result | `BLOCKED: E_SCREEN_SPACE` |
| Corpus shard, candidate lane, source relation, falsifier, or retained lineage is missing | `BLOCKED: E_CORPUS` |
| Identity graph is incomplete or its counterfactual fails | `BLOCKED: E_SOURCE_IDENTITY` |
| Matching, open-set, or transformation test fails | `BLOCKED: E_IDENTIFIABILITY` |
| Claims are conflated, unscoped, or global | `BLOCKED: E_CLAIM` |
| Experiment record is incomplete or required experimental tokens drift | `BLOCKED: E_EXPERIMENT` or `BLOCKED: E_EXPLORATION` |
| A non-compensatory gate fails | Existing exact gate code; no aggregate score can rescue it |
| Three repairs fail at the same cause | Existing deterministic stop rule |

## Test Plan

Tests must be written and observed failing before implementation.

1. Schema tests reject missing mechanisms, modality or screen-space coverage, current-source fields, task packet fields, claim boundaries, and invalid stopping states.
2. Procedure, Markdown, package-map, runner, and orchestration tests reject vague actions, implicit inputs, missing consumers, directory-only loading, commands outside command tables, HTML break tags, malformed headings, broken real lines, dense tables, undefined terms, duplicate rules, skipped eligible parallel work, concurrent writers, stale hashes, unprobed visual reviewers, unresolved conflicts, and worker `PASS` accepted without lead readback; sequential fallback must preserve the same records.
3. Identity tests reject flat feature lists, missing applicable modalities, source and output originality conflation, surface-only or palette-only uniqueness, complexity or polish used as originality, and identity relations unchanged by counterfactuals.
4. Identifiability tests reject easy distractors, missing open-set choice, missing transformations, absent confusion or false-alarm records, and unsupported one-of-a-kind wording.
5. Research and experiment tests reject snippets as evidence, surface imitation, quota filler, single-score selection, missing controls, font rarity without live rank and asset proof, unaccounted web paths, and experimental-token drift.
6. Screen-space tests reject missing axes, silent omissions, unsupported `not_applicable`, unresolved `unknown`, missing fallbacks, and narrowing that loses an applicable invariant, experiment, or token decision.
7. Corpus tests reject missing shards, generic themes, random combinations, fewer than twelve distinct candidates, absent lanes, early taste filtering, one-domain dominance, and tokens without idea lineage.
8. A positive fixture passes separate bounded claims with source relations, screen-space dispositions, all four candidate lanes, matched distractors, transformations, counterfactual loss, multi-representation neighbors, three mechanism families, one inversion, uncommon embedded fonts, and exact deliverable agreement.
9. Visual fixture tests keep the rejected board negative, audit every prior artifact, and withhold positive status from the floating-flower proof until wide, narrow, and sub-320 final pixels pass.
10. Existing DTCG, proof, artifact, evidence, Markdown, source-lineage, and package tests remain green.
11. The official Agent Skills validator, changed-script compile and help checks, `mise run ci`, current-source smoke test, logic audit, cleanup, duplicate scan, every-file current-byte trigger audit, and post-validation canonical-to-installed byte comparison form the final gate.

## Acceptance

The written design is ready for implementation only after this spec and all appendices pass open-item, contradiction, ambiguity, scope, source, claim-boundary, and voice review, then receive user approval. The implementation passes only when new tests fail for their intended reason, focused and full package checks pass on current bytes, every Execution and Completion route names its owner file, every Markdown file passes machine checks and human readback, each applicable screen family and retained idea keeps full lineage, dated research is saved, all deliverables agree, no temporary files remain, and the installed copy is byte-identical to the canonical package. No commit or push is part of acceptance.

## Research Basis

The [research-basis appendix](2026-08-27-dtcg-research-basis.md) is the canonical owner for this design's dated sources, classifications, design consequences, counterevidence, and refresh boundary.
