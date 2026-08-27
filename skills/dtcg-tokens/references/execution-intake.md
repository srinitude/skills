# Execution: intake and discovery

Run Steps 01 through 08 in order. Use the exact fields defined in `references/execution-guide.md` and the handoffs in `assets/execution-io-map.json`.

## Step 01: Freeze the run

- **Purpose:** Fix the request, sources, outputs, and date so every later claim uses the same task.
- **Consumes:** `request.packet` and `source.payload` from the user or an authorized source.
- **Action:** Follow `references/deterministic-execution.md`; choose `<name>` and a run ID; run `scripts/current_anchor.py` once; record the command, source order, outputs, acceptance terms, limits, state, and retries before judgment.
- **Produces:** `run.contract` in `<name>.run.json`, with source locators and the clock anchor.
- **PASS when:** Every required field exists, each source has a locator, and the output set is explicit.
- **BLOCKED when:** Any required request, source, output, or acceptance term is missing; set `E_INPUT` and stop judgment.
- **Recovery:** Get the missing item, keep the run ID if scope did not change, and rerun Step 01.

## Step 02: Inventory input and intent

- **Purpose:** Record what each source is and how it may influence the result before reading it as design direction.
- **Consumes:** `run.contract` and the same `source.payload` frozen in Step 01.
- **Action:** Check every format and intent facet in `assets/multimodal-input-catalog.json`; hash stable bytes; record locator, access, channels, role, authority, influence, scope, conflicts, and supported extensions; keep format separate from intent.
- **Produces:** `source.inventory` with one format record, one intent record, and hashes for each source.
- **PASS when:** Every source appears once in both inventories and each influence claim names its authority and scope.
- **BLOCKED when:** A source cannot be accessed, hashed, or classified without guessing; set `E_INPUT`.
- **Recovery:** Restore access or narrow the run with user authority, then rerun Step 02 and its dependents.

## Step 03: Prove vision execution

- **Purpose:** Put all visual interpretation, design decisions, proof authorship, and final judgment on one strong vision path.
- **Consumes:** `source.inventory`, `run.contract`, and the source payloads they name.
- **Action:** Run every probe in `references/vision-execution.md`; require direct whole-frame and detail inspection, located findings, comparison judgment, and rendered readback; if any probe fails, send the full packet to one strong vision-capable model and delegate every judgment task through Step 23 while keeping other work mechanical.
- **Produces:** `vision.execution` with the executor, probe results, observations, counterchecks, delegation boundary, and allowed mechanical tasks.
- **PASS when:** One strong vision executor owns source inspection, token decisions, HTML authorship, and final visual review, and all probes pass.
- **BLOCKED when:** No qualified vision executor can inspect the sources and final renders; set `E_VISION` and do not generate tokens or proof.
- **Recovery:** Provide a qualified vision route with the full frozen packet, then rerun Step 03.

## Step 04: Observe visuals

- **Purpose:** Turn each source into located facts without treating OCR, measurements, inference, or taste as direct observation.
- **Consumes:** `vision.execution`, `source.inventory`, and `source.payload`.
- **Action:** Apply `references/multimodal-inspection.md` at whole-frame, detail, and comparison scales; record source ID, locator, region, observation, confidence, counterevidence, and any OCR or measurement support for each fact.
- **Produces:** `observation.register` with one located record per material fact.
- **PASS when:** Every accessible visual and material source has all applicable passes and every fact points to a location.
- **BLOCKED when:** A required surface is unseen or a fact has no located evidence; set `E_EVIDENCE`.
- **Recovery:** Inspect the missing surface or remove the unsupported fact, then rerun Step 04.

## Step 05: Classify statements

- **Purpose:** Keep source facts, interpretations, and assumptions distinct.
- **Consumes:** `observation.register`, `run.contract`, and all material source clauses.
- **Action:** Follow `references/evidence-schema.md`; mark each statement `observed`, `inferred`, or `assumed`; link its evidence; ask once only when a missing fact would change the system; otherwise limit the assumption and its influence.
- **Produces:** `statement.register` with one basis, evidence link, confidence, limit, and affected outputs per statement.
- **PASS when:** Every material statement has one basis and no assumption is presented as observation.
- **BLOCKED when:** An unlimited unknown can change token architecture or proof claims; set `E_INPUT`.
- **Recovery:** Resolve the unknown or limit its influence in the run contract, then rerun Step 05.

## Step 06: Falsify the thesis

- **Purpose:** Create a source-specific thesis that does not fit unrelated work unchanged.
- **Consumes:** `statement.register`, `observation.register`, audience evidence, and source constraints.
- **Action:** Use `references/originality-rubric.md`; state the audience, use, intended feeling, and source-specific idea in one sentence; substitute two unrelated domains; revise until both substitutions fail for evidence-backed reasons.
- **Produces:** `identity.thesis` with evidence IDs, substitutions, failures, revisions, and claim limits.
- **PASS when:** Every clause is sourced and neither unrelated substitution remains credible.
- **BLOCKED when:** The thesis is generic, unsupported, or portable; set `E_EVIDENCE`.
- **Recovery:** Return to Step 04 or 05 for missing evidence, then rebuild and retest the thesis.

## Step 07: Expand the token universe

- **Purpose:** List the full token possibility surface before excluding anything.
- **Consumes:** `identity.thesis` and `statement.register`.
- **Action:** Read `assets/token-possibility-catalog.json`, `references/dtcg-2025.10.md`, and `references/category-taxonomy.md`; place every catalog leaf in the ledger before exclusions; add source- or intent-backed extensions with stable IDs.
- **Produces:** `token.universe`, with every catalog leaf and extension represented once.
- **PASS when:** Every leaf appears exactly once and every extension cites a source or intent record.
- **BLOCKED when:** A leaf is missing, duplicated, or excluded before review; set `E_EVIDENCE`.
- **Recovery:** Restore the full ledger, fix duplicate IDs, and rerun Step 07.

## Step 08: Generate experiments

- **Purpose:** Reserve real token capacity for exploration without adding arbitrary novelty.
- **Consumes:** `token.universe` and `identity.thesis`.
- **Action:** Check `assets/exploration-strategy-catalog.json` in its fixed order; create one candidate for each applicable strategy; run its gates; keep at least two tokens from two strategies; record why any strategy does not apply.
- **Produces:** `exploration.ledger` with each candidate, evidence, reason, hypothesis, context, status, boundary, and path.
- **PASS when:** Every strategy has a disposition and sourced candidates meet the minimum.
- **BLOCKED when:** A strategy lacks a reason, the minimum is missing, or a candidate is filler; set `E_EVIDENCE`.
- **Recovery:** Revisit the thesis or universe, create only supported candidates, and rerun Step 08.
