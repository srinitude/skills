# Execution: token and proof build

Run Steps 09 through 17 in order. Use the command table in `references/execution-guide.md`. `assets/execution-io-map.json` owns each step packet and `scripts/run_pipeline.py` owns run state, hashes, and handoffs.

## Step 09: Map contexts

**Input**
`exploration.ledger`, `token.universe`, `statement.register`, and `observation.register`.

**Action**
Create and start the S09 packet with `scripts/run_pipeline.py`. Apply `references/evidence-schema.md`, `references/screen-decision.md`, and `assets/screen-possibility-space.json`. Map every requirement and possibility across applicable type, role, state, mode, component, context, value, viewport, motion, input, data, environment, and physical condition cells.

**Save**
Save `context.matrix` as `<name>.records/S09-context.matrix.json`, with one token, omission, experiment, or non-applicability disposition for every requirement and cell.

**Pass**
Every requirement and applicable matrix cell has one reasoned disposition and no cell is silently dropped. Use `scripts/run_pipeline.py pass` with `context.matrix`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_EVIDENCE` when any requirement or applicable cell lacks a disposition. Name its stable ID.

**Feeds**
Step 10 consumes `context.matrix`, `token.universe`, and `identity.thesis`.

## Step 10: Create signatures

**Input**
`context.matrix`, `token.universe`, and `identity.thesis`.

**Action**
Create and start the S10 packet with `scripts/run_pipeline.py`. The strong vision executor applies `references/originality-rubric.md` and `references/creative-transfer.md` to create at least five sourced decisions across at least three axes. For typography, follow `references/google-font-selection.md` and run `scripts/prepare_google_fonts.py`; compare at least three same-date eligible families outside the popular half.

**Save**
Save `signature.decisions` as `<name>.records/S10-signature.decisions.json`, including each evidence-to-token-to-render chain, cross-axis relation, generic default replaced, and the complete `font.selection` record.

**Pass**
Every signature is source-specific, useful to the audience, connected to another axis, and visually judged against alternatives; font candidates and selections satisfy currentness, rarity, license, asset, and specimen checks. Use `scripts/run_pipeline.py pass` with `signature.decisions`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_EVIDENCE`, `E_FONT_CURRENT`, `E_FONT_RARITY`, or `E_REVIEW` when decision or typography evidence fails. Name the failed signature or font gate.

**Feeds**
Step 11 consumes `signature.decisions`, `context.matrix`, and `token.universe`.

## Step 11: Author tokens

**Input**
`signature.decisions`, `context.matrix`, and `token.universe`.

**Action**
Create and start the S11 packet with `scripts/run_pipeline.py`. Apply `references/dtcg-2025.10.md` and `assets/dtcg-format-2025.10.schema.json`. Write stable paths, `$type`, `$value`, `$description`, valid aliases, namespaced extensions, experimental metadata, and selected font paths. Include each retained path once and no excluded path.

**Save**
Save `artifact.tokens` as `<name>.tokens.json` in stable path order.

**Pass**
The file exactly matches retained universe, context, signature, experimental, and font records. Use `scripts/run_pipeline.py pass` with `artifact.tokens` so the exact bytes are hashed.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_DTCG` or `E_FONT_RARITY` when a value, path, alias, type, extension, experimental record, or selected font would misstate evidence.

**Feeds**
Step 12 consumes `artifact.tokens`.

## Step 12: Validate tokens

**Input**
`artifact.tokens` from the exact saved `<name>.tokens.json` bytes.

**Action**
Create and start the S12 packet with `scripts/run_pipeline.py`. Run `scripts/validate_dtcg.py`; save its complete machine-readable result, including command, stdout, stderr, exit code, schema hash, counts, and token hash. Fix the source architecture rather than the verdict.

**Save**
Save `validation.dtcg` as `<name>.records/S12-validation.dtcg.json`.

**Pass**
The validator exits 0 and reports `valid: true` for the registered token hash. Use `scripts/run_pipeline.py pass` with `validation.dtcg`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_DTCG` for any current-byte error. Include the validator evidence and earliest repair step.

**Feeds**
Step 13 consumes `validation.dtcg` and every named record listed in its packet.

## Step 13: Build evidence

**Input**
`validation.dtcg`, `artifact.tokens`, `run.contract`, `source.inventory`, `observation.register`, `statement.register`, `identity.thesis`, `token.universe`, `exploration.ledger`, `context.matrix`, and `signature.decisions`.

**Action**
Create and start the S13 packet with `scripts/run_pipeline.py`. Fill `assets/evidence-template.json` under `references/evidence-schema.md` and `assets/originality-analysis-contract.json`. Join IDs and hashes; record corpus, thresholds, experiments, originality proxies, claim limits, Google Fonts data, token-to-source relations, review plans, and pending judgment. Keep `globally_unique` false.

**Save**
Save `artifact.evidence` as `<name>.evidence.json`.

**Pass**
Every required section exists and all shared IDs, paths, hashes, font assets, experiment records, claims, and limits agree. Use `scripts/run_pipeline.py pass` with `artifact.evidence`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_EVIDENCE` or `E_FONT_ASSET` when a record is missing, two records conflict, or a required asset or license hash is absent.

**Feeds**
Step 14 consumes `artifact.evidence`, `artifact.tokens`, `vision.execution`, and `source.payload`.

## Step 14: Author proof

**Input**
`artifact.evidence`, `artifact.tokens`, `vision.execution`, and the original `source.payload`.

**Action**
Create and start the S14 packet with `scripts/run_pipeline.py`. The strong vision executor reads `references/visual-review.md`, `references/writing-style.md`, `references/google-font-selection.md`, and `scripts/lib/artifact_contract.py`, then authors the standalone HTML structure, content, copy, hierarchy, specimens, interactions, and style from this run's evidence and tokens. Do not reuse a visual shell. Embed prepared font CSS with exact WOFF2 data URLs.

**Save**
Save `proof.candidate` as `<name>.proof.candidate.html` and include the obligation-to-region map in `<name>.records/S14-proof.candidate.json`.

**Pass**
Every proof obligation appears once, each region has a source-specific purpose, every selected font is embedded and visible, and raw JSON is secondary. Use `scripts/run_pipeline.py pass` with `proof.candidate` pointing to the HTML candidate.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_VISION`, `E_FONT_ASSET`, or `E_ASSEMBLY` when vision authorship is absent, a region cannot be built truthfully, or an external dependency remains.

**Feeds**
Step 15 consumes `proof.candidate`, `identity.thesis`, and `source.inventory`.

## Step 15: Reject reused shells

**Input**
`proof.candidate`, `identity.thesis`, `source.inventory`, and the frozen comparison corpus.

**Action**
Create and start the S15 packet with `scripts/run_pipeline.py`. The strong vision executor applies `references/deterministic-execution.md`, `references/multimodal-originality.md`, and `assets/exploration-corpus/negative-patterns.json`. Compare with prior proof artifacts, substitute unrelated domains, remove signature relations, inspect common synthetic patterns, and repair any portable layout, copy, theme, or composition.

**Save**
Save `proof.originality-review` as `<name>.records/S15-proof.originality-review.json`, with comparisons, regions, counterevidence, repairs, uncertainty, and the current candidate hash.

**Pass**
No generic shell survives substitution or removal tests, and no high-risk negative pattern remains without a sourced reason. Use `scripts/run_pipeline.py pass` with `proof.originality-review`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_REVIEW` when a reused shell, stock composition, portable content pattern, or unsupported novelty remains.

**Feeds**
Step 16 consumes `proof.originality-review`, `proof.candidate`, `artifact.tokens`, `context.matrix`, and `exploration.ledger`.

## Step 16: Expose coverage

**Input**
`proof.originality-review`, `proof.candidate`, `artifact.tokens`, `context.matrix`, and `exploration.ledger`.

**Action**
Create and start the S16 packet with `scripts/run_pipeline.py`. Use `scripts/lib/artifact_contract.py` and `scripts/lib/coverage.py` to enumerate exact token, stress-cell, permutation, and experiment sets. Give each retained item one meaning-specific visible region with stable data attributes. Escape attribute values without changing decoded identifiers.

**Save**
Save `proof.coverage-map` as `<name>.records/S16-proof.coverage-map.json` with exact item-to-region relations.

**Pass**
Token, matrix, experiment, and visible region sets match exactly with no extras, omissions, or raw-JSON-only proof. Use `scripts/run_pipeline.py pass` with `proof.coverage-map`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_ASSEMBLY` when an applicable token, permutation, stress cell, or experiment lacks a truthful specimen.

**Feeds**
Step 17 consumes `proof.coverage-map`, `proof.candidate`, `artifact.tokens`, `artifact.evidence`, and `run.contract`.

## Step 17: Assemble proof

**Input**
`proof.coverage-map`, `proof.candidate`, `artifact.tokens`, `artifact.evidence`, and `run.contract`.

**Action**
Create and start the S17 packet with `scripts/run_pipeline.py`. Run `scripts/assemble_artifact.py` to validate obligations and embed canonical records. The assembler may check and copy bytes but must not choose layout, styling, copy, hierarchy, or judgment. Verify every embedded font, token, evidence, and surface hash.

**Save**
Save `artifact.proof` as the self-contained `<name>.proof.html`.

**Pass**
Assembly exits 0, one offline HTML file remains intact, selected fonts are visibly used, WOFF2 hashes match evidence, all authored regions remain, and no machine verdict replaces visual review. Use `scripts/run_pipeline.py pass` with `artifact.proof`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_FONT_ASSET` or `E_ASSEMBLY` when assembly fails, a font is external, unused, invalid, or mismatched, an embedded record differs, or an authored region changes.

**Feeds**
Step 18 consumes `artifact.proof`, `proof.coverage-map`, `source.payload`, and `vision.execution`.
