# Vision execution gate

Use this gate before any source interpretation, token judgment, proof authorship, or visual verdict. Read `references/qualitative-judgment.md` with it so the capability probe covers open-ended interpretation as well as spatial and defect checks. A capability label or self-description is not evidence. Prove the required operations on the supplied inputs and record the result in `<name>.run.json`. Use `mise run token-packet -- <args>` for this routed resource.

Load the fixture and pair paths from `assets/vision-probe-manifest.json`. Inspect each named region in the actual rendered pixels. Confirm that the reviewer can distinguish the known failure from its stated pass countercondition. The countercondition is a test distinction, not a positive artifact or a style to copy. Use `mise run token-packet -- <args>` for this routed resource.

## Capability probe

Run every check below against the actual source set. Record `pass`, `fail`, or `not_applicable`, the inspected locator, one observed fact, and one countercheck for each item.

1. **Direct pixels:** Open every supplied visual source as pixels or rendered frames. Record one whole-frame fact that cannot be copied from its filename, metadata, OCR, document tree, or surrounding text.
2. **Regional inspection:** Zoom into at least two decision-bearing regions per visual source. Record their locators and facts about spacing, edges, crop, overlap, alignment, type, color relation, state, or material detail.
3. **Spatial reasoning:** Identify foreground and background, containment, occlusion, adjacency, alignment, reading order, and any collision or unintended overlap that affects interpretation.
4. **Comparison:** When two sources, frames, states, or modes exist, inspect them side by side. Record what stays invariant, what changes, and whether the change is intentional, harmful, or unresolved.
5. **Responsive review:** Confirm a path to render and inspect the final standalone HTML at one wide and one narrow viewport. The final review must use actual rendered pixels; markup, styles, a document tree, or computed values alone do not pass.
6. **Detail retention:** Confirm that zoomed inspection preserves enough detail to judge small type, strokes, focus treatment, target spacing, clipping, crops, and microalignment.
7. **Evidence discipline:** Separate observations from inferences and assumptions. Record confidence and the strongest visible counterevidence for every high-impact judgment.
8. **Artifact authorship:** Confirm that the same strong vision executor can author the run-specific HTML composition and later inspect its final assembled pixels. Delegating only the final verdict does not pass.
9. **Qualitative range:** Confirm that the executor can identify source-specific mood, tension, rhythm, material character, cultural context, interaction feel, competing readings, and emergent qualities without forcing them into a score or house style.

## Delegation packet

If any required probe fails, transfer every judgment task to one strong vision-capable model. Send exact source bytes or stable locators, the frozen task packet, source inventory, observations already limited to mechanical facts, all applicable catalogs, the current stage inputs, required output paths, and this file. Require the returned packet to include the vision executor identity, probe results, located observations, identity thesis, token decisions, signature decisions, authored HTML candidate, wide and narrow findings, defect and invariant records, four judgment tracks, counterevidence, limits, and final readback.

The primary executor may only inventory, hash, validate, preserve records, run deterministic scripts, and assemble the returned candidate. It may not write or revise the thesis, tokens, visual composition, taste verdict, originality verdict, uniqueness verdict, invariant verdict, defect verdict, or non-AI-slop verdict.

## PASS

The gate passes only when exactly one active or delegated strong vision executor passes every applicable probe, directly inspects every supplied visual, owns every judgment task, can author the proof artifact, and has a verified path to inspect the final HTML at wide and narrow widths. Save the executor, capability evidence, delegation state, allowed mechanical tasks, and all probe results under `vision_execution` in `<name>.run.json` and mirror the executor record in `<name>.evidence.json`.

## BLOCKED

Set `E_VISION` and stop before thesis, token, proof, or visual-claim work when no executor passes every applicable probe, a supplied visual cannot be inspected directly, delegation omits any judgment task, or final rendered pixels cannot be reviewed. Save the failed probe, attempted path, exact missing capability, and permitted mechanical work. Do not substitute OCR, metadata, sampled colors, a document tree, a screenshot file that nobody inspected, or a detector score for direct visual judgment.
