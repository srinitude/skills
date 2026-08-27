# Multimodal inspection

## Source inventory

Assign every source an identifier before interpretation. Record media kind, original locator, SHA-256, byte size when available, page or duration when applicable, and whether native visual inspection is required.

| Input               | Required direct inspection                                                                                                        | Supporting extraction                                            |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Image or screenshot | View the full frame, then inspect important regions at readable scale.                                                            | OCR, dimensions, color sampling, metadata.                       |
| Video or animation  | View the opening, closing, scene changes, interaction states, and every segment that supports a token decision. Record timecodes. | Transcript, scene detection, frame extraction, audio transcript. |
| PDF or slide deck   | Inspect every page with visual design evidence. Record page and region.                                                           | Text extraction, document structure, embedded asset inventory.   |
| Live interface      | Inspect the rendered page and material states needed by the request. Record route, state, viewport, and region.                   | Document structure, computed values, accessibility tree.         |
| Audio               | Listen to relevant passages and record timecodes.                                                                                 | Transcript, speaker labels, amplitude or tempo analysis.         |
| Text, data, or code | Read the content and record section, field, selector, or line location.                                                           | Search, parsing, schema checks.                                  |

## Vision gate

For each visual source, the active executor must use its native visual reasoning as the primary judgment method and complete three distinct passes. Record `whole-frame`, `detail`, and `comparative` in the source's `vision_passes` array. State at least three pixel-checkable facts per source, with `source_id`, `locator`, `region`, `fact`, and `confidence`. Use `high` for plainly visible evidence, `moderate` for a likely reading with some ambiguity, and `low` for a tentative observation that cannot support a passing gate by itself.

The whole-frame pass reads the full frame or state for identity, audience cues, focal hierarchy, density, composition, and intended feeling. The detail pass zooms into type, palette relations, spacing, edges, radii, strokes, material, image crop, icons, controls, and motion cues. Load `assets/visual-defect-catalog.json` and inspect every applicable marker. The comparative pass places sources, states, pages, or timecodes against each other to find repeated primitives, meaningful variation, contradictions, bad output, and details that would be lost in isolated viewing.

For a token set and its proof artifact, also load `assets/perceptual-motor-invariant-catalog.json`. Check token feasibility and actual rendered use for every applicable visual-perception, cognitive-comprehension, motor-touch, and cross-context invariant. A token value may remain experimental or unused. An invariant gates only a claimed use, never the existence of an exploratory token branch.

Load `assets/judgment-review-catalog.json` for the separate taste, originality, corpus-uniqueness, and non-AI-slop tracks. Do not merge these judgments with objective defect findings or with each other.

Describe relations, not isolated color names. Useful observations cover hierarchy, type contrast, spacing rhythm, shape language, crop behavior, material treatment, focal placement, density, state change, and repeated motifs. Record counterevidence when a source conflicts with the leading identity thesis.

OCR is evidence about visible words, not evidence that the surrounding composition was inspected. A color sampler reports a pixel value, not its role. File names and metadata report source context, not visual content. None of these can set `vision_inspected` to true.

## Coverage

Inspect every supplied still image in all three passes. For a multi-page or time-based source, inspect every design-bearing page, scene change, state change, and segment used by a decision. If full coverage is impractical, record the sampling rule, inspected locations, omitted range, and reason; the proof report must describe the result as partial and cannot claim non-slop for the omitted scope.

For a mixed file, apply each relevant method. A slide with text and imagery needs both content reading and native visual inspection. A video with motion and narration needs visual inspection plus listening or transcript review when the narration changes the meaning.

Any newly observed harmful condition not covered by the catalogs uses the unknown marker or invariant. Record the condition, region, state, repeatability, affected human outcome, token relations, and proposed catalog addition. A preference without repeatable perception, comprehension, access, or task impact stays in the taste track.

## Evidence boundary

Label each retained statement as observed, inferred, or assumed. Only observed facts and clearly bounded inferences may support a passing quality gate. Native visual observations must drive the identity thesis, signature decisions, category selection, final HTML judgment, and `render_integrity` defect sweep. Never infer audience, brand values, or functional semantics solely from an aesthetic resemblance.
