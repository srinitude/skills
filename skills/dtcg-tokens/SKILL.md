---
name: dtcg-tokens
description: 'Use when any multimodal source must become source-specific DTCG tokens with a vision-reviewed standalone proof artifact.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.2.2'
---

# dtcg-tokens

Turn any inspectable multimodal input into source-specific DTCG 2025.10 JSON, evidence JSON, a standalone HTML proof artifact, and a run record. Start with the full possibility surface, then narrow it with located source evidence and reasons. Strong native vision owns source interpretation, design decisions, artifact authorship, and final visual judgment. Never invent a source, audience, product fact, brand premise, comparison corpus, or proof claim.

## Commands

| Command                               | Result                                                                                           |
| ------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `help`                                | Show inputs, intents, outputs, vision requirements, and claim limits.                            |
| `generate <inputs>`                   | Create `<name>.tokens.json`, `<name>.evidence.json`, `<name>.proof.html`, and `<name>.run.json`. |
| `validate <tokens>`                   | Check DTCG 2025.10 structure, values, names, references, type agreement, and cycles.             |
| `prove <tokens> <evidence> [sources]` | Author, assemble, inspect, and read back a source- and token-specific standalone proof artifact. |

Load `examples/help.md`, `examples/generate.md`, `examples/validate.md`, or `examples/prove.md` only for the matching command. Load `examples/failure-global-claim.md` only for an absolute uniqueness request. Load `evals/contract.md`, `evals/rubric.md`, and `scripts/tests/test_ci_contract.py` only in Step 24.

## Package map

A directory name does not load a file. Load, inspect, copy, or run a file only when the current command, Execution row, step procedure, or Completion gate names its exact relative path.

| Path                         | Contains                                                                                                                                   | Load or run when                                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| `references/`                | Plain-language procedures, rules, decision guides, and review methods.                                                                     | Read only the exact Markdown file routed by the current step or gate.                                              |
| `assets/`                    | Machine-readable schemas, catalogs, contracts, policies, manifests, templates, and static fixtures.                                        | Inspect the named asset when a procedure or script consumes it; never treat the directory as instruction text.     |
| `assets/exploration-corpus/` | Versioned creative primitives, operators, mechanisms, concepts, themes, constraints, questions, technology records, and negative patterns. | Load through its manifest only during the exploration step or its validation.                                      |
| `scripts/`                   | Deterministic command-line scaffolds, preparers, assemblers, validators, linters, and audits.                                              | Run the exact script named by the current step or gate; read its code only to repair or audit it.                  |
| `scripts/lib/`               | Import-only helpers for DTCG rules, accounting, coverage, artifact checks, review, fonts, experiments, and pipeline state.                 | Load only through the script that imports the named helper; never run a library file as a command.                 |
| `scripts/tests/`             | Discovered unit and contract tests for script and package behavior.                                                                        | Run through `mise run test`; inspect a named test only during Step 24 or a focused repair.                         |
| `evals/`                     | Trigger, behavior, failure, recovery, lineage, mapping, contract, and rubric records.                                                      | Load only the named eval file during Step 24 or a targeted evaluation.                                             |
| `evals/files/`               | Bounded token, evidence, source, and negative visual fixtures used by named evals or tests.                                                | Load only the fixture named by its eval, mapping, or test; never treat a rejected fixture as a positive precedent. |
| `examples/`                  | Verified worked command runs and one bounded failure example.                                                                              | Read only the example that matches the active command or failure.                                                  |
| `mise.toml`                  | The local task graph and the single full-check entry point.                                                                                | Run or inspect it in Step 24 and package maintenance.                                                              |
| `.github/workflows/`         | Remote checks that call the same local task entry point.                                                                                   | Inspect only when auditing remote validation or repository integration.                                            |

## Operating contract

Fix the process, not the design. Keep step order, named handoffs, evidence, states, gates, and claim limits deterministic. Keep source types, intents, extensions, token content, visual language, specimens, interactions, qualitative lenses, and experiments open. Use `references/extension-protocol.md` whenever a catalog omits a supported input or idea. For typography, follow `references/google-font-selection.md` and run `scripts/prepare_google_fonts.py`; each selected family must rank outside the most popular 50% of the same-date live Google Fonts catalog and pass source-specific vision review.

Push every mechanical action into `scripts/` when it can be defined by inputs, outputs, schemas, hashes, state transitions, comparisons, counts, or exit codes. Scripts scaffold judgment; they never make the judgment. Use `scripts/run_pipeline.py` to initialize the run, hash inputs, prepare each step packet, enforce prerequisites, record outputs, and set `PASS` or `BLOCKED`. A strong vision-capable model must own every visual or qualitative decision. If the active executor lacks strong vision, delegate every judgment and do not generate tokens or proof until that route passes `references/vision-execution.md`.

## Execution

`generate` and `prove` run all 25 steps in order. `help` returns the command contract without creating artifacts. `validate` runs only the bounded conformance check and cannot claim token or proof quality. Before every pipeline step, run `scripts/run_pipeline.py packet` and `scripts/run_pipeline.py start`; after saving every named output, run its `pass` or `block` command. Use `assets/execution-io-map.json` for exact inputs, outputs, support files, and decision owner; use `assets/execution-step-contract.json` for fields, states, and errors; use `references/deterministic-execution.md` for reruns. Every linked procedure defines `Input`, `Action`, `Save`, `Pass`, `Blocked`, and `Feeds` on separate lines. No deliverable alone completes the skill, and no command may skip a retained gate.

| #   | Step                                                                                            | Use                                                            | Produces                   |
| --- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | -------------------------- |
| 01  | [Freeze the run](references/execution-intake.md#step-01-freeze-the-run)                         | `scripts/run_pipeline.py` and `references/execution-intake.md` | `run.contract`             |
| 02  | [Inventory input and intent](references/execution-intake.md#step-02-inventory-input-and-intent) | `scripts/run_pipeline.py` and `references/execution-intake.md` | `source.inventory`         |
| 03  | [Prove vision execution](references/execution-intake.md#step-03-prove-vision-execution)         | `scripts/run_pipeline.py` and `references/execution-intake.md` | `vision.execution`         |
| 04  | [Observe visuals](references/execution-intake.md#step-04-observe-visuals)                       | `scripts/run_pipeline.py` and `references/execution-intake.md` | `observation.register`     |
| 05  | [Classify statements](references/execution-intake.md#step-05-classify-statements)               | `scripts/run_pipeline.py` and `references/execution-intake.md` | `statement.register`       |
| 06  | [Falsify the thesis](references/execution-intake.md#step-06-falsify-the-thesis)                 | `scripts/run_pipeline.py` and `references/execution-intake.md` | `identity.thesis`          |
| 07  | [Expand the token universe](references/execution-intake.md#step-07-expand-the-token-universe)   | `scripts/run_pipeline.py` and `references/execution-intake.md` | `token.universe`           |
| 08  | [Generate experiments](references/execution-intake.md#step-08-generate-experiments)             | `scripts/run_pipeline.py` and `references/execution-intake.md` | `exploration.ledger`       |
| 09  | [Map contexts](references/execution-build.md#step-09-map-contexts)                              | `scripts/run_pipeline.py` and `references/execution-build.md`  | `context.matrix`           |
| 10  | [Create signatures](references/execution-build.md#step-10-create-signatures)                    | `scripts/run_pipeline.py` and `references/execution-build.md`  | `signature.decisions`      |
| 11  | [Author tokens](references/execution-build.md#step-11-author-tokens)                            | `scripts/run_pipeline.py` and `references/execution-build.md`  | `artifact.tokens`          |
| 12  | [Validate tokens](references/execution-build.md#step-12-validate-tokens)                        | `scripts/run_pipeline.py` and `references/execution-build.md`  | `validation.dtcg`          |
| 13  | [Build evidence](references/execution-build.md#step-13-build-evidence)                          | `scripts/run_pipeline.py` and `references/execution-build.md`  | `artifact.evidence`        |
| 14  | [Author proof](references/execution-build.md#step-14-author-proof)                              | `scripts/run_pipeline.py` and `references/execution-build.md`  | `proof.candidate`          |
| 15  | [Reject reused shells](references/execution-build.md#step-15-reject-reused-shells)              | `scripts/run_pipeline.py` and `references/execution-build.md`  | `proof.originality-review` |
| 16  | [Expose coverage](references/execution-build.md#step-16-expose-coverage)                        | `scripts/run_pipeline.py` and `references/execution-build.md`  | `proof.coverage-map`       |
| 17  | [Assemble proof](references/execution-build.md#step-17-assemble-proof)                          | `scripts/run_pipeline.py` and `references/execution-build.md`  | `artifact.proof`           |
| 18  | [Inspect final HTML](references/execution-review.md#step-18-inspect-final-html)                 | `scripts/run_pipeline.py` and `references/execution-review.md` | `review.visual`            |
| 19  | [Resolve defects](references/execution-review.md#step-19-resolve-defects)                       | `scripts/run_pipeline.py` and `references/execution-review.md` | `review.defects`           |
| 20  | [Resolve invariants](references/execution-review.md#step-20-resolve-invariants)                 | `scripts/run_pipeline.py` and `references/execution-review.md` | `review.invariants`        |
| 21  | [Judge four tracks](references/execution-review.md#step-21-judge-four-tracks)                   | `scripts/run_pipeline.py` and `references/execution-review.md` | `review.judgment`          |
| 22  | [Repair causes](references/execution-review.md#step-22-repair-causes)                           | `scripts/run_pipeline.py` and `references/execution-review.md` | `repair.result`            |
| 23  | [Read back final bytes](references/execution-review.md#step-23-read-back-final-bytes)           | `scripts/run_pipeline.py` and `references/execution-review.md` | `final.readback`           |
| 24  | [Validate the package](references/execution-review.md#step-24-validate-the-package)             | `scripts/run_pipeline.py` and `references/execution-review.md` | `package.validation`       |
| 25  | [Return proved results](references/execution-review.md#step-25-return-proved-results)           | `scripts/run_pipeline.py` and `references/execution-review.md` | `completion.disposition`   |

## Boundaries

- Token count is not quality evidence. Unsupported tokens count against the result.
- Keep conformance, source specificity, taste, originality, corpus uniqueness, non-AI-slop, invariants, and artifact integrity as separate claims.
- Token JSON cannot prove rendered quality. Machine checks cannot certify pixels. Vision cannot override measured failures.
- Experimental tokens may remain without a passing use claim. The proof must expose failures and limits as clearly as passes.
- Use `references/qualitative-judgment.md` for taste, originality, corpus uniqueness, and non-AI-slop judgment; keep its interpretation flexible and its evidence requirements fixed.
- Global uniqueness is outside this skill's valid claim scope and remains unproved.

## Completion

| Gate                   | Done only when                                                                                                                                                                                                                 | Check with                                  |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------- |
| Pipeline               | All 25 current step records are `PASS`; every named input, output, support file, predecessor, and hash resolves.                                                                                                               | `scripts/run_pipeline.py`                   |
| Deliverables           | `<name>.tokens.json`, `<name>.evidence.json`, `<name>.proof.html`, and `<name>.run.json` exist, parse or render, and agree on run identity and hashes.                                                                         | `references/evidence-schema.md`             |
| Conformance            | `tokens.json` passes DTCG 2025.10 on current bytes with exit 0 and no unresolved value, type, name, alias, pointer, reference, or cycle error.                                                                                 | `scripts/validate_dtcg.py`                  |
| Accounting             | Every source, intent, catalog leaf, screen possibility, context cell, extension, exclusion, and retained token path appears exactly once.                                                                                      | `scripts/lib/accounting.py`                 |
| Exploration            | At least three retained experimental tokens use at least three distinct strategies, include inversion or antithesis, and agree across tokens, evidence, specimens, and final review.                                           | `scripts/validate_exploration.py`           |
| Specificity            | At least five source-derived signature decisions across at least three applicable axes trace from located source evidence to token paths and rendered regions.                                                                 | `assets/originality-analysis-contract.json` |
| Typography             | Same-date live Google Fonts research yields at least three eligible candidates, each selection ranks outside the most popular 50%, embedded WOFF2 and license hashes match, offline rendering works, and vision review passes. | `scripts/prepare_google_fonts.py`           |
| Proof coverage         | Every applicable token type, context permutation, and experimental token has a meaning-specific visible specimen; raw JSON alone does not pass.                                                                                | `scripts/lib/artifact_contract.py`          |
| Visual readback        | The final assembled `proof.html` is inspected with strong vision across wide, narrow, whole-frame, detail, state, mode, motion, input, and data conditions.                                                                    | `assets/vision-probe-manifest.json`         |
| Defects and invariants | Every defect and invariant has one disposition, with zero unresolved vetoes, zero unresolved major defects, and no failed claimed invariant.                                                                                   | `scripts/lib/review.py`                     |
| Judgment and claims    | Taste, originality, corpus uniqueness, and non-AI-slop are judged separately with located evidence, counterevidence, uncertainty, competing readings, and limits; `globally_unique` remains false.                             | `assets/judgment-review-catalog.json`       |
| Package health         | Every persistent file has a named activation or consumer route, every required check uses current bytes, and fresh `mise run ci` returns exit 0.                                                                               | `scripts/audit_file_triggers.py`            |

If any gate fails or lacks evidence, use `scripts/run_pipeline.py block` under `references/deterministic-execution.md`; return `BLOCKED`, name each failed gate and exact recovery need, and withhold non-slop, originality, corpus uniqueness, and completion claims.
