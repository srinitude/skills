# Execution: intake and discovery

Run Steps 01 through 08 in order. Use the command table in `references/execution-guide.md`. `assets/execution-io-map.json` owns each step packet and `scripts/run_pipeline.py` owns run state, hashes, and handoffs.

## Step 01: Freeze the run

**Input**
The user request as `request.packet`, every authorized source as `source.payload`, and one fresh clock record from `scripts/current_anchor.py`.

**Action**
Read `references/deterministic-execution.md`, `references/subagent-orchestration.md`, and `assets/subagent-task-contract.json`. Freeze the command, scope, source order, outputs, acceptance gates, claim limits, owner map, parallel work, dependencies, and retry rule. Use `scripts/run_pipeline.py init`, then create and start the S01 packet.

**Save**
Save `run.contract` as `<name>.records/S01-run.contract.json` and keep `<name>.run.json` as the runner-owned state record.

**Pass**
Every required field, source locator, owner, dependency, output, limit, and date is explicit. Use `scripts/run_pipeline.py pass` with `run.contract`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_INPUT` when task material, authority, source access, output scope, or an acceptance gate is missing. State exactly what must be supplied.

**Feeds**
Step 02 consumes `run.contract` and the same frozen `source.payload`.

## Step 02: Inventory input and intent

**Input**
`run.contract` and every frozen source in `source.payload`.

**Action**
Create and start the S02 packet with `scripts/run_pipeline.py`. Apply every format and intent facet in `assets/multimodal-input-catalog.json`, then use `references/multimodal-inspection.md` to record locator, access, channels, role, authority, influence, scope, conflict, and supported extension without mixing format with intent.

**Save**
Save `source.inventory` as `<name>.records/S02-source.inventory.json`, with one format record, one intent record, and stable-byte hash data for every source.

**Pass**
Every source appears exactly once in both inventories, and every influence claim names its authority and scope. Use `scripts/run_pipeline.py pass` with `source.inventory`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_INPUT` when a source cannot be accessed, hashed, or classified without guessing. Name the source and recovery action.

**Feeds**
Step 03 consumes `source.inventory` and `run.contract`.

## Step 03: Prove vision execution

**Input**
`source.inventory`, `run.contract`, and the source files they name.

**Action**
Create and start the S03 packet with `scripts/run_pipeline.py`. Run every probe in `assets/vision-probe-manifest.json` under `references/vision-execution.md`. Require direct whole-frame and detail inspection, located findings, comparison judgment, and rendered readback. If any probe fails, delegate every judgment through Step 23 to one strong vision-capable model while other executors remain mechanical.

**Save**
Save `vision.execution` as `<name>.records/S03-vision.execution.json`, including the executor, probe results, counterchecks, delegation boundary, and allowed mechanical work.

**Pass**
One strong vision executor owns source inspection, token decisions, proof authorship, and final visual review, and every probe passes. Use `scripts/run_pipeline.py pass` with `vision.execution`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_VISION` when no qualified vision executor can inspect both sources and final renders. Do not generate tokens or proof.

**Feeds**
Step 04 consumes `vision.execution`, `source.inventory`, and `source.payload`.

## Step 04: Observe visuals

**Input**
`vision.execution`, `source.inventory`, and every accessible source in `source.payload`.

**Action**
Create and start the S04 packet with `scripts/run_pipeline.py`. The strong vision executor applies `references/multimodal-inspection.md` and `references/multimodal-originality.md` at whole-frame, detail, sequence, comparison, and cross-source scales. Keep direct observation separate from OCR, measurements, inference, and taste.

**Save**
Save `observation.register` as `<name>.records/S04-observation.register.json`, with source ID, locator, region, observation, basis, confidence, counterevidence, and support for every material fact.

**Pass**
Every accessible visual and material source has all applicable passes, and every fact points to a location. Use `scripts/run_pipeline.py pass` with `observation.register`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_EVIDENCE` when a required surface is unseen or a fact lacks located evidence. Name the missing surface or unsupported fact.

**Feeds**
Step 05 consumes `observation.register` and `run.contract`.

## Step 05: Classify statements

**Input**
`observation.register`, `run.contract`, and every material clause from the frozen sources.

**Action**
Create and start the S05 packet with `scripts/run_pipeline.py`. Apply `references/evidence-schema.md` and `references/decisions.md`. Mark each statement `observed`, `inferred`, or `assumed`; link its evidence, confidence, limit, and affected output. Ask once only when an unknown would change the system.

**Save**
Save `statement.register` as `<name>.records/S05-statement.register.json` with one basis and one bounded influence record per statement.

**Pass**
Every material statement has one basis and no assumption is presented as observation. Use `scripts/run_pipeline.py pass` with `statement.register`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_INPUT` when an unbounded unknown can change token architecture or proof claims. Name the smallest fact needed.

**Feeds**
Step 06 consumes `statement.register` and `observation.register`.

## Step 06: Falsify the thesis

**Input**
`statement.register`, `observation.register`, audience evidence, and source constraints.

**Action**
Create and start the S06 packet with `scripts/run_pipeline.py`. The strong vision executor applies `assets/originality-analysis-contract.json`, `references/originality-rubric.md`, and `references/multimodal-originality.md`. Build a source identity graph, state the audience, use, intended feeling, and source-specific idea, then test unrelated-domain substitution, feature removal, nearest-neighbor similarity, and identifiability loss.

**Save**
Save `identity.thesis` as `<name>.records/S06-identity.thesis.json`, including identity claims, evidence IDs, substitutions, removals, nearest neighbors, failures, revisions, uncertainty, and claim limits.

**Pass**
Every clause is sourced, unrelated substitutions fail, removing signature relations reduces identifiability, and the thesis does not fit a generic neighbor unchanged. Use `scripts/run_pipeline.py pass` with `identity.thesis`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_EVIDENCE` when the thesis is generic, unsupported, portable, or not identifiable. Name the missing evidence or failed test.

**Feeds**
Step 07 consumes `identity.thesis` and `statement.register`.

## Step 07: Expand the token universe

**Input**
`identity.thesis` and `statement.register`.

**Action**
Create and start the S07 packet with `scripts/run_pipeline.py`. Enumerate every leaf in `assets/token-possibility-catalog.json` and every screen primitive, behavior, condition, medium, input, and physical effect in `assets/screen-possibility-space.json` before exclusion. Apply `references/dtcg-2025.10.md`, `references/category-taxonomy.md`, and `references/screen-decision.md`; add source- or intent-backed extensions with stable IDs.

**Save**
Save `token.universe` as `<name>.records/S07-token.universe.json`, with every catalog leaf, screen possibility, extension, and later exclusion represented exactly once.

**Pass**
Every base possibility appears exactly once, every extension cites a source or intent record, and nothing was removed before review. Use `scripts/run_pipeline.py pass` with `token.universe`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_EVIDENCE` when a leaf is missing, duplicated, or excluded before review. Name the exact ID.

**Feeds**
Step 08 consumes `token.universe` and `identity.thesis`.

## Step 08: Generate experiments

**Input**
`token.universe`, `identity.thesis`, current research records, and the exploration corpus named by `assets/exploration-corpus/manifest.json`.

**Action**
Create and start the S08 packet with `scripts/run_pipeline.py`. Run `scripts/prepare_creative_research.py` under `references/research-protocol.md`, then use `assets/creative-source-frontier.json`, every corpus shard, `references/creative-transfer.md`, `references/exploration-synthesis.md`, and `references/experimental-decision.md`. Produce at least 12 candidates across all four lanes in `assets/experiment-contract.json`, include at least one inversion or antithesis, and let the strong vision executor judge value after the broad search. Run `scripts/validate_exploration.py` before retention.

**Save**
Save `exploration.ledger` as `<name>.records/S08-exploration.ledger.json`, with sources, transfers, lanes, candidates, hypotheses, evidence, contexts, states, boundaries, rejections, and retained token paths.

**Pass**
Every frontier cell and corpus shard has a disposition; at least three supported tokens from at least three distinct strategies remain; inversion or antithesis is present; and no retained candidate is filler. Use `scripts/run_pipeline.py pass` with `exploration.ledger`.

**Blocked**
Use `scripts/run_pipeline.py block` with `E_EVIDENCE` when research is stale or untraceable, a lane is empty, fewer than 12 candidates exist, the retained minimum fails, or a candidate lacks a sourced reason. Name the failed contract field.

**Feeds**
Step 09 consumes `exploration.ledger`, `token.universe`, `statement.register`, and `observation.register`.
