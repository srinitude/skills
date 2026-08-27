# Visual review contract

Read `references/qualitative-judgment.md` before any taste, originality, uniqueness, non-AI-slop, or open-ended visual judgment. It standardizes evidence fields while preserving subjective interpretation, competing readings, emergent lenses, and source-specific expression.

This review has five independent tracks. No average or blended score exists. A pass in one track cannot offset a failure in another.

## 1. Objective defects

Load `assets/visual-defect-catalog.json`. Account for every marker exactly once. Use `pass`, `fail`, `not_applicable`, or `unresolved` at working time. A final pass requires every applicable marker checked, zero unresolved vetoes, and zero unresolved major defects.

The catalog covers render integrity, geometry, typography, contrast, interaction, accessibility, responsive behavior, information architecture, design coherence, source specificity, proof integrity, technical integrity, content integrity, corpus similarity, state coverage, production readiness, and time validity. Its unknown-defect marker keeps the review open to failure modes that were not known when the catalog was written.

Machine measurements prove only the property measured. A width calculation can prove overflow, not good composition. A contrast calculation can prove a ratio, not readable hierarchy. Strong native vision performs the whole-frame and detail judgments after machine checks.

For typography, also load `references/google-font-selection.md`. Confirm the catalog rank and cutoff from the saved same-date capture, then compare at least three eligible families in final-content specimens. Inspect computed family resolution, smallest and largest claimed text, numerals, punctuation, mixed case, required scripts, every selected weight and style, line breaks, fallback, collision, hierarchy, voice, and source relation. The final proof must work with network access blocked, and each embedded WOFF2 SHA-256 must match evidence.

## 2. Perceptual and motor invariants

Load `assets/perceptual-motor-invariant-catalog.json`. Start with all invariants, then narrow each to `pass`, `not_applicable`, or `not_used_experimental` with a reason.

Each applicable invariant needs both:

- token feasibility, which proves that resolved values and relations can express the required outcome;
- rendered evidence, which proves the actual use works in its viewport, state, mode, and input method.

The invariants protect minimum human outcomes: visibility, figure-ground separation, grouping, hierarchy, differentiation, stable mappings, unambiguous state, failure priority, readable labels, visible focus, target size, target spacing, pointer cancellation, alternatives to dragging and complex gestures, reflow, text resize, reduced motion, and cross-mode semantic stability.

They do not prescribe a palette, typeface, grid, composition, symmetry, visual style, or familiar interaction. A token may be unusual, speculative, or not yet used. The invariant gates only a claimed rendered use.

### Creative exception protocol

When a new direction departs from a familiar implementation:

1. State the human outcome protected by the invariant.
2. Name the experiment and affected token paths.
3. Provide an equally effective access path when the experimental form cannot carry the outcome alone.
4. Test the actual render across affected widths, states, modes, and input methods.
5. Record the gain, cost, counterevidence, and pass boundary.
6. Keep unresolved experimental branches in the token and evidence records as partial or unused. Do not delete them merely to force conformity.

## 3. Taste

Load the `taste` obligations in `assets/judgment-review-catalog.json`. Taste is not objectively provable. It becomes auditable through reasoned visual judgment.

Review fitness for audience and task, reading order, rhythm, typographic voice, color relations, earned expression, restraint, detail resolution, memorability, and coherence across states. For every pass, cite visible regions, compare a credible alternative, and record the strongest counterexample.

Personal dislike, fashion, novelty, minimalism, maximalism, symmetry, and asymmetry do not fail taste by themselves. A taste failure names the relation that is unfit, incoherent, unresolved, or unsupported and shows it in the artifact.

## 4. Originality and corpus-bounded uniqueness

Load the `originality` and `corpus_uniqueness` obligations in `assets/judgment-review-catalog.json`.

Originality requires source-derived signature decisions, cross-axis interaction, non-default relations, claim-to-implementation alignment, and a complete lineage from source to observation to decision to token to rendered region. Apply noun substitution and transplant tests. A shell that accepts unrelated nouns and content without structural change fails.

Uniqueness is limited to a named comparison corpus. Freeze the corpus and thresholds before comparison. Compare:

- exact token, evidence, and artifact bytes;
- normalized token path-role-reference-value graphs;
- semantic role graphs with primitive values removed;
- layout skeletons with color, font, copy, and decoration removed;
- full-color, grayscale, edge, hierarchy, and region-level appearance;
- headline, section, and specimen grammar;
- nearest neighbors in a blind side-by-side review.

Color-only distance cannot prove distinctiveness. Global uniqueness remains unproved.

## 5. Non-AI-slop output traits

Load the `non_ai_slop` obligations in `assets/judgment-review-catalog.json`. Review the artifact, not presumed authorship.

Check reasoning-to-implementation alignment, source-clause coverage, template dependence, filler, unsupported ornament, microdetail consistency, purposeless repetition, truthful examples, compound-constraint accuracy, and provenance boundaries. Appearance or a detector score never proves who or what made an artifact. Authorship claims require provenance.

## Required passes

Review every visual source and the actual proof artifact at:

- whole-frame scale for identity, hierarchy, density, composition, and first read;
- detail scale for type, edges, crops, controls, data, tokens, states, and defects;
- comparative scale against sources, states, modes, and the declared corpus;
- wide and narrow viewports;
- every applicable interaction, data, error, motion, reduced-motion, and mode state.

Each finding records viewport, state, region, marker or obligation, observed condition, evidence, countercheck, status, and repair if needed.

Before visual judgment, confirm that `scripts/lib/artifact_contract.py` found exact equality between the coverage plan and decoded `data-token-path`, `data-stress-cell`, and `data-permutation-cell` attributes on renderable, non-hidden elements. Then inspect the corresponding visible regions. Attribute equality proves structural presence and uniqueness only; it cannot prove that CSS left the region visible or that a specimen is meaningful, legible, or well designed.

## Current basis

The numeric accessibility floors are checked against current official W3C material on the run date. The 2026-08-27 baseline uses:

- WCAG 2.2: <https://www.w3.org/TR/WCAG22/>
- Target Size Minimum: <https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html>
- Contrast Minimum: <https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html>
- Focus Visible: <https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html>
- Focus Not Obscured Minimum: <https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum>
- Resize Text: <https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html>
- Three Flashes or Below Threshold: <https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold>
- Cognitive and learning accessibility guidance: <https://www.w3.org/TR/coga-usable/>

The W3C cognitive guidance is supplemental and is not presented as WCAG conformance. Recheck every drift-prone source before a current claim.

Research basis for output-trait and similarity checks:

- Design Theater: <https://arxiv.org/abs/2607.22928>
- IDEA-Bench: <https://arxiv.org/abs/2412.11767>
- GenAI-Bench: <https://openaccess.thecvf.com/content/CVPR2024W/EvGenFM/html/Li_Evaluating_and_Improving_Compositional_Text-to-Visual_Generation_CVPRW_2024_paper.html>
- NIST synthetic-content transparency report: <https://doi.org/10.6028/NIST.AI.100-4>
