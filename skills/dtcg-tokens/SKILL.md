---
name: dtcg-tokens
description: 'Use when any multimodal source must become source-specific DTCG tokens with a vision-reviewed standalone proof artifact.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.2.0'
---

# dtcg-tokens

Turn any inspectable multimodal input into source-specific DTCG 2025.10 JSON, evidence JSON, and a standalone HTML proof artifact. Start from the full token possibility universe, then narrow every possibility with evidence and reasons. Strong native vision owns source interpretation, design decisions, artifact authorship, and final visual judgment.

## Commands

| Command                               | Result                                                                                           |
| ------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `help`                                | Show commands, accepted inputs and intents, outputs, vision requirement, and claim limits.       |
| `generate <inputs>`                   | Create `<name>.tokens.json`, `<name>.evidence.json`, `<name>.proof.html`, and `<name>.run.json`. |
| `validate <tokens>`                   | Validate DTCG 2025.10 structure, values, names, references, type agreement, and cycles.          |
| `prove <tokens> <evidence> [sources]` | Author, assemble, inspect, and read back a source- and token-specific standalone proof artifact. |

If a request lacks the input or output needed for one command, state the missing item. Do not invent a source, audience, product fact, brand premise, comparison corpus, or proof claim.

## Execution

1. Read `references/deterministic-execution.md`. Write the frozen task packet and `<name>.run.json`. Acquire exactly one fresh local clock anchor with `scripts/current_anchor.py` before date-sensitive work.
2. Load `assets/multimodal-input-catalog.json`. Inventory every source by format and intent. Record identifier, locator, SHA-256, access method, sensory channels, source role, decision authority, allowed influence, target scope, and conflicts. Unknown and future formats use the catalog's extension path.
3. Before judgment, confirm that the active model has strong native vision and can directly inspect every supplied visual, zoom into regions, compare states and sources, and review the actual HTML at wide and narrow widths. If not, delegate every judgment-related task to a strong vision-capable model, including source inspection, thesis, token decisions, visual artifact authorship, taste, originality, uniqueness, invariant checks, defect review, and final readback. The primary executor may only inventory, hash, validate, and assemble returned records. If no strong vision-capable model or delegation path exists, set `E_VISION` and do not generate tokens or proof.
4. Read `references/multimodal-inspection.md`. For every visual source, perform whole-frame, detail, and comparative native-vision passes. Record source, locator, region, observed fact, confidence, and counterevidence. OCR, filenames, metadata, color samples, document trees, and statistics are supporting evidence only.
5. Separate observed, inferred, and assumed statements. Ask one concise question only when an unretrievable unknown would materially change the token system. Otherwise keep a narrow labeled assumption in evidence.
6. Write one identity thesis naming audience, use context, intended feeling, and a source-specific visual idea. Apply noun substitution. If unrelated nouns still fit, revise the thesis before authoring.
7. Load `assets/token-possibility-catalog.json`, `references/dtcg-2025.10.md`, and `references/category-taxonomy.md`. Expand every catalog leaf before exclusion. Add source- or intent-discovered extensions. Never start from a starter scale or a small preferred subset.
8. Load `assets/exploration-strategy-catalog.json`. Generate a candidate for every applicable strategy in its fixed order and record every candidate in the possibility ledger. Apply its ordered gates without a blended score. Retain at least two experimental tokens from at least two distinct strategies. Give every possibility exactly one disposition, reason, evidence locator, stage, and affected token paths when retained.
9. Build a context requirement for every source clause and high-confidence observation. Map each requirement to token paths or an explicit omission. Create the applicable permutation matrix across type, role, state, mode, component, context, value partition, viewport, motion, input method, and data condition.
10. Create at least five source-derived signature decisions across at least three applicable axes. Each names evidence, token paths, audience fit, and the generic default it replaces. Unsupported stock scales, filler roles, decorative values, and symmetry-driven completion are blocked.
11. Write `<name>.tokens.json` with `$schema` pointing to the bundled DTCG 2025.10 schema. Use valid standard types, aliases for semantic reuse, descriptions for non-obvious intent, and names without `$`, `{`, `}`, or `.`. Use namespaced `$extensions` for nonstandard concepts.
12. Run `python3 scripts/validate_dtcg.py <tokens>`. A nonzero exit blocks conformance. Repair the token source or architecture, never the report sentence.
13. Write `<name>.evidence.json` from `assets/evidence-template.json` and `references/evidence-schema.md`. Load all three review catalogs. Keep judgment claims pending until final visual review. Name the comparison corpus and keep `globally_unique` false.
14. Give the strong vision executor the sources, tokens, evidence, `references/visual-review.md`, and the proof obligations in `scripts/lib/artifact_contract.py`. It authors the entire HTML structure, content strategy, copy, hierarchy, specimen strategy, interaction, and styling from scratch for this run.
15. Do not reuse a proof template, layout bank, theme bank, copy bank, section composition, design seed, automatic visual generator, or prior artifact shell. Styling and content must both respond to the current tokens, source intent, audience task, and proof needs. Stable machine-readable proof obligations are not a visual template.
16. Make every applicable token type and permutation inspectable through an evidence form suited to its meaning. Give every experimental token a visible specimen, strategy, hypothesis, status, and explicit production-use boundary, even when it remains unused. Do not force color, type, dimension, motion, gradient, border, shadow, stroke, transition, and composite values into one repeated card or table grammar. Raw JSON remains a secondary inspectable layer.
17. Run `python3 scripts/assemble_artifact.py --candidate <candidate> --tokens <tokens> --evidence <evidence> --output <proof> --run-id <id>`. The assembler validates structure and embeds canonical data. It does not design or visually certify the artifact.
18. Read `references/visual-review.md`. Inspect the actual HTML with strong native vision at wide and narrow widths, whole-frame and detail scale, and every applicable state, mode, motion preference, input method, data condition, and permutation.
19. Account for every marker in `assets/visual-defect-catalog.json`. Zero unresolved vetoes and zero unresolved major defects are required. Record any novel harmful condition through the unknown marker rather than ignoring it.
20. Account for every invariant in `assets/perceptual-motor-invariant-catalog.json`. Test token feasibility and rendered use. Invariants protect minimum perception, comprehension, and motor outcomes. They do not impose familiar form or block experimental token branches. Use the catalog's creative exception protocol for unconventional directions.
21. Complete separate taste, originality, corpus-uniqueness, and non-AI-slop reviews from `assets/judgment-review-catalog.json`. Record visible evidence and counterevidence. Do not infer authorship from appearance or detector scores.
22. Repair source interpretation, token relations, evidence, or the authored artifact for every failure. Rerun all dependent stages and visual passes. Never change only a verdict. After three failed attempts at the same cause, keep the stage blocked and name the exact missing evidence or capability.
23. Assemble the final evidence and artifact, then perform final readback after assembly. Confirm visible status, embedded records, hashes, run identity, wide and narrow renders, catalog coverage, and claims all agree.
24. Run `mise run ci` after changing the skill. If the task runner is unavailable, use `references/validation.md` and report the direct command results without inventing a task-runner result.
25. Return all four artifacts, SHA-256 values, token counts by DTCG type, full-universe and context coverage, declared comparison scope, review coverage, check exits, and remaining limits.

## Loading map

- Read `references/deterministic-execution.md` before every command.
- Read `references/multimodal-inspection.md` for `generate` and any visual, audio, spatial, interactive, or mixed source.
- Read `references/dtcg-2025.10.md` and `references/category-taxonomy.md` before token authoring or repair.
- Read `references/originality-rubric.md` before identity, signature, or comparison decisions.
- Read `references/visual-review.md` before proof authorship and every visual review.
- Read `references/evidence-schema.md` before writing evidence.
- Read `references/validation.md` before package verification.
- Use `assets/evidence-template.json` as a record skeleton and `assets/dtcg-format-2025.10.schema.json` as the pinned conformance copy.
- Read `assets/exploration-strategy-catalog.json` before possibility narrowing and experimental token selection.
- Read the matching file in `examples/` before a command. Read `examples/failure-global-claim.md` for absolute uniqueness requests.
- Read `evals/contract.md` and `evals/rubric.md` before changing behavior or acceptance gates.
- Run the behavioral checks in `scripts/tests/` after changing scripts, catalogs, evidence rules, or artifact obligations.
- Read `references/generation-contract.md` before changing this package and `references/decisions.md` before changing an established decision.

## Boundaries

- Token count is not quality evidence. Unsupported tokens and ornamental scale completion count against the result.
- DTCG conformance, source specificity, taste, originality, corpus-bounded uniqueness, non-AI-slop, invariants, and artifact integrity are separate claims.
- A token file alone cannot prove rendered invariants or visual quality.
- A machine check cannot visually certify an artifact. A vision review cannot override a measured conformance, contrast, overflow, or hash failure.
- Experimental tokens may remain without a passing rendered-use claim. A failed experiment blocks only that clean-use claim, not further exploration.
- The proof artifact exposes failures and limits as prominently as passes. It is evidence, not a self-awarded certificate.
- Global uniqueness cannot be proved without an exhaustive comparison corpus.

## Completion

Done requires four readable artifacts; token validation exit 0; complete input, intent, possibility, context, and permutation accounting; at least two experimental tokens from two distinct strategies with exact cross-artifact path coverage; at least five signature decisions; a named comparison corpus; a vision-authored run-specific HTML artifact; wide and narrow final readback; complete defect, invariant, taste, originality, corpus-uniqueness, and non-AI-slop reviews; zero unresolved vetoes or major defects; and a fresh package validation. Any missing gate blocks a clean non-slop or one-of-a-kind-within-corpus claim.
