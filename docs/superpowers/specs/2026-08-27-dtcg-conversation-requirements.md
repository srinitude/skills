# DTCG Conversation Requirements Appendix

Date: 2026-08-27

Status: Approved for implementation

Parent and backlink: [DTCG Adaptive Source Frontier Design](2026-08-27-dtcg-adaptive-source-frontier-design.md), Retained Conversation Contract.

Load trigger: Use this appendix before changing, testing, or approving any part of the `dtcg-tokens` package. It owns the retained user requirements from this conversation. Package references own runtime procedure.

## Rule

An update may change wording, file layout, or implementation method. It may not weaken, merge, or drop a requirement in this ledger. Each implementation change must map to at least one requirement ID. Each requirement must map to a file owner and a deciding check.

## Output And Portability

| ID | Required result | Planned owner | Deciding proof |
| --- | --- | --- | --- |
| R-001 | The package is named `dtcg-tokens` and follows the current Agent Skills format and repository shape. | `SKILL.md`, package validator | Official format validation and repository checks pass. |
| R-002 | The package stays platform-agnostic. | `SKILL.md`, references | No client-only path or tool is presented as universal. |
| R-003 | Every run produces DTCG 2025.10 token JSON, evidence JSON, one standalone proof HTML file, and one run record. | execution and evidence owners | Four current deliverables agree on run ID, paths, hashes, and claims. |
| R-004 | Token generation starts from the full named possibility space and narrows only with recorded reasons. | token, screen, and exploration catalogs | Every catalog family has one disposition and no applicable result disappears. |
| R-005 | The source context can add more tokens and new token categories. | extension protocol | Each extension has a source, definition, type, use, test, and lineage. |

## Input And Intent

| ID | Required result | Planned owner | Deciding proof |
| --- | --- | --- | --- |
| R-010 | The skill accepts any inspectable mix of image, video, audio, text, document, code, data, interface, spatial, material, interaction, or sensor evidence. | multimodal input catalog | Every supplied item is inventoried and every applicable modality is inspected. |
| R-011 | Input enumeration covers intent as well as format. | input and intent catalog | Purpose, audience, task, context, desired effect, exclusions, and claim limits are explicit. |
| R-012 | New input forms and intents enter through a dated extension record. | extension protocol | No unknown input is silently forced into an existing class. |
| R-013 | Current date and source date affect standards, research, technology, fonts, comparison corpora, and claims. | current-date and research owners | One fresh date anchor and dated source records exist for the run. |
| R-014 | Typography uses Google Fonts that rank outside the most popular 50 percent in a live same-date catalog and still pass source-fit review. | font selection owner | Rank evidence, three eligible candidates, selected token paths, licenses, embedded font hashes, offline use, and final vision review pass. |

## Vision And Judgment

| ID | Required result | Planned owner | Deciding proof |
| --- | --- | --- | --- |
| R-020 | Actual source pixels and rendered pixels drive every visual judgment. | vision execution and review | Full-frame and region records locate visible evidence on current renders. |
| R-021 | The active model must have strong vision. If it does not, all judgment work goes to a model with strong vision that passes the same probe. | vision probe and orchestration | The visual owner passes the fixture probe or the run stops with `E_VISION`. |
| R-022 | Objective defects and qualitative judgment stay separate. | defect and judgment catalogs | Defects, taste, originality, fit, and uncertainty have separate records. |
| R-023 | Review checks overlap, clipping, crop, hierarchy, type, contrast, grouping, state, affordance, touch, responsiveness, motion, and recovery. | visual and invariant owners | Every applicable check has a located result and no unresolved veto. |
| R-024 | Sight, perception, and touch invariants protect human use without fixing an aesthetic. | screen possibility and invariant owners | Failed physical or perceptual use vetoes the claim; unfamiliar style alone does not. |
| R-025 | Every prior generated artifact in this project is inventoried and audited before it can act as a positive precedent. Rejected work stays a negative fixture. | precedent and negative-pattern owner | The artifact inventory has one current visual result per item, and no rejected shell, image, or layout is reused as a positive template. |
| R-026 | The rejected reference board supplied in this conversation is a negative fixture for overlap, hierarchy, type, composition, and generic generated-design review. | vision probe owner | Its failure labels, regions, and counterexample pairs are saved and never treated as a target style. |
| R-027 | Existing floating-flower output cannot become a positive example until wide, narrow, and sub-320 pixel review passes on final bytes. | proof and precedent owners | Responsive pixel review has no unresolved overflow, clipping, or defect veto. |

## Originality And Non-Slop Claims

| ID | Required result | Planned owner | Deciding proof |
| --- | --- | --- | --- |
| R-030 | Non-work-slop, non-design-slop, non-AI-slop, originality, taste, source fit, identifiability, uniqueness, and bounded one-of-a-kind status are separate claims. | judgment and claim owners | Each claim has its own evidence, counterevidence, uncertainty, and result. |
| R-031 | Objective bad-output markers include defects, broken behavior, missing states, false affordance, weak information structure, inaccessible use, and unsupported claims. | defect catalog | Each applicable marker is resolved once. |
| R-032 | Qualitative review checks taste, restraint, coherence, intentional irregularity, source identity, cliché, generic generated patterns, and conceptual strength. | qualitative judgment owner | Comparative vision review names evidence and the strongest counterreading. |
| R-033 | Identifiability uses matched distractors, transformations, open-set rejection, and confusion records. | multimodal originality owner | The output remains attributable to its source under the declared test. |
| R-034 | Corpus uniqueness uses several representations and frozen comparison bounds. | originality owner | Nearest neighbors, thresholds, corpus date, and representation disagreements are saved. |
| R-035 | Global uniqueness is never claimed. | claim owner | `globally_unique` remains false in every run. |

## Proof Artifact

| ID | Required result | Planned owner | Deciding proof |
| --- | --- | --- | --- |
| R-040 | The standalone HTML proof is authored from the generated tokens and source relations. | proof authoring owner | Visible regions trace to token paths, source evidence, and claim checks. |
| R-041 | Proof styling, content, layout, and interaction change for every source and run. | proof originality owner | No reusable visual shell survives the shell comparison and ablation tests. |
| R-042 | The proof exercises every applicable token type, context, state, viewport, interaction, permutation, and retained experiment. | proof coverage owner | Coverage maps and rendered specimens match the applicable sets exactly. |
| R-043 | The package contains the extracted proof criteria, not the external source name or URL used to derive them. | proof references | A content scan finds no forbidden source mention. |
| R-044 | Structural passes, hashes, and screenshots do not prove visual quality. | proof review owner | Final current pixels receive strong-vision review after assembly. |

## Exploration And Research

| ID | Required result | Planned owner | Deciding proof |
| --- | --- | --- | --- |
| R-050 | Exploration uses a typed corpus of primitives, operators, mechanisms, concepts, themes, tensions, constraints, questions, technology records, and negative patterns. | exploration corpus | All required shards parse, hash, and route into Step 08. |
| R-051 | Search covers related and unrelated domains, current web sources, relevant recent arXiv work, and installed skill-discovery sources. | source frontier and research record | Quotas, queries, sources, transfers, counterevidence, and stop reasons are saved. |
| R-052 | Creative generation uses fixed combinational, exploratory, transformational, and antithetical lanes. | exploration synthesis | At least three distinct candidates exist in each lane before evaluation. |
| R-053 | Every candidate states source relations, primitive, operator, mechanism, theme or tension, constraint, question, predicted effect, falsifier, and token paths. | idea record | Incomplete or cosmetic-only candidates fail. |
| R-054 | Experiments use frozen hypotheses, controls, variables, thresholds, stop rules, evidence, and rollback. | experiment contract | Confirmation cannot change the frozen question after seeing the result. |
| R-055 | The final token set retains at least three experimental tokens from three mechanism families, including one inversion or antithesis. | experiment and token owners | Token, experiment, evidence, specimen, and review paths agree. |
| R-056 | Recent technology widens the candidate set only through a maturity record, support boundary, fallback, and current evidence. | technology watch | A new item cannot enter production only because it is new. |
| R-057 | Research uses the `find-skills` workflow on skills.sh for creativity and experiment methods, then checks each useful source before transfer. | source frontier and research record | Query, result URL, source package, extracted mechanism, limits, and disposition are saved. |
| R-058 | Research inventories every available source-relevant web path and uses it or records why it is not applicable or unavailable. | research record | A capability ledger accounts for search, source opening, rendered inspection, academic search, and other relevant paths. |

## Execution, Delegation, And Writing

| ID | Required result | Planned owner | Deciding proof |
| --- | --- | --- | --- |
| R-060 | `generate` and `prove` execute all 25 steps. No agent may stop after one file or the skill body. | execution guide and records | All step records are `PASS` on current inputs before completion. |
| R-061 | Every Execution step links its exact reference, asset, or script. Completion links the owner of every done condition. | `SKILL.md` routes | Link and routing checks find no orphan step or gate. |
| R-062 | Each procedure puts `Input`, `Action`, `Save`, `Pass`, `Blocked`, and `Feeds` on separate lines and defines their meaning. | execution references | Step-card validation passes for all 25 steps. |
| R-063 | Commands appear in tables. Procedures use real Markdown lines and never use HTML break tags. | writing style owner | Markdown lint and rendered readback pass. |
| R-064 | Every Markdown file is plain, readable, cleanly structured, and visually calm. | writing style and lint owner | Machine checks and full human readback pass every Markdown file. |
| R-065 | Independent eligible work uses runtime subagents with one writer per deliverable, typed packets, hashes, counterevidence, and lead verification. | orchestration owner | Parallel and sequential fallback tests produce the same record contract. |
| R-066 | Reliability research is translated into short rules, typed state, explicit checks, negative cases, and recovery. The skill does not compare AI system tiers. | deterministic execution owner | Content scan and behavior tests pass; only the strong-vision rule names an AI model requirement. |
| R-067 | The process is fixed while source, intent, tokens, experiments, proof design, and extensions stay open. | all owners | Same inputs and seed reproduce records; new valid extensions do not require a new core process. |
| R-068 | `SKILL.md` explains the role and load trigger for `references/`, `assets/`, `scripts/`, `scripts/tests/`, `evals/`, `evals/files/`, `examples/`, task configuration, and workflow files. | package map owner | Package-map tests find every file class and reject directory-only loading. |
| R-069 | Every mechanical state change, packet, hash, dependency check, validation, and audit uses a script where a deterministic operation is possible. Scripts prepare and verify judgment records but never make taste or visual judgments. | pipeline runner and script owners | Runner tests cover all 25 steps, and the judgment boundary test passes. |

## Validation And Publication Boundary

| ID | Required result | Planned owner | Deciding proof |
| --- | --- | --- | --- |
| R-070 | Validation covers format, scripts, JSON, Markdown, links, behavior, vision, evidence, proof, package health, cleanup, and canonical-to-installed bytes. | validation owner | Every current required check passes with no skipped gate. |
| R-071 | Logic audit checks the bounded package for contradictions, missing links, and unsupported claims. | logic-audit gate | No unresolved critical or high-impact finding remains. |
| R-072 | Commits and published artifacts contain no AI co-creation or coauthoring metadata. | publication boundary | Metadata scan passes before any later authorized publication. |
| R-073 | No commit or push is part of the current work. | current task boundary | Repository history and remote state remain unchanged by this work. |
| R-074 | Final validation rereads every current package byte and audits the exact trigger or consumer for every file. | file-trigger audit owner | The current-byte audit reports no unread or unrouted file. |
| R-075 | Paired vision fixtures name exact negative regions, expected failures, and pass counterconditions without treating a countercondition as a positive design precedent. | vision probe owner | Fixture-pair and pixel-review tests pass. |
| R-076 | The skill and all support files use simple language and a consistent visual structure. | writing style owner | Markdown lint and human readback find no unclear step, malformed table, or hidden rule. |
| R-077 | Canonical and installed skill copies are compared only after every package check passes. | installation boundary | Final byte comparison is exact and no earlier sync masks a canonical failure. |

## Acceptance

The implementation cannot pass while any requirement lacks an owner, deciding proof, or current result. Simplification may remove repeated wording. It may not remove a requirement, proof duty, boundary, or failure state.
