# DTCG Exploration Corpus Appendix

Date: 2026-08-27

Status: Approved for implementation

Parent and backlink: [DTCG Adaptive Source Frontier Design](2026-08-27-dtcg-adaptive-source-frontier-design.md), Exploration Corpus.

Load trigger: Use this appendix while implementing or reviewing `assets/exploration-corpus/`, `references/exploration-synthesis.md`, Step 08, `E_CORPUS`, or their tests. The future package files own runtime procedure. This appendix owns the approved corpus, synthesis, and coverage design.

## Outcome

Exploration must start from a typed, versioned corpus of usable creative material. The corpus must produce source-derived, testable token hypotheses through a fixed synthesis process. It must not reduce creativity to an undefined search for interesting examples, generic mood words, prebuilt styles, or random combinations.

## Object Definitions

| Object     | Definition                                                                                                    | Not accepted                                                 |
| ---------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Primitive  | Lowest-level controllable visual, spatial, temporal, interaction, sensory, material, state, or data property. | A finished style or named trend.                             |
| Operator   | A transformation that changes one or more primitives or relationships.                                        | A vague instruction such as make it better or more creative. |
| Mechanism  | A cause-and-effect pattern that predicts an observable result.                                                | A metaphor with no structural transfer or falsifier.         |
| Concept    | A reusable structural arrangement of primitives, operators, and mechanisms for a stated purpose.              | A screenshot, template, or surface look to copy.             |
| Theme      | A source-backed semantic or experiential proposition with observable implications.                            | A generic mood adjective without evidence or consequences.   |
| Tension    | Two forces that the candidate must hold, separate, sequence, or reconcile.                                    | A decorative pair of opposites with no decision effect.      |
| Constraint | A hard, soft, hidden, inverted, or experimental boundary on the candidate.                                    | An unstated convention treated as physics.                   |
| Question   | A bounded prompt whose answer could change a token or proof decision.                                         | An open-ended request for inspiration.                       |
| Idea       | A run-specific, falsifiable hypothesis assembled from source evidence and corpus entries.                     | A static corpus item or untestable suggestion.               |

## Package Shape

The corpus is a versioned folder, not one unstructured list.

| Planned file                                       | Canonical content                                                                                                           |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `assets/exploration-corpus/manifest.json`          | Version, schema, shard hashes, counts, update date, source classes, and compatibility.                                      |
| `assets/exploration-corpus/primitives.json`        | Atomic visual, spatial, type, color, material, motion, interaction, haptic, audio, state, data, and accessibility controls. |
| `assets/exploration-corpus/operators.json`         | Combination, inversion, substitution, scaling, sequencing, mapping, abstraction, perturbation, and topology operations.     |
| `assets/exploration-corpus/mechanisms.json`        | Relational patterns from design, science, art, engineering, nature, language, movement, music, and other domains.           |
| `assets/exploration-corpus/concepts.json`          | Structural patterns with prerequisites, effects, risks, and tests.                                                          |
| `assets/exploration-corpus/themes.json`            | Proposition and tension grammars, evidence requirements, implications, anti-signals, and clichés to avoid.                  |
| `assets/exploration-corpus/constraints.json`       | Human invariants, technology limits, hidden assumptions, inversion candidates, and experimental bounds.                     |
| `assets/exploration-corpus/questions.json`         | Typed questions for source analysis, cross-domain transfer, counterfactuals, physical interaction, and proof.               |
| `assets/exploration-corpus/technology.json`        | Dated capability records from the technology watch, with maturity and fallback requirements.                                |
| `assets/exploration-corpus/negative-patterns.json` | Generic shells, repeated generated-design patterns, invalid transfers, failed themes, and rejected visual precedents.       |

The manifest must fail if a shard is missing, stale, duplicated, unreferenced, or has a hash mismatch. The future runtime reference explains how to load only the shards needed for a run while the manifest proves full catalog awareness.

## Entry Contract

Every static corpus entry records:

- stable ID, class, name, plain definition, version, and date
- source class, source domain, source citation, and confidence
- structural relations and predicted effect
- compatible screen axes, token types, modalities, intents, and tasks
- prerequisites, incompatibilities, invariants, risks, and common misuses
- one or more operators that can act on it
- evidence that would support or falsify its use
- allowed maturity lane and required fallback
- similarity keys and known near-duplicates

An entry is rejected if it is only a style label, has no observable consequence, names a technology without maturity, repeats another entry, contains a finished visual recipe, or cannot participate in a falsifiable idea.

## Primitive Families

The core primitive corpus covers:

- geometry, topology, proportion, position, alignment, density, rhythm, hierarchy, grouping, overlap, occlusion, crop, and negative space
- type family traits, variable axes, scale, measure, spacing, script, language, writing mode, emphasis, and text behavior
- hue, lightness, chroma, alpha, contrast, gamut, dynamic range, gradients, blends, filters, texture, light, and material cues
- static, responsive, stateful, temporal, spatial, three-dimensional, and crossmodal relationships
- duration, rate, delay, easing, path, inertia, interruption, continuity, transition, morph, oscillation, and reduced-motion equivalents
- pointer, touch, stylus, keyboard, switch, voice, gaze, hand, body, controller, sensor, and assistive input properties
- activation, selection, steering, drawing, manipulation, navigation, editing, comparison, recovery, collaboration, and exploration actions
- visual, auditory, vibrotactile, force, friction, stiffness, shape, thermal, electrical, ultrasound, and pseudo-haptic feedback
- default, focus, active, selected, disabled, loading, progress, error, empty, offline, permission, conflict, undo, preview, and committed states
- nominal, ordinal, quantitative, relational, temporal, spatial, probabilistic, uncertain, and provenance-bearing data

The [screen possibility-space appendix](2026-08-27-dtcg-screen-possibility-space-design.md) owns the full axis definitions. Corpus primitives reference those IDs instead of copying their procedure.

## Operator Families

The operator corpus must include these stable families:

| Family         | Operations                                                                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Combine        | Pair, layer, interleave, braid, fuse, alternate, synchronize, or counterpoint.                                                        |
| Separate       | Split, isolate, stagger, gate, reveal, defer, phase, or create redundancy.                                                            |
| Transform      | Scale, stretch, compress, rotate, translate, warp, morph, quantize, interpolate, or remap.                                            |
| Reframe        | Change objective, agent, granularity, formalism, time scale, point of view, or medium.                                                |
| Invert         | Reverse hierarchy, direction, figure and ground, control and response, input and output, default and exception, or cause and display. |
| Vary           | Sweep, block, randomize, perturb, mutate, exaggerate, attenuate, or test extremes.                                                    |
| Abstract       | Strip surface traits, preserve relations, generalize, specialize, encode, or symbolize.                                               |
| Transfer       | Map a verified mechanism from a distant domain while forbidding surface imitation.                                                    |
| Counterfactual | Remove, replace, shuffle, flatten, transplant, mask, or preserve style while changing structure.                                      |
| Temporalize    | Sequence, accumulate, decay, loop, branch, pause, interrupt, replay, or make state history visible.                                   |

Each operator must name input types, output types, invalid combinations, predicted effect, and at least one falsifier.

## Theme Grammar

A theme is not a mood word. Each theme record contains:

- proposition: the idea the output should make perceptible
- evidence: exact source observations and relationships that support it
- antithesis: a plausible opposing proposition
- tension: what must be reconciled, separated, or deliberately left unresolved
- entailments: expected effects on hierarchy, type, color, space, motion, interaction, and proof
- anti-signals: choices that contradict the proposition
- clichés: familiar motifs or surface treatments that cannot stand in for the theme
- counterfactual: what visual or behavioral change should weaken the theme

Themes are created or activated only after source inspection. The static corpus supplies grammars and question types, not brand personalities or ready-made aesthetics.

## Run-Local Corpus

Every run builds a source-specific extension over the static corpus. It contains:

- identity-graph nodes and relationships from the actual input
- user intent, intended audience, tasks, contexts, and forbidden outcomes
- applicable screen-axis records and physical constraints
- transferred mechanisms from current and distant research
- active themes, antitheses, tensions, and counterfactuals
- recent technology candidates with maturity classes
- rejected precedents and source-specific anti-patterns
- unanswered questions, uncertainty, and blocked evidence

Every run-local entry retains its lineage to the input location, research record, or explicit user instruction. No unlocated adjective may become a source fact.

## Deterministic Synthesis

Exploration uses a recorded seed derived from the input hash, intent hash, corpus version, and run ID. The same seed and inputs reproduce the same sampling order. A new run ID permits a different exploration while keeping the result auditable.

The lead builds four candidate lanes before evaluation:

| Lane             | Required construction                                                               | Minimum candidates |
| ---------------- | ----------------------------------------------------------------------------------- | ------------------ |
| Combinational    | Two source relations plus primitives and a mechanism from a distant domain.         | 3                  |
| Exploratory      | Search inside a declared rule set by varying primitives or parameters.              | 3                  |
| Transformational | Change a soft or hidden constraint, objective, medium, agent, or interaction model. | 3                  |
| Antithetical     | Use inversion, contradiction, or a counter-theme against the leading thesis.        | 3                  |

Each candidate must contain at least two source-specific relationships, one primitive, one operator, one mechanism, one theme or tension, one constraint, one question, one predicted effect, one falsifier, and exact candidate token paths. Include a physical interaction primitive when applicable. Include at least one current technology candidate in the twelve-candidate set, but do not retain it merely to fill the quota.

The candidate count may exceed twelve to cover applicable modalities or underrepresented corpus cells. It may not fall below twelve. The lead deduplicates candidates by source relations, operator, mechanism, screen tuple, predicted effect, and token paths. Cosmetic differences do not create a new candidate.

## Generation And Evaluation Separation

Generation records all twelve candidates before taste filtering. It may reject only a physically impossible tuple, invalid contract, duplicate, forbidden outcome, or missing source relation during this phase. It cannot reject a candidate for unfamiliarity, aesthetic risk, or low initial confidence.

Evaluation then proceeds in order:

1. Contract and source-lineage validation.
2. DTCG, physical, accessibility, safety, privacy, and capability vetoes.
3. Baseline and controlled experiment rendering.
4. Counterfactual and ablation tests.
5. Strong-vision comparison with located evidence and counterevidence.
6. Originality, identifiability, corpus uniqueness, source fit, and non-slop review as separate tracks.
7. Quality-diversity retention and exact token propagation.

The final set still retains at least three experimental tokens from three mechanism families, including one antithetical or inversion result. A retained result must trace back through the idea, corpus entries, source relations, experiment, proof specimen, and final review.

## Anti-Fixation Controls

- Do not begin from a proof-artifact template, named visual trend, or prior successful token set.
- Do not let the first theme become the only theme. Generate its antithesis before synthesis.
- Do not use palette swaps, font swaps, complexity, ornament, or novelty language as separate ideas.
- Do not let one domain, one operator, or one screen axis dominate more than half the candidates.
- Do not expose evaluator rankings to generators before all candidate records are frozen.
- Do not convert corpus frequency into quality. Common entries are not preferred by default.
- Do not hide rejected candidates. Their reasons are part of the evidence.

## Failure And Tests

Return `BLOCKED: E_CORPUS` for a missing shard, stale manifest hash, invalid entry, absent source-local extension, fewer than twelve candidates, missing lane, missing corpus class, duplicate presented as variety, theme without source evidence, idea without a falsifier, or final experimental token without complete lineage.

Focused tests must reject the instruction to find interesting ideas without typed entries, generic themes such as bold or futuristic without propositions, random combinations with no mechanism, candidates differing only by color or type, premature taste filtering, one-domain dominance, and a retained token whose idea record is absent. A positive fixture must reproduce its candidate order from the saved seed, cover all four lanes, preserve at least twelve distinct candidates, reject at least one tempting but invalid recent technology, and trace retained tokens to source, corpus, experiment, proof, and review.

## Research Owner

The [research-basis appendix](2026-08-27-dtcg-research-basis.md) owns the dated creativity, analogy, originality, experimentation, screen, and technology sources that justify the corpus and synthesis rules.
