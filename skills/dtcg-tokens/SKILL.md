---
name: dtcg-tokens
description: 'Use when any multimodal source must become source-specific DTCG tokens with a vision-reviewed standalone proof artifact.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.2.1'
---

# dtcg-tokens

Turn any inspectable multimodal input into source-specific DTCG 2025.10 JSON, evidence JSON, a standalone HTML proof artifact, and a run record. Start with the full possibility surface, then narrow it with source evidence and reasons. Strong native vision owns source interpretation, design decisions, artifact authorship, and final visual judgment. Never invent a source, audience, product fact, brand premise, comparison corpus, or proof claim.

## Commands

| Command                               | Result                                                                                           |
| ------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `help`                                | Show inputs, intents, outputs, vision requirements, and claim limits.                            |
| `generate <inputs>`                   | Create `<name>.tokens.json`, `<name>.evidence.json`, `<name>.proof.html`, and `<name>.run.json`. |
| `validate <tokens>`                   | Check DTCG 2025.10 structure, values, names, references, type agreement, and cycles.             |
| `prove <tokens> <evidence> [sources]` | Author, assemble, inspect, and read back a source- and token-specific standalone proof artifact. |

Load `examples/help.md`, `examples/generate.md`, `examples/validate.md`, or `examples/prove.md` only when the matching command needs a worked run. Load `examples/failure-global-claim.md` when absolute uniqueness is requested. Load `evals/contract.md`, `evals/rubric.md`, and `scripts/tests/test_ci_contract.py` only in Step 24.

## Operating contract

Fix the process, not the design. Keep step order, named handoffs, evidence, states, gates, and claim limits deterministic. Keep source types, intents, extensions, token content, visual language, specimens, interactions, qualitative lenses, and experiments open. Use `references/extension-protocol.md` whenever the input needs something a catalog does not name.

## Execution

`generate` and `prove` run all 25 steps in order and may claim completion only after every gate passes. `help` returns the command contract without creating artifacts. `validate` runs the bounded conformance diagnostic and cannot claim token quality, proof quality, or skill completion. Before each pipeline step, open its linked section in `references/execution-guide.md` and every support file named there. Use `assets/execution-io-map.json` for exact inputs and outputs, `assets/execution-step-contract.json` for records and state, and `references/deterministic-execution.md` for retries and dependent reruns. A step may start only after all named inputs exist and the preceding step is `PASS`. Save its named output before continuing. No deliverable alone completes the skill. Do not stop after creating, validating, or reviewing one file.

| #   | Step                                                                                            | Start with                   | Do and save                                           | Gate                                                                                              |
| --- | ----------------------------------------------------------------------------------------------- | ---------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| 01  | [Freeze the run](references/execution-intake.md#step-01-freeze-the-run)                         | Request and source payloads. | Freeze scope as `run.contract`.                       | PASS: all fields exist. BLOCKED: `E_INPUT` for missing task material.                             |
| 02  | [Inventory input and intent](references/execution-intake.md#step-02-inventory-input-and-intent) | `run.contract`.              | Account for every source as `source.inventory`.       | PASS: both inventories are exact. BLOCKED: `E_INPUT` for inaccessible material.                   |
| 03  | [Prove vision execution](references/execution-intake.md#step-03-prove-vision-execution)         | `source.inventory`.          | Prove the vision path as `vision.execution`.          | PASS: one strong vision path owns all judgment. BLOCKED: `E_VISION`.                              |
| 04  | [Observe visuals](references/execution-intake.md#step-04-observe-visuals)                       | `vision.execution`.          | Save located facts as `observation.register`.         | PASS: every fact is located. BLOCKED: `E_EVIDENCE` for unseen facts.                              |
| 05  | [Classify statements](references/execution-intake.md#step-05-classify-statements)               | `observation.register`.      | Save each basis as `statement.register`.              | PASS: every statement has one basis. BLOCKED: `E_INPUT` for an unbounded unknown.                 |
| 06  | [Falsify the thesis](references/execution-intake.md#step-06-falsify-the-thesis)                 | `statement.register`.        | Test and save `identity.thesis`.                      | PASS: unrelated substitutions fail. BLOCKED: `E_EVIDENCE` for a generic thesis.                   |
| 07  | [Expand the token universe](references/execution-intake.md#step-07-expand-the-token-universe)   | `identity.thesis`.           | Save the full pre-narrowing `token.universe`.         | PASS: every possibility is accounted for. BLOCKED: `E_EVIDENCE` for gaps or duplicates.           |
| 08  | [Generate experiments](references/execution-intake.md#step-08-generate-experiments)             | `token.universe`.            | Test and save `exploration.ledger`.                   | PASS: all strategies and minimums resolve. BLOCKED: `E_EVIDENCE` for gaps or filler.              |
| 09  | [Map contexts](references/execution-build.md#step-09-map-contexts)                              | `exploration.ledger`.        | Save every relationship as `context.matrix`.          | PASS: every requirement has a disposition. BLOCKED: `E_EVIDENCE` for an unmapped item.            |
| 10  | [Create signatures](references/execution-build.md#step-10-create-signatures)                    | `context.matrix`.            | Save sourced cross-axis `signature.decisions`.        | PASS: five decisions across three axes trace to renders. BLOCKED: `E_EVIDENCE`.                   |
| 11  | [Author tokens](references/execution-build.md#step-11-author-tokens)                            | `signature.decisions`.       | Write and hash `artifact.tokens`.                     | PASS: retained paths match exactly. BLOCKED: `E_DTCG` for an untruthful representation.           |
| 12  | [Validate tokens](references/execution-build.md#step-12-validate-tokens)                        | `artifact.tokens`.           | Run the checker and save `validation.dtcg`.           | PASS: exit 0 and `valid: true`. BLOCKED: `E_DTCG` for any current-byte error.                     |
| 13  | [Build evidence](references/execution-build.md#step-13-build-evidence)                          | `validation.dtcg`.           | Join prior records as `artifact.evidence`.            | PASS: all IDs, hashes, and claims agree. BLOCKED: `E_EVIDENCE` for gaps or contradictions.        |
| 14  | [Author proof](references/execution-build.md#step-14-author-proof)                              | `artifact.evidence`.         | Vision-author and map `proof.candidate`.              | PASS: every obligation has a source-specific region. BLOCKED: `E_VISION` or `E_ASSEMBLY`.         |
| 15  | [Reject reused shells](references/execution-build.md#step-15-reject-reused-shells)              | `proof.candidate`.           | Compare, repair, and save `proof.originality-review`. | PASS: no generic shell survives. BLOCKED: `E_REVIEW` for reuse.                                   |
| 16  | [Expose coverage](references/execution-build.md#step-16-expose-coverage)                        | `proof.originality-review`.  | Map every visible specimen as `proof.coverage-map`.   | PASS: token, permutation, experiment, and region sets match. BLOCKED: `E_ASSEMBLY`.               |
| 17  | [Assemble proof](references/execution-build.md#step-17-assemble-proof)                          | `proof.coverage-map`.        | Assemble and hash `artifact.proof`.                   | PASS: one intact self-contained HTML exits 0. BLOCKED: `E_ASSEMBLY`.                              |
| 18  | [Inspect final HTML](references/execution-review.md#step-18-inspect-final-html)                 | `artifact.proof`.            | Inspect final pixels as `review.visual`.              | PASS: every required surface is seen. BLOCKED: `E_REVIEW` for missing readback.                   |
| 19  | [Resolve defects](references/execution-review.md#step-19-resolve-defects)                       | `review.visual`.             | Resolve every marker in `review.defects`.             | PASS: zero unresolved vetoes or major defects. BLOCKED: `E_REVIEW`.                               |
| 20  | [Resolve invariants](references/execution-review.md#step-20-resolve-invariants)                 | `review.defects`.            | Resolve every invariant in `review.invariants`.       | PASS: no claimed use fails. BLOCKED: `E_REVIEW` for a missing or failed invariant.                |
| 21  | [Judge four tracks](references/execution-review.md#step-21-judge-four-tracks)                   | `review.invariants`.         | Save separate claims as `review.judgment`.            | PASS: all scoped tracks pass and global uniqueness stays false. BLOCKED: `E_REVIEW` or `E_CLAIM`. |
| 22  | [Repair causes](references/execution-review.md#step-22-repair-causes)                           | `review.judgment`.           | Repair the earliest cause as `repair.result`.         | PASS: cause and dependents pass. BLOCKED: three failed attempts or a missing capability.          |
| 23  | [Read back final bytes](references/execution-review.md#step-23-read-back-final-bytes)           | `repair.result`.             | Reconcile all current bytes as `final.readback`.      | PASS: artifacts and claims agree. BLOCKED: the first matching assembly, review, or claim code.    |
| 24  | [Validate the package](references/execution-review.md#step-24-validate-the-package)             | `final.readback`.            | Run current-tree checks as `package.validation`.      | PASS: every required check exits 0. BLOCKED: any failed, skipped, or stale check.                 |
| 25  | [Return proved results](references/execution-review.md#step-25-return-proved-results)           | `package.validation`.        | Save and return `completion.disposition`.             | PASS: all steps and Completion gates pass. BLOCKED: return exact failed gates and recovery.       |

## Boundaries

- Token count is not quality evidence. Unsupported tokens count against the result.
- Keep conformance, source specificity, taste, originality, corpus uniqueness, non-AI-slop, invariants, and artifact integrity as separate claims.
- Token JSON cannot prove rendered quality. Machine checks cannot certify pixels. Vision cannot override measured failures.
- Experimental tokens may remain without a passing use claim. The proof must expose failures and limits as clearly as passes.
- Never claim global uniqueness without an exhaustive comparison corpus.

## Completion

- **Pipeline:** All 25 records required by `assets/execution-step-contract.json` are `PASS`, and every handoff in `assets/execution-io-map.json` resolves on current inputs and final bytes.
- **Deliverables:** `<name>.tokens.json`, `<name>.evidence.json`, `<name>.proof.html`, and `<name>.run.json` exist, are readable, and agree on hashes and run identity under `references/evidence-schema.md`.
- **Conformance:** `python3 scripts/validate_dtcg.py <tokens>` returns exit 0 with no unresolved name, metadata, value, type, alias, JSON Pointer, group-extension, reference, or cycle error and reports the pinned hash of `assets/dtcg-format-2025.10.schema.json`.
- **Accounting:** The records defined by `assets/multimodal-input-catalog.json` and `assets/token-possibility-catalog.json` account for every input, intent, catalog leaf, context requirement, applicable permutation, extension, exclusion, and retained token path exactly once.
- **Exploration:** At least two experimental tokens from at least two distinct strategies in `assets/exploration-strategy-catalog.json` have exact token, ledger, evidence, specimen, and final-review path agreement.
- **Specificity:** At least five source-derived signature decisions across at least three applicable axes pass `references/originality-rubric.md` and trace to sources, tokens, and rendered regions.
- **Proof coverage:** Every applicable token type, context permutation, and experimental token has a meaning-specific visible specimen that satisfies `scripts/lib/artifact_contract.py`; embedded raw JSON alone does not pass.
- **Visual readback:** The final assembled artifact passes the wide, narrow, whole-frame, detail, state, mode, motion, input, and data checks in `references/visual-review.md`, and review occurs after final assembly.
- **Defects and invariants:** Every entry in `assets/visual-defect-catalog.json` and `assets/perceptual-motor-invariant-catalog.json` is resolved exactly once, with zero unresolved vetoes, zero unresolved major defects, and no failed claimed invariant.
- **Judgment and claims:** Every track in `assets/judgment-review-catalog.json` and every applicable or emergent lens in `references/qualitative-judgment.md` is resolved with located evidence, counterevidence, uncertainty, competing readings, and limits; the corpus is named; claims match reviews; and `globally_unique` remains false.
- **Package health:** A fresh `mise run ci` returns exit 0 under `references/validation.md`, and the reported output belongs to the current skill bytes.

If any gate fails or lacks evidence, follow `references/deterministic-execution.md`: return `BLOCKED`, name each failed gate and its exact evidence or capability gap, and do not claim non-slop, originality, corpus uniqueness, or completion.
