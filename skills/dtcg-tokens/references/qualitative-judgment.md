# Qualitative judgment

Use this reference for source interpretation, taste, originality, corpus comparison, non-AI-slop review, proof authorship, and any vision-led decision. Standardize the evidence record and review discipline. Do not standardize taste, style, emotional response, or creative direction.

## Fixed evidence, flexible interpretation

Every judgment records the source and artifact context, actual viewport and state, located region, visible evidence, strongest counterevidence, one credible alternative, competing readings, uncertainty, confidence, rationale, verdict, and limits. These fields are fixed so another reviewer can inspect the reasoning.

For token and proof work, also record one token-local quality gate. Check source fidelity, semantic role, accessible range, spacing relationships, responsive behavior, familiarity, standards, uniqueness, and rendered proof separately. Every applicable gate must pass. A numeric average, regular scale, unusual value, or polished crop cannot cancel another failed gate or prove whole-product quality.

Spacing review distinguishes related-item gaps, component insets, group separation, section rhythm, shell separation, and wide-aperture spacing. Require rendered grouping evidence at relevant widths and content ranges. Reject uniform spacing that erases hierarchy, arbitrary one-off values without a semantic owner, and empty space that has no reading, task, or identity role.

## Continuous canvas cleanliness

For token-proof or installed-token work on a visual canvas, cleanliness is a continuous noncompensating gate, not a final tidying pass. Capture and inspect a whole-canvas baseline before the first write, keep the active work area readable during each batch, and inspect both the whole canvas and readable detail after every create, move, relabel, restyle, reparent, detach, or authorized delete. Recheck after any lower-owner change. If the same executor cannot directly see the current pixels, the affected cleanliness claim is `BLOCKED`.

Use human eyes to judge order, grouping, crowding, alignment, edge conditions, scale, overlap, clipping, visual noise, and whether accepted work remains distinguishable from experiments. Use the human brain to judge semantic zones, provenance, status, comparison logic, reading sequence, next action, and whether placement creates a false relationship or false pass. Use human touch to judge selection safety, target separation, reachable controls, view occlusion, input-path effort, accidental-edit risk, and whether a person can manipulate the intended item without disturbing a neighbor.

Reject bad design such as false hierarchy, hidden state, conflicting accepted owners, inaccessible controls, and decorative order that contradicts meaning. Reject bad output such as unnamed scratch nodes, stale leftovers, unexplained duplicates, clipped evidence, overlapping boards, off-canvas required content, mixed comparison conditions, and an unviewed tidy claim. Reject bad practice such as cleanup only at the end, interleaving historical evidence with canonical work, deleting proof to make the canvas look finished, using auto-layout or bulk movement without readback, or accepting a structurally neat canvas that fails human eye, brain, or touch judgment.

A clean canvas need not be empty, sparse, symmetrical, or stylistically uniform. Preserve necessary evidence in explicit accepted, exploration, rejected, historical, or quarantine zones with stable names, readable separation, current status, and followable lineage. Record the affected regions and node or item locators, before and after views, eye, brain, and touch findings, bad-work dispositions, retained evidence, authorized cleanup, invalidated dependents, and current verdict.

Familiarity, standards, and uniqueness are simultaneous requirements. Familiar values may remain distinctive through product-specific relationships. Novel values fail when they damage access or category recognition. Familiar values fail when they collapse the token system into an interchangeable default.

The reviewer may choose any expressive direction, evidence form, visual grammar, and qualitative lens supported by the source and task. No house style, preferred level of restraint, trend, symmetry rule, aesthetic ideology, or numeric score determines taste. A strict evidence protocol must not collapse multiple defensible readings into fake objectivity.

Start from the full lens universe below, then mark each lens `applicable`, `not_applicable` with a reason, or `emergent` with a name and reason. Select depth by impact. A lens that can materially change tokens, proof structure, or a claim requires located evidence and a countercheck.

## Qualitative lens universe

- Purpose, audience, setting, use frequency, stakes, and consequence fit.
- Emotional register, mood, warmth, distance, urgency, calm, intimacy, authority, play, seriousness, and confidence.
- Narrative, sequence, reveal, pacing, pause, anticipation, closure, and sense of progression.
- Composition, balance, imbalance, tension, release, visual weight, energy, rhythm, density, emptiness, scale, and spatial character.
- Attention, salience, gaze path, reading order, hierarchy, interruption, and recovery.
- Typography voice, cadence, measure, optical weight, contrast, texture, and relation to language and content.
- Color, light, darkness, atmosphere, material, surface, transparency, depth, temperature, and relational behavior.
- Shape, edge, line, texture, image treatment, icon character, crop, overlap, and motif meaning.
- Motion character, duration, tempo, acceleration, continuity, transition logic, stillness, and reduced-motion equivalence.
- Interaction feel, affordance, feedback, directness, friction, tactility, control, forgiveness, and trust.
- Sound, haptic, spatial, physical, and cross-sensory agreement when the inputs or intended product support them.
- Cultural context, connotation, symbolism, language, place, time, references, and risk of appropriation or misreading.
- Familiarity, convention, surprise, ambiguity, mystery, legibility, and the cost and benefit of departing from expectations.
- Credibility, authenticity, care, finish, precision, craft, perceived effort, and consistency between large and small decisions.
- Memorability, recognition, identity strength, source specificity, and whether novelty serves the idea.
- Accessibility as lived experience, including effort, comfort, cognitive load, fatigue, comprehension, and equivalent access beyond minimum conformance.
- Continuity across viewport, mode, state, input method, data condition, time, and repeated use.
- Originality, genericity, filler, repetition, unsupported ornament, template dependence, false rationale, and other non-slop traits.
- Any source-specific quality that the listed lenses do not name.

The list is a starting universe, not a scoring sheet. A reviewer may combine related lenses when the relation matters, split a lens when different readings conflict, or introduce a new lens through the open-finding rule.

## Open findings

Do not force a material qualitative observation into the nearest catalog entry. Create an `emergent` finding with a stable local ID, plain-language lens name, source or artifact locator, visible condition, why it matters, affected decisions or claims, counterevidence, competing readings, and proposed review method. If the condition is harmful, also record it through the unknown marker in `assets/visual-defect-catalog.json` without treating the defect record as a substitute for the qualitative record. Use `mise run token-packet -- <args>` for this routed resource.

Current catalogs are floors, not ceilings. New cultural readings, visual conventions, interaction forms, sensory combinations, or slop patterns may appear after the package date. Record them rather than ignoring them or pretending the existing taxonomy was exhaustive.

## Multiple defensible readings

When two readings fit the visible evidence, record both before choosing. Name the audience, context, or value that makes each reading plausible. Prefer the reading that better matches direct source evidence and the frozen task. If the choice materially changes the token system and evidence cannot decide it, keep the judgment `partial` or `blocked` and ask one concise question. Disagreement is not a defect; concealed uncertainty is.

## Judgment record

Each qualitative finding contains `track`, `lens`, `applicability`, `claim`, `viewport`, `state`, `region`, `source_relation`, `visible_evidence`, `counterevidence`, `credible_alternative`, `competing_readings`, `uncertainty`, `confidence`, `verdict`, `rationale`, and `limits`. Confidence may be verbal and must not imply mathematical precision. A track verdict follows its evidence and veto rules, never an average.

A qualitative PASS requires every applicable or emergent lens to be accounted for at the depth justified by its impact, every high-impact claim to have visible evidence and a countercheck, competing readings to remain visible, and the final rationale to fit the stated audience and task. Use `BLOCKED` when direct visual access, source context, comparison evidence, or a material choice is unavailable. Use `partial` when the record supports a bounded judgment but not the full claim.
