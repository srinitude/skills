# DTCG Identity And Orchestration Appendix

Date: 2026-08-27

Status: Approved for implementation

Parent and backlink: [DTCG Adaptive Source Frontier Design](2026-08-27-dtcg-adaptive-source-frontier-design.md), Identity And Orchestration.

Load trigger: Use this appendix while implementing or reviewing `assets/subagent-task-contract.json`, `references/subagent-orchestration.md`, `assets/originality-analysis-contract.json`, `references/multimodal-originality.md`, runtime delegation, source identity, claim boundaries, or their tests. The future package files own runtime procedure. This appendix owns the approved design boundary.

## Runtime Subagent Orchestration

The lead freezes a task dependency graph before work begins. Delegation is eligible only when the environment supports it and at least two ready tasks are independent, bounded, and have disjoint write ownership. When eligible, the run must delegate and use available parallel capacity. When delegation is unavailable, the same roles run sequentially with identical task and result records; unavailability alone is not failure.

The lead owns the run contract, graph, integration, final claims, current-byte readback, and final strong-vision adjudication. One writer owns each mutable deliverable. Workers may independently research source domains, inspect modality slices, search comparison-corpus shards, generate experiment candidates, or run read-only checks. A worker may make visual judgments only after passing the same strong-vision probe as the lead. A worker's `PASS` is a claim to verify, not proof.

Every task packet records `task_id`, role, objective, exact input paths and hashes, dependencies, source boundary, allowed and forbidden actions, tools, output schema, required evidence, completion rule, budget, and status. Every result records claims, primary sources, located evidence, counterevidence, uncertainty, conflicts, output paths and hashes, and `PASS` or `BLOCKED`. Reviewer briefs must not contain a favored conclusion. At least one independent task must seek counterevidence. The lead preserves disagreements, removes duplicate work, rereads primary sources, and resolves conflicts against current bytes.

## Claim Model

The evidence manifest must keep these claims separate:

| Claim                    | Required meaning and proof                                                                                           |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| `source_specificity`     | Located observations and relationships are present in the actual input.                                              |
| `source_distinctiveness` | Named features differ from a stated local context or matched comparison set.                                         |
| `source_originality`     | Novelty and contextual fit both pass within a named corpus, date, feature space, and task.                           |
| `output_originality`     | Tokens and proof derive from source relationships instead of a reusable shell or surface substitution.               |
| `output_identifiability` | Reviewers can match output to its source among matched distractors under declared transformations.                   |
| `corpus_uniqueness`      | No collision or near neighbor crosses declared thresholds in a frozen corpus and representation set.                 |
| `memorability`           | Corrected recognition evidence passes; loudness or salience alone cannot establish it.                               |
| `authorship_provenance`  | External provenance records support authorship; style cannot prove it.                                               |
| `bounded_one_of_a_kind`  | Originality, identifiability, and multi-representation corpus uniqueness all pass inside the same declared boundary. |
| `globally_unique`        | Always false because the searchable universe is neither complete nor stable.                                         |

A result can be unique but unidentifiable, identifiable but unoriginal, memorable but generic, or original but unfit. The skill must report each state without upgrading it to another claim.

## Multimodal Source Identity

The source identity graph contains located nodes and typed edges. Each node records modality, observation, location or time range, role, confidence, expected invariance, allowed variation, and comparison context. Edges record spatial, temporal, semantic, causal, hierarchical, rhythmic, material, interaction, crossmodal-congruence, purposeful-tension, absence, or silence relationships.

Applicable observations include visual hierarchy, topology, composition, type, palette relations, material, light, crop, and negative space; audio timbre, pitch, rhythm, dynamics, texture, and silence; motion timing, cadence, trajectory, editing, and continuity; text lexicon, syntax, rhetoric, semantics, and voice; touch affordance, target, force, material, contact geometry, and feedback; code, data, and interaction topology, states, distributions, constraints, and behavior; and crossmodal binding, counterpoint, timing, semantic agreement, or controlled dissonance. Missing applicable modalities are a failure, not silent omission.

The graph is not accepted as a flat feature list. Each proposed identity-bearing relation must survive at least one relevant negative control: remove a salient element, replace it with a category average, strip color, type, copy, ornament, or polish, flatten hierarchy or rhythm, shuffle crossmodal timing, transplant a near-neighbor layout skeleton, mask detail, or preserve surface style while changing structure. A relation passes only when its ablation produces measurable recognition or structural loss and the same relation cannot be derived as well from matched distractors.

## Identifiability And Uniqueness Tests

Identifiability uses n-way source matching with same-category, comparable-finish distractors plus an open-set `none of the above` option. Record top-1 and top-k retrieval, confusion matrix, hit rate, false-alarm rate, within-source consistency, between-source separation, and counterfactual identity loss. Test applicable transformations such as viewport, theme, state, input method, crop, scale, grayscale, reduced detail, temporal segment, and noise or degradation. A test is invalid when distractors make the answer obvious through category, finish, or file metadata.

Corpus uniqueness compares exact bytes, normalized token graphs, low-level appearance, near-duplicate perceptual features, mid-level layout, object and pose relations, grayscale, edges, topology, semantic and content grammar, temporal, audio, tactile, and crossmodal relation signatures as applicable. Save nearest neighbors and thresholds for each representation, explain disagreements, and freeze corpus membership and date. No single similarity metric, embedding, hash, or aggregate score can prove uniqueness.

Memorability remains a separate optional experiment. It requires held-out recognition with hit rate corrected by false alarms. Authorship remains a provenance question. A one-of-a-kind claim must state the exact corpus, date, representations, thresholds, transformations, distractor policy, and failed global claim.

## Failure Ownership

Return `E_DELEGATION` for skipped eligible delegation or an invalid worker contract, `E_HANDOFF` for stale or missing hashes or schemas, `E_CONFLICT` for unresolved worker disagreement, `E_VISION` for an unqualified visual reviewer, `E_SOURCE_IDENTITY` for an incomplete or unfalsified graph, `E_IDENTIFIABILITY` for failed matching or invariance, and `E_CLAIM` for conflated or unbounded claims.

## Research Owner

The [research-basis appendix](2026-08-27-dtcg-research-basis.md) owns the dated originality, recognition, multimodal identity, visual judgment, and orchestration sources that justify these requirements.
