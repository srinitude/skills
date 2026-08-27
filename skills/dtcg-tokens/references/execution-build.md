# Execution: token and proof build

Run Steps 09 through 17 in order. Use the exact fields defined in `references/execution-guide.md` and the handoffs in `assets/execution-io-map.json`.

## Step 09: Map contexts

- **Purpose:** Connect requirements and token possibilities to every state and condition in which people may use them.
- **Consumes:** `exploration.ledger`, `token.universe`, `statement.register`, and `observation.register`.
- **Action:** Use `references/evidence-schema.md`; map every requirement to a token path or explicit omission; expand each applicable type, role, state, mode, component, context, value, viewport, motion, input, and data cell.
- **Produces:** `context.matrix` with one reasoned disposition for every requirement and applicable permutation.
- **PASS when:** Every requirement and matrix cell maps to a token, omission, or stated non-applicability reason.
- **BLOCKED when:** Any requirement or applicable cell has no disposition; set `E_EVIDENCE`.
- **Recovery:** Fix the missing relationship in Steps 04 through 08, then rebuild Step 09.

## Step 10: Create signatures

- **Purpose:** Turn source evidence into connected decisions that make the system distinct.
- **Consumes:** `context.matrix`, `token.universe`, and `identity.thesis`.
- **Action:** Apply `references/originality-rubric.md`; create at least five sourced decisions across at least three axes; for each, name evidence, token paths, rendered target, audience fit, and the generic default it replaces; reject decoration without purpose.
- **Produces:** `signature.decisions`, ordered by downstream effect and linked across axes.
- **PASS when:** Every decision traces source to token to render, fits the audience, and interacts with another axis.
- **BLOCKED when:** Fewer than five decisions or three axes pass evidence checks; set `E_EVIDENCE`.
- **Recovery:** Return to Steps 06 through 09, strengthen the source link, and rebuild Step 10.

## Step 11: Author tokens

- **Purpose:** Encode the retained system as truthful, stable-path DTCG JSON.
- **Consumes:** `signature.decisions`, `context.matrix`, and `token.universe`.
- **Action:** Follow `references/dtcg-2025.10.md` and `assets/dtcg-format-2025.10.schema.json`; write `$schema`, valid types, aliases, descriptions, namespaced extensions, and valid names; include each retained path once and no excluded path.
- **Produces:** `artifact.tokens` as `<name>.tokens.json` plus its hash.
- **PASS when:** The file matches the retained ledger, matrix, signatures, and exclusions exactly.
- **BLOCKED when:** A value, path, alias, type, or extension would misstate the evidence; set `E_DTCG`.
- **Recovery:** Fix the earliest ledger, matrix, or authoring cause, then rerun Step 11.

## Step 12: Validate tokens

- **Purpose:** Prove DTCG conformance on the exact token bytes that later artifacts will embed.
- **Consumes:** `artifact.tokens`.
- **Action:** Run `python3 scripts/validate_dtcg.py <name>.tokens.json`; read every error; fix the source architecture, not the verdict; rerun on current bytes.
- **Produces:** `validation.dtcg` with command, stdout, stderr, exit code, schema hash, counts, and token hash.
- **PASS when:** The command exits 0 and reports `valid: true` for the saved token hash.
- **BLOCKED when:** Any current-byte error remains; set `E_DTCG` and withhold conformance.
- **Recovery:** Fix the cited source relation or token value, then rerun Steps 11 and 12.

## Step 13: Build evidence

- **Purpose:** Join the run, sources, observations, decisions, tokens, review plans, corpus, and claim limits in one record.
- **Consumes:** `validation.dtcg`, `artifact.tokens`, `run.contract`, `source.inventory`, `observation.register`, `statement.register`, `identity.thesis`, `token.universe`, `exploration.ledger`, `context.matrix`, and `signature.decisions`.
- **Action:** Fill `assets/evidence-template.json` under `references/evidence-schema.md`; freeze a named comparison corpus and thresholds; keep judgment pending and `globally_unique` false.
- **Produces:** `artifact.evidence` as `<name>.evidence.json` plus its hash.
- **PASS when:** Every required section exists and all shared IDs, paths, hashes, claims, and limits agree.
- **BLOCKED when:** A required record is missing or two records conflict; set `E_EVIDENCE`.
- **Recovery:** Fix the earliest upstream record, rerun its dependents, then rebuild Step 13.

## Step 14: Author proof

- **Purpose:** Create a proof surface specific to the sources and tokens, not a reused visual shell.
- **Consumes:** `artifact.evidence`, `artifact.tokens`, `vision.execution`, and `source.payload`.
- **Action:** The Step 03 vision executor must read `references/visual-review.md` and `scripts/lib/artifact_contract.py`, then author the full standalone HTML structure, copy, hierarchy, specimens, interactions, and style from current evidence; make the template different for each token system.
- **Produces:** `proof.candidate` plus an obligation-to-region map.
- **PASS when:** Every proof obligation exists once, each region has a source-specific purpose, and raw JSON is not the only proof.
- **BLOCKED when:** Vision authorship is absent or a required region cannot be built truthfully; set `E_VISION` or `E_ASSEMBLY`.
- **Recovery:** Restore the Step 03 vision path or fix the missing evidence, then reauthor Step 14.

## Step 15: Reject reused shells

- **Purpose:** Detect generic layout, theme, copy, or composition reuse.
- **Consumes:** `proof.candidate`, `identity.thesis`, and `source.inventory`.
- **Action:** Use `references/deterministic-execution.md`; compare the candidate with prior proof artifacts and move it to an unrelated domain; reauthor any template, layout, theme, copy, composition, seed, generator output, or shell that survives either test.
- **Produces:** `proof.originality-review` with comparisons, matched regions, repairs, and a fresh candidate hash.
- **PASS when:** No generic shell survives either test.
- **BLOCKED when:** A reused shell, stock composition, or portable content pattern remains; set `E_REVIEW`.
- **Recovery:** Reauthor the cited region from the thesis and evidence, then rerun Step 15.

## Step 16: Expose coverage

- **Purpose:** Make each token and permutation visible so coverage is inspected, not inferred from data.
- **Consumes:** `proof.originality-review`, `proof.candidate`, `artifact.tokens`, `context.matrix`, and `exploration.ledger`.
- **Action:** Follow `references/deterministic-execution.md`; give every retained token a meaningful specimen marked once with `data-token-path`, every generated stress cell a visible comparison marked once with `data-stress-cell`, and every applicable or explicitly excluded context permutation a visible record marked once with `data-permutation-cell`; show each experiment with strategy, hypothesis, status, and boundary; keep raw JSON secondary. Escape attribute values as HTML without changing their decoded identifiers.
- **Produces:** `proof.coverage-map` with exact token-to-region, permutation-to-region, and experiment-to-region links.
- **PASS when:** Token, matrix, experiment, and visible region sets match exactly.
- **BLOCKED when:** An applicable token, permutation, or experiment lacks a truthful specimen; set `E_ASSEMBLY`.
- **Recovery:** Add or fix the missing specimen without changing unrelated regions, then rerun Step 16.

## Step 17: Assemble proof

- **Purpose:** Produce one self-contained HTML file without changing the authored design.
- **Consumes:** `proof.coverage-map`, `proof.candidate`, `artifact.tokens`, `artifact.evidence`, and `run.contract`.
- **Action:** Run the command documented by `scripts/assemble_artifact.py`; let the assembler validate and embed records only; do not let it choose layout, style, hierarchy, copy, or judgment. A pending run reports `reviewed_surface_sha256`. After strong-vision review records that exact surface hash in evidence, rerun the same candidate to obtain recorded-pass state.
- **Produces:** `artifact.proof` as `<name>.proof.html`, with command output, exit code, proof hash, and embedded hashes.
- **PASS when:** Exit 0 creates one self-contained HTML file, all authored regions remain intact, the reported surface hash matches final evidence for recorded-pass state, and no machine-selected visual verdict substitutes for the review record.
- **BLOCKED when:** Assembly fails, an embedded hash differs, or an authored region changes; set `E_ASSEMBLY`.
- **Recovery:** Fix the cited input or assembler defect, then rerun Step 17 on current inputs.
