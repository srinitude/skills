# Execution: review and completion

Run Steps 18 through 25 in order. Use the exact fields defined in `references/execution-guide.md` and the handoffs in `assets/execution-io-map.json`.

## Step 18: Inspect final HTML

- **Purpose:** Judge the assembled pixels and interactions, not source code or a pre-assembly candidate.
- **Consumes:** `artifact.proof`, `proof.coverage-map`, `source.payload`, and `vision.execution`.
- **Action:** The vision executor must use `references/visual-review.md` to inspect wide, narrow, whole-frame, detail, every applicable state, mode, motion, input, data condition, permutation, and corpus comparison after assembly. For a pending artifact, record the assembler's `reviewed_surface_sha256` only after this pass; after recorded-pass assembly, inspect the exact final HTML again and defer its full byte hash to Step 23.
- **Produces:** `review.visual` with viewport, state, region, observation, countercheck, status, and repair.
- **PASS when:** Every required surface has located final-pixel evidence on the final proof hash.
- **BLOCKED when:** A required surface, state, or viewport is unseen; set `E_REVIEW`.
- **Recovery:** Render and inspect the missing condition, then rerun Step 18 for the full surface set.

## Step 19: Resolve defects

- **Purpose:** Reject harmful output such as overlap, clipping, illegibility, broken response, and false proof cues.
- **Consumes:** `review.visual` and `artifact.proof`.
- **Action:** Check every marker in `assets/visual-defect-catalog.json`; measure when possible; inspect overlap, clipping, typography, contrast, geometry, interaction, response, content, and proof integrity; record new harm as an unknown marker before deciding it.
- **Produces:** `review.defects` with marker IDs, findings, severity, repairs, reruns, and final status.
- **PASS when:** Every marker has one disposition and zero veto or major defects remain.
- **BLOCKED when:** A veto, major defect, or applicable marker remains unresolved; set `E_REVIEW`.
- **Recovery:** Fix the earliest visual or token cause, rebuild the proof, and rerun Steps 17 through 19.

## Step 20: Resolve invariants

- **Purpose:** Protect minimum perceptual and motor needs while allowing supported creative exceptions and unused experiments.
- **Consumes:** `review.defects`, `artifact.tokens`, and `artifact.proof`.
- **Action:** Test every entry in `assets/perceptual-motor-invariant-catalog.json` in token feasibility and rendered use; record pass or reasoned exception; use the creative exception protocol without imposing a house style; include touch targets when touch applies.
- **Produces:** `review.invariants` with invariant ID, evidence, state, status, gain, cost, counterevidence, and claim boundary.
- **PASS when:** Every invariant appears once and no claimed use fails.
- **BLOCKED when:** An applicable invariant is missing, a claimed use fails, or an exception lacks evidence; set `E_REVIEW`.
- **Recovery:** Fix the failing use or remove its claim while keeping unused experiments, then rerun Step 20.

## Step 21: Judge four tracks

- **Purpose:** Keep taste, originality, corpus uniqueness, and non-AI-slop as separate claims.
- **Consumes:** `review.invariants`, `review.defects`, `artifact.proof`, `source.payload`, and `signature.decisions`.
- **Action:** Use `assets/judgment-review-catalog.json` and `references/qualitative-judgment.md`; start with all lenses, narrow to those that apply, add new lenses, keep competing readings, cite regions, compare alternatives and corpus neighbors, and record counterevidence; use `examples/failure-global-claim.md` for absolute uniqueness requests; never infer authorship from appearance.
- **Produces:** `review.judgment` with separate taste, originality, corpus-uniqueness, and non-AI-slop records, each with uncertainty and limits.
- **PASS when:** All four tracks pass within scope and `globally_unique` remains false.
- **BLOCKED when:** A track fails, lacks located evidence, exceeds its corpus, or claims authorship from appearance; set `E_REVIEW` or `E_CLAIM`.
- **Recovery:** Fix the cited source, token, or proof cause, expand only an authorized corpus, and rerun the affected track and dependents.

## Step 22: Repair causes

- **Purpose:** Fix the earliest cause of failure instead of changing the latest artifact or verdict alone.
- **Consumes:** `review.judgment`, `review.invariants`, `review.defects`, and all earlier failed gates.
- **Action:** Follow `references/deterministic-execution.md`; find the earliest causal source, token relation, record, or proof region; fix it; set that step and all dependents to `RUNNING`; rerun them; stop after three failed attempts at the same cause.
- **Produces:** `repair.result` with attempt number, cause, change, rerun set, fresh checks, and outcome.
- **PASS when:** The cause and every dependent gate pass on current inputs, bytes, and pixels.
- **BLOCKED when:** Three repair attempts at the same cause fail or required evidence or capability is missing; keep the original error.
- **Recovery:** Name the exact missing evidence or capability and wait for it; never change only the verdict to `PASS`.

## Step 23: Read back final bytes

- **Purpose:** Confirm that all four deliverables, visible proof, embedded records, reviews, and claims agree after repairs.
- **Consumes:** `repair.result`, `artifact.tokens`, `artifact.evidence`, `artifact.proof`, and `run.contract`.
- **Action:** Apply `references/evidence-schema.md`; rehash all four deliverables; reopen the recorded-pass HTML; visually inspect its exact final pixels; compare the visible verdict, embedded records, run ID, viewports, coverage, claims, and limits; store the full HTML byte hash in `<name>.run.json`; build the completion matrix from current bytes; do not reassemble after this readback.
- **Produces:** `final.readback` with hashes, locators, review time, and a criterion-to-evidence map.
- **PASS when:** Every artifact and claim agrees after final assembly and each completion criterion has current evidence.
- **BLOCKED when:** A hash, identifier, verdict, coverage record, claim, or limit differs; set the first matching `E_ASSEMBLY`, `E_REVIEW`, or `E_CLAIM`.
- **Recovery:** Fix the earliest mismatch and rerun that step and every dependent step through Step 23.

## Step 24: Validate the package

- **Purpose:** Prove that the current skill package, contracts, examples, and checks still agree.
- **Consumes:** `final.readback` and the current package tree.
- **Action:** Read `references/generation-contract.md`, `references/decisions.md`, `references/validation.md`, `evals/contract.md`, and `evals/rubric.md`; run `mise run ci`, or every listed direct check if unavailable; include `scripts/tests/test_ci_contract.py`; parse every JSON file; confirm removed visual generators remain absent.
- **Produces:** `package.validation` with commands, exits, outputs, skill hash, and checked paths.
- **PASS when:** Every current-byte check exits 0 and the recorded skill hash matches the checked tree.
- **BLOCKED when:** A required check fails, is skipped, or uses older bytes; do not claim package health.
- **Recovery:** Fix the failing package owner, rerun its focused check, then rerun the full Step 24 gate.

## Step 25: Return proved results

- **Purpose:** Return only claims proved by the full pipeline and make failures and limits visible.
- **Consumes:** `package.validation`, `final.readback`, `run.contract`, and all 25 step records.
- **Action:** Follow `references/deterministic-execution.md`; check every `SKILL.md` Completion gate; return artifact paths, hashes, counts, universe and context coverage, corpus scope, visual review coverage, command exits, failed gates, and limits; never report one deliverable as the whole result.
- **Produces:** `completion.disposition` with final status, artifacts, criterion map, failed gates, and recovery needs.
- **PASS when:** All 25 step records and every Completion gate are `PASS` on current inputs and final bytes, and every claim has artifact, command, or located visual evidence.
- **BLOCKED when:** Any step or Completion gate is unproved; return its ID and recovery need while withholding non-slop, originality, corpus uniqueness, and completion claims.
- **Recovery:** Resume at the earliest failed step, rerun all dependents, rebuild the disposition, and return only after a fresh Step 25 check.
