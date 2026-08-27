# Execution: review and completion

Run Steps 18 through 25 in order. Use the command table in `references/execution-guide.md`. `assets/execution-io-map.json` owns each step packet and `scripts/run_pipeline.py` owns run state, hashes, and handoffs.

## Step 18: Inspect final HTML

**Input**
`artifact.proof`, `proof.coverage-map`, `source.payload`, and `vision.execution`.

**Action**
Create and start the S18 packet with `scripts/run_pipeline.py`. The strong vision executor applies `assets/vision-probe-manifest.json`, `references/visual-review.md`, and `references/google-font-selection.md` to the assembled HTML. Inspect wide, narrow, whole-frame, detail, every applicable state, mode, motion, input, data, permutation, corpus comparison, and selected-font specimen. Confirm actual font rendering and fallback-sensitive line breaks.

**Save**
Save `review.visual` as `<name>.records/S18-review.visual.json`, with viewport, state, region, observation, countercheck, status, and required repair.

**Pass**
Every required surface and font specimen has located final-pixel evidence on the registered proof hash, with no unseen or fallback-dependent claim. Use `scripts/run_pipeline.py pass` with `review.visual`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_REVIEW` when a required surface, state, viewport, comparison, or font render is unseen or fails. Name the exact condition.

**Feeds**
Step 19 consumes `review.visual` and `artifact.proof`.

## Step 19: Resolve defects

**Input**
`review.visual` and `artifact.proof`.

**Action**
Create and start the S19 packet with `scripts/run_pipeline.py`. The strong vision executor checks every marker in `assets/visual-defect-catalog.json` under `references/visual-review.md`. Measure when possible; inspect overlap, clipping, illegibility, contrast, typography, fallback, geometry, interaction, response, content, hierarchy, false affordance, and proof integrity. Add a newly observed harm as a bounded unknown marker before deciding it.

**Save**
Save `review.defects` as `<name>.records/S19-review.defects.json`, with marker IDs, evidence, severity, repair, rerun set, and final status.

**Pass**
Every marker has one disposition and zero vetoes or major defects remain unresolved. Use `scripts/run_pipeline.py pass` with `review.defects`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_REVIEW` when a veto, major defect, or applicable marker remains unresolved. Name the region, harm, and earliest repair step.

**Feeds**
Step 20 consumes `review.defects`, `artifact.tokens`, and `artifact.proof`.

## Step 20: Resolve invariants

**Input**
`review.defects`, `artifact.tokens`, and `artifact.proof`.

**Action**
Create and start the S20 packet with `scripts/run_pipeline.py`. The strong vision executor tests every entry in `assets/perceptual-motor-invariant-catalog.json` in token feasibility and rendered use, guided by `references/screen-decision.md`. Cover human-eye legibility, brain-level hierarchy and grouping, motion and cognitive load, reach and touch targets, focus, input, response, and error recovery. Apply the creative exception protocol without imposing a house style.

**Save**
Save `review.invariants` as `<name>.records/S20-review.invariants.json`, with invariant ID, evidence, state, status, gain, cost, counterevidence, exception, and claim boundary.

**Pass**
Every invariant appears once, no claimed use fails, and every exception has located evidence and an equal or better protected outcome. Use `scripts/run_pipeline.py pass` with `review.invariants`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_REVIEW` when an applicable invariant is missing, a claimed use fails, or an exception lacks evidence. Name the failing outcome rather than prescribing familiar form.

**Feeds**
Step 21 consumes `review.invariants`, `review.defects`, `artifact.proof`, `source.payload`, and `signature.decisions`.

## Step 21: Judge four tracks

**Input**
`review.invariants`, `review.defects`, `artifact.proof`, `source.payload`, and `signature.decisions`.

**Action**
Create and start the S21 packet with `scripts/run_pipeline.py`. The strong vision executor applies `assets/judgment-review-catalog.json`, `references/qualitative-judgment.md`, and `references/multimodal-originality.md`. Judge taste, originality, named-corpus uniqueness, and non-AI-slop separately. Start with every lens, narrow by evidence, add emergent lenses, compare alternatives and corpus neighbors, record competing readings and counterevidence, and never infer authorship from appearance.

**Save**
Save `review.judgment` as `<name>.records/S21-review.judgment.json`, with four separate records, located evidence, uncertainty, competing readings, corpus scope, limitations, and claim wording.

**Pass**
All four tracks pass within their stated scope, all claims match evidence, and `globally_unique` remains false. Use `scripts/run_pipeline.py pass` with `review.judgment`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_REVIEW` or `E_CLAIM` when a track fails, lacks located evidence, exceeds its corpus, hides uncertainty, or claims authorship from appearance.

**Feeds**
Step 22 consumes `review.judgment`, `review.invariants`, and `review.defects`.

## Step 22: Repair causes

**Input**
`review.judgment`, `review.invariants`, `review.defects`, and every earlier failed gate.

**Action**
Create and start the S22 packet with `scripts/run_pipeline.py`. Apply `references/deterministic-execution.md`. Find the earliest causal source, token relation, record, or proof region; repair it; set that step and every dependent step back to `RUNNING`; rerun them in order. Stop after three failed attempts at the same cause.

**Save**
Save `repair.result` as `<name>.records/S22-repair.result.json`, with attempt number, cause, change, rerun set, fresh checks, and outcome.

**Pass**
The earliest cause and every dependent gate pass on current inputs, bytes, and pixels. Use `scripts/run_pipeline.py pass` with `repair.result`.

**Blocked**
Use `scripts/run_pipeline.py block` with the original allowed error code after three failed attempts or when required evidence or capability is missing. State the exact recovery need; never change only the verdict.

**Feeds**
Step 23 consumes `repair.result`, `artifact.tokens`, `artifact.evidence`, `artifact.proof`, and `run.contract`.

## Step 23: Read back final bytes

**Input**
`repair.result`, `artifact.tokens`, `artifact.evidence`, `artifact.proof`, and `run.contract`.

**Action**
Create and start the S23 packet with `scripts/run_pipeline.py`. Apply `references/evidence-schema.md` and `references/google-font-selection.md`. Rehash all four deliverables, reopen the final HTML, visually inspect its exact pixels, and compare visible verdicts, embedded records, run ID, coverage, viewports, source claims, font ranks, catalog date and hash, WOFF2 hashes, licenses, uncertainty, and limits. Do not reassemble after this readback.

**Save**
Save `final.readback` as `<name>.records/S23-final.readback.json`, with hashes, locators, review time, and a criterion-to-evidence map. Store the full HTML byte hash in `<name>.run.json`.

**Pass**
Every artifact, font record, review, and claim agrees after final assembly, and each completion criterion has same-date evidence. Use `scripts/run_pipeline.py pass` with `final.readback`.

**Blocked**
Use `scripts/run_pipeline.py block` with the first matching `E_FONT_CURRENT`, `E_FONT_ASSET`, `E_ASSEMBLY`, `E_REVIEW`, or `E_CLAIM` when any hash, ID, verdict, record, claim, or limit differs.

**Feeds**
Step 24 consumes `final.readback` and the current package tree.

## Step 24: Validate the package

**Input**
`final.readback` and every persistent file in the current skill directory.

**Action**
Create and start the S24 packet with `scripts/run_pipeline.py`. Read `references/generation-contract.md`, `references/decisions.md`, `references/validation.md`, `references/file-trigger-audit.md`, `evals/contract.md`, `evals/rubric.md`, and `evals/source-lineage.json`. Run the task graph in `mise.toml`, including `scripts/validate_skill.py`, `scripts/audit_file_triggers.py`, `scripts/check_evals.py`, and every discovered file in `scripts/tests/`. Run the current official `skills-ref validate .` check in an isolated environment. Parse every JSON file, compile every Python file, run every script help path, inspect every Markdown file, and confirm negative fixtures remain negative.

**Save**
Save `package.validation` as `<name>.records/S24-package.validation.json`, with commands, exits, outputs, skill hash, file count, byte count, checked paths, trigger routes, and limitations of each check.

**Pass**
Every required current-byte check exits 0, every persistent file has a named activation or consumer route, and the recorded tree hash matches the checked package. Use `scripts/run_pipeline.py pass` with `package.validation`.

**Blocked**
Use `scripts/run_pipeline.py block` with the applicable error code when a check fails, is skipped, uses stale bytes, or leaves a file without a real route. Name the canonical owner and focused recovery command.

**Feeds**
Step 25 consumes `package.validation`, `final.readback`, `run.contract`, and all 25 step records.

## Step 25: Return proved results

**Input**
`package.validation`, `final.readback`, `run.contract`, and every step record in `<name>.run.json`.

**Action**
Create and start the S25 packet with `scripts/run_pipeline.py`. Apply `references/deterministic-execution.md` and `references/evidence-schema.md`. Check every `SKILL.md` Completion row; return artifact paths, hashes, counts, universe and context coverage, corpus scope, visual-review coverage, command exits, failed gates, uncertainty, and limits. Never report one deliverable as the whole result.

**Save**
Save `completion.disposition` as `<name>.records/S25-completion.disposition.json` and include final status, artifacts, criterion map, failed gates, and recovery needs.

**Pass**
All 25 step records and every Completion gate are `PASS` on current inputs and final bytes, and every claim has artifact, command, or located visual evidence. Use `scripts/run_pipeline.py pass` with `completion.disposition`, then confirm `scripts/run_pipeline.py status` reports complete.

**Blocked**
Use `scripts/run_pipeline.py block` with the earliest failed gate's code when any step or Completion row is unproved. Return its ID and recovery need while withholding non-slop, originality, corpus uniqueness, and completion claims.

**Feeds**
The user receives only the proved artifacts, evidence, limitations, and exact recovery needs from `completion.disposition`.
