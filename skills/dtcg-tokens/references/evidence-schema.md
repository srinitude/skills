# Evidence file schema

Start from `assets/evidence-template.json`. The evidence file is the canonical record for source accounting, decisions, review, claims, and limits. The standalone HTML embeds it without changing its meaning.

## Source and intent

- `report_version` and `title` identify the record.
- `sources` lists every input with stable identifier, kind, locator, SHA-256, and visual-inspection state.
- Every visual source records `whole-frame`, `detail`, and `comparative` native-vision passes.
- `observations` stores atomic facts with source, locator, region, basis, confidence, and counterevidence when present.
- `input_manifest` enumerates format and access facets from `assets/multimodal-input-catalog.json`.
- `intent_manifest` records request intent and each source's role, authority, allowed influence, target scope, conflicts, and disposition.

## Token decisions and full-universe narrowing

- `identity_thesis` names audience, context, intended feeling, and source-specific visual idea.
- `signature_decisions` contains at least five source-linked decisions across at least three applicable axes.
- `possibility_ledger` starts from every leaf in `assets/token-possibility-catalog.json` and assigns exactly one disposition.
- `context_requirements` maps source and intent requirements to retained possibilities and token paths.
- `permutation_space` declares applicable type, role, state, mode, component, context, and value branches plus exclusions and equivalence classes.
- `experimental_output` lists every token in the required top-level experimental partition. It contains at least two paths using at least two strategies from `assets/exploration-strategy-catalog.json`. Each entry exactly repeats the stable experiment identifier, exploration strategy, hypothesis, intended context, status, visible-specimen requirement, and invariant disposition.
- `temporal_context` stores exactly one fresh local clock anchor, the pinned conformance target, the current specification check, and every current primary source.

## Quality checks

`quality_checks` includes exactly these names:

- `audience_relation`
- `visual_identity`
- `hierarchy`
- `cohesion`
- `non_genericity`
- `render_integrity`
- `possibility_accounting`
- `context_coverage`
- `coverage_integrity`
- `temporal_currency`
- `taste`
- `originality`
- `corpus_uniqueness`
- `non_ai_slop`
- `perceptual_motor_invariants`
- `objective_visual_defects`
- `experimental_output`

Preliminary evidence may use `pending_visual_review`. Final evidence requires every check to pass with concrete evidence.

## Artifact review

`artifact_review.vision_executor` records an active or delegated strong-native-vision executor. If that capability is absent and delegation is unavailable, the work is blocked before judgment.

`viewports` contains final wide and narrow reviews. Each record names width, height, pass status, whole-frame and detail regions, and located findings.

`defect_review` uses `assets/visual-defect-catalog.json`. Final evidence lists every marker identifier exactly once in `reviewed_ids`, records findings with marker and region, and has zero unresolved vetoes or major defects.

`invariant_review` uses `assets/perceptual-motor-invariant-catalog.json`. Final evidence lists every invariant exactly once. Final statuses are:

- `pass`: the claimed use passed token feasibility and rendered review;
- `not_applicable`: the context cannot produce this condition and the evidence states why;
- `not_used_experimental`: the token branch remains available for exploration but no published use claims the invariant.

`judgment_reviews` uses `assets/judgment-review-catalog.json`. It contains separate passing tracks for taste, originality, corpus uniqueness, and non-AI-slop. Each track lists every obligation, located evidence, and the strongest counterevidence.

`experimental_review` lists every experimental token path exactly once and confirms that the final artifact contains a visible specimen and explicit use boundary. A raw embedded JSON path alone does not satisfy the visible-specimen requirement.

`final_readback` records pass status, the reviewed surface hash, exact artifact locator, and confirmation that review happened after final assembly.

## Comparison and claims

`comparison` names a nonempty declared corpus, item count, frozen methods and thresholds, nearest neighbors, results, and limits.

Final `claims` may set these to true only after their matching review passes:

- `dtcg_conformant`
- `non_slop`
- `original_within_scope`
- `taste_pass`
- `non_ai_slop`
- `unique_within_declared_corpus`
- `invariants_satisfied`

`globally_unique` remains false. `limits` includes `Global uniqueness cannot be proved without an exhaustive comparison corpus.`

## Evidence integrity

SHA-256 values use lowercase 64-character hexadecimal strings from exact bytes. A live source requires a saved, hashed capture. URLs alone are not stable source evidence.

Every decision and pass traces source to observation to decision to token to rendered region. A machine check proves only its named property. A visual statement without a viewport, state, region, and observed condition cannot support a pass.
