---
name: dtcg-tokens
description: 'Use when any multimodal source must become source-specific DTCG tokens with a vision-reviewed standalone proof artifact.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.4.1'
---

# dtcg-tokens

## Outcome

Turn inspectable multimodal source evidence into source-specific DTCG 2025.10 JSON, evidence JSON, a standalone HTML proof artifact, and a run record. Start with the full token possibility surface, narrow it with located evidence and material experiments, and accept token values only after current rendered-pixel judgment. Never invent a source, audience, product fact, brand premise, comparison corpus, or proof claim.

## Motivation

A structurally valid token file can still be generic, misleading, inaccessible, mediocre, or visually poor. Deterministic Mise tasks own repeatable mechanics so strong native vision can concentrate on source interpretation, token relationships, creative experiments, human eye, brain, and touch judgment, and final visual acceptance.

## Commands

| Command | Result | Owning task |
| --- | --- | --- |
| `help` | Show inputs, intents, outputs, vision requirements, and claim limits. | `mise run token-help` |
| `generate <inputs>` | Produce `<name>.tokens.json`, `<name>.evidence.json`, `<name>.proof.html`, and `<name>.run.json`. | `mise run token-run -- <args>` |
| `validate <tokens>` | Check DTCG 2025.10 structure, values, names, references, type agreement, and cycles. | `mise run token-validate -- <tokens>` |
| `prove <tokens> <evidence> [sources]` | Assemble, inspect, and read back a source-specific standalone proof. | `mise run token-prove -- <args>` |

Load `examples/help.md`, `examples/generate.md`, `examples/validate.md`, or `examples/prove.md` only through the matching `mise run token-help`, `mise run token-run`, `mise run token-validate`, or `mise run token-prove` operation. Load `examples/failure-global-claim.md` through `mise run evals` only for an absolute uniqueness request.

For package maintenance, load `references/generation-contract.md` through `mise run validate`; load `references/resource-and-experiment-design.md` and `assets/improvement-contract.json` through `mise run improvement-policy`; load `references/use-case-specificity.md` and `assets/use-case-contract.json` through `mise run use-case-policy`; load `assets/invocation-receipt-template.json` through `mise run invocation-policy -- <receipt>`. If Mise is unavailable, return `BLOCKED`; never call a private implementation file directly.

## Package map

| Path | Contains | Load or run when |
| --- | --- | --- |
| `references/` | Conditional token procedures, decisions, and visual review methods. | Load the exact relative path returned by `mise run token-packet -- <args>`. |
| `assets/` | DTCG schemas, catalogs, policies, contracts, manifests, and fixtures. | Load an exact path from `mise run token-packet -- <args>` or its owning policy task. |
| `assets/exploration-corpus/` | Bounded exploration vocabulary and synthesis constraints. | Load through `mise run validate-exploration` or its packet. |
| `evals/` | Trigger, behavior, failure, recovery, lineage, and rubric records. | Load through `mise run evals` or the Step 24 packet. |
| `evals/files/` | Real token, evidence, brief, and manifest fixtures. | Read only through `mise run evals` or the owning validation or proof task. |
| `examples/` | Verified command examples and one bounded failure example. | Load through the matching public command task or `mise run evals`. |
| `mise.toml` | Sole task graph, cache policy, and dependency owners. | Run the public operation or package gate. |
| `.github/workflows/` | Remote CI route. | Remote CI invokes only `mise run ci`. |

A directory name does not load a file. Use the exact relative path returned by its owning Mise task and only for the active decision.

## Governing factory

Use current `skill-factory` update mode for every package change. Before writing, run its `mise run plan-standardize -- /absolute/path/to/dtcg-tokens`, save the baseline digest outside the package, and observe RED. Afterward run DTCG checks plus factory `mise run validate-target -- /absolute/path/to/dtcg-tokens`, `mise run eval-target -- /absolute/path/to/dtcg-tokens`, and `mise run invocation-policy -- <receipt>`. Run maintenance last. Missing receipts invalidate the update.

## Mise lifecycle contract

Before acceptance run `mise run domain-research-policy`, `mise run use-case-policy`, `mise run mise-primitives-policy`, `mise run primitive-lifecycle-policy`, `mise run task-graph-policy`, and `mise run decision-policy`. Map all domain actors, objects, actions, states, rules, variants, interfaces, authorities, failures, recoveries, evidence, time, resources, quality, terms, and exclusions. Map every skill body, reference, asset, implementation, test, Mise task, example, eval, policy, schema, and record across discovery through retirement.

Account for every task on one default path. Give each inapplicable task current token-specific proof and validate it with `mise run invocation-policy -- <receipt>`. Keep Mise fixed during outcome work. After acceptance run `mise run mise-primitives-update`, rerun `mise run ci`, and record version and catalog digest.

## Token-design contract

Keep order, evidence, state, gates, and claim limits deterministic. Keep sources, intent, token content, visual language, specimens, interactions, lenses, and material experiments open. Load `references/extension-protocol.md` through `mise run token-packet -- <args>` for omitted input types. Load `references/google-font-selection.md` through `mise run font-prepare -- <args>`; each family must rank outside the most popular 50% of the same-date Google Fonts catalog and pass vision review.

Optimize elapsed time after correctness, source coverage, creative range, and proof are fixed. Progress needs an owner change plus readback; plans, queued work, running commands, and unviewed output do not count. Batch independent work. Serialize writers and vision decisions.

Before a token or relationship passes, load `references/controlled-comparisons.md` through `mise run token-packet -- <args>`. Register materially different experiments before sight. Freeze conditions, hypothesis, null, measure, falsifier, and decision rule. Reject micro tuning unless requested or tied to a defect or required threshold. Use current eye, brain, and touch judgment to lock a winner before canonical authoring.

Give every retained primitive and relationship a focus-intent record with `user_task`, `focus_target`, `focus_location`, `focus_timing`, `focus_mechanism`, `focus_reason`, `attention_sequence`, `competing_signals`, `defocus_and_recovery`, and `failure_evidence`. Pixels must show the attention order. A token owns salience capacity, not product focus; it does not prove product-level focus success.

Treat portrait and landscape as separate mobile and tablet contexts. Prove both or justify non-use. Add an orientation relationship only if rotation changes reach, safe area, wrapping, density, spacing, or salience. Any change invalidates both.

For multipage design artifacts, record canonical destination and native ancestry. Wrong-page, duplicate, orphan, stale, or visually rejected placement is `BLOCKED`. Standalone generation needs no design app; Figma ownership stays with its lifecycle skill.

After measured gates, direct visual proof is the highest visual authority. The same strong vision-capable executor inspects current whole views and details across states, viewports, input paths, before and after each change and invalidation. Structure, metadata, metrics, hashes, unviewed captures, or another verdict cannot grant visual `PASS`. Missing sight is `BLOCKED`.

During a Computer Use audit in a design application, apply the paramount visual-proof rule before any item decision. The same invoking strong vision-capable executor must use every applicable available vision capability plus a platform-neutral local application-control capability to operate and directly inspect the active design application, including Figma, before and after each mutation. A Figma lifecycle audit also needs the Figma skill's current pass receipt and item-level source dispositions. If any required sight, state, or control route is unavailable, the item is `BLOCKED`. Outside that audit, this token skill works alone and must not require application control or product-only providers.

Keep each token canvas clean throughout mutation. Load `references/qualitative-judgment.md` through `mise run token-packet -- <args>` before writing. Inspect the whole canvas and active area; separate canonical, exploratory, rejected, and historical work. Expose overlap, clipping, stacking, residue, bad order, unreachable targets, and stale evidence. Cleanup may move, label, or quarantine, never erase proof without authority. Require before-and-after receipts.

Begin from zero trust. Mark inherited tokens, claims, evidence, specimens, and verdicts `STALE` until current proof earns `PASS`. Inspect first, retain passes, and do not change correct work for novelty. Bind outcomes to measures or direct judgment; never claim perfection.

Push every mechanical action into Mise-owned tasks. Mise tasks scaffold judgment; they never make the judgment. `mise run token-run -- <args>` creates 25 records; `mise run token-packet -- <args>`, `mise run token-start -- <args>`, `mise run token-pass -- <args>`, and `mise run token-block -- <args>` own transitions. A strong vision-capable model owns qualitative decisions. Without strong vision, delegate every judgment and do not generate tokens or proof until that route passes.

## Ordered workflow

1. **Freeze the token outcome.** Mise: run `mise run token-run -- <args>`. Model: bind the source, intent, audience, deliverables, exclusions, and proof limit. Branch: choose help, validate, generate, or prove from the request.
2. **Prove readiness and source authority.** Mise: run `mise run token-packet -- <args>`. Model: inspect current source evidence and classify every statement. If: a required source, authority, or vision route is missing, run `mise run token-block -- <args>` and stop that claim.
3. **Expand before narrowing.** Mise: run `mise run token-explore -- <args>`. Model: create materially different source-specific directions and disconfirm the leading thesis. For each: record every applicable token family, context, exclusion, and counterexample once.
4. **Run material experiments.** Mise: run `mise run validate-exploration`. Model: compare large alternatives under frozen conditions with direct eye, brain, and touch judgment. Repeat: return an unresolved factor to experimentation until one direction earns a lock or a real blocker stops the loop.
5. **Lock lower owners before higher use.** Mise: run `mise run token-pass -- <args>` only after the experiment receipt resolves. Model: lock accepted token primitives and relationships before authoring dependent atoms, molecules, organisms, templates, or screens. If: a lower owner changes, invalidate every dependent proof and return to its first affected step.
6. **Author and validate tokens.** Mise: run `mise run token-validate -- <tokens>`. Model: author only supported source-specific values and explain every omission, alias, relationship, and exception. If: conformance fails, repair the lowest token owner and rerun validation.
7. **Assemble and inspect proof.** Mise: run `mise run token-prove -- <args>`. Model: inspect current whole-view and readable-detail pixels across required states, modes, inputs, viewports, and orientations. For each: accept, reject, or block every visual claim with located evidence.
8. **Repair and integrate.** Mise: run `mise run ci`. Model: distinguish structural, source, visual, and interaction failures and repair the lowest owner. Repeat: rerun the affected task and integrated gate until both pass or the exact blocker is recorded.
9. **Return or restore.** Mise: run `mise run token-status -- <args>` and `mise run invocation-policy -- <receipt>`. Model: report deliverables, proof, uncertainty, and limits; retain an optional improvement only under the nonregression contract. Stop: finish at the first fully accepted state and restore the last accepted digest after any regression.

## Execution

`generate` and `prove` run all 25 steps in order. `help` creates nothing; `validate` proves conformance only. `mise run token-packet -- <args>` routes exact inputs, outputs, owners, states, and rerun rules through `assets/execution-io-map.json`, `assets/execution-step-contract.json`, and `references/deterministic-execution.md`. It routes Steps 01 to 08 through `references/execution-intake.md`, Steps 09 to 17 through `references/execution-build.md`, and Steps 18 to 25 through `references/execution-review.md`. Start with `mise run token-start -- <args>`; finish with `mise run token-pass -- <args>` or `mise run token-block -- <args>`. Step 12 uses `mise run token-validate -- <tokens>`, Step 17 uses `mise run token-prove -- <args>`, Step 24 uses `mise run ci`, and Step 25 uses `mise run token-status -- <args>`. No deliverable alone completes the skill.

| # | Step | Use | Produces |
| --- | --- | --- | --- |
| 01 | [Freeze](references/execution-intake.md#step-01-freeze-the-run) | `mise run token-run` | run |
| 02 | [Inventory](references/execution-intake.md#step-02-inventory-input-and-intent) | `mise run token-packet` | inventory |
| 03 | [Vision](references/execution-intake.md#step-03-prove-vision-execution) | `mise run token-packet` | vision |
| 04 | [Observe](references/execution-intake.md#step-04-observe-visuals) | `mise run token-packet` | observations |
| 05 | [Classify](references/execution-intake.md#step-05-classify-statements) | `mise run token-packet` | claims |
| 06 | [Falsify](references/execution-intake.md#step-06-falsify-the-thesis) | `mise run token-packet` | thesis |
| 07 | [Expand](references/execution-intake.md#step-07-expand-the-token-universe) | `mise run token-packet` | universe |
| 08 | [Experiment](references/execution-intake.md#step-08-generate-experiments) | `mise run token-packet` | trials |
| 09 | [Contexts](references/execution-build.md#step-09-map-contexts) | `mise run token-packet` | matrix |
| 10 | [Signatures](references/execution-build.md#step-10-create-signatures) | `mise run token-packet` | signatures |
| 11 | [Author](references/execution-build.md#step-11-author-tokens) | `mise run token-packet` | tokens |
| 12 | [Validate](references/execution-build.md#step-12-validate-tokens) | `mise run token-validate` | report |
| 13 | [Evidence](references/execution-build.md#step-13-build-evidence) | `mise run token-packet` | evidence |
| 14 | [Proof](references/execution-build.md#step-14-author-proof) | `mise run token-packet` | candidate |
| 15 | [Originality](references/execution-build.md#step-15-reject-reused-shells) | `mise run token-packet` | review |
| 16 | [Coverage](references/execution-build.md#step-16-expose-coverage) | `mise run token-packet` | coverage |
| 17 | [Assemble](references/execution-build.md#step-17-assemble-proof) | `mise run token-prove` | proof |
| 18 | [Inspect](references/execution-review.md#step-18-inspect-final-html) | `mise run token-packet` | visual |
| 19 | [Defects](references/execution-review.md#step-19-resolve-defects) | `mise run token-packet` | defects |
| 20 | [Invariants](references/execution-review.md#step-20-resolve-invariants) | `mise run token-packet` | invariants |
| 21 | [Judge](references/execution-review.md#step-21-judge-four-tracks) | `mise run token-packet` | judgment |
| 22 | [Repair](references/execution-review.md#step-22-repair-causes) | `mise run token-packet` | repair |
| 23 | [Readback](references/execution-review.md#step-23-read-back-final-bytes) | `mise run token-packet` | bytes |
| 24 | [Package](references/execution-review.md#step-24-validate-the-package) | `mise run ci` | validation |
| 25 | [Return](references/execution-review.md#step-25-return-proved-results) | `mise run token-status` | status |

## Boundaries

- Token count is not quality evidence. Unsupported tokens count against the result.
- Keep conformance, source specificity, taste, originality, corpus uniqueness, non-AI-slop, invariants, and proof integrity as separate claims.
- Token JSON cannot prove rendered quality. Machine checks cannot certify pixels. Vision cannot override measured failures.
- Experimental tokens may remain without a passing use claim. Proof must expose failures and limits as clearly as passes.
- Load `references/qualitative-judgment.md` through `mise run token-packet -- <args>` for taste, originality, corpus uniqueness, and non-AI-slop judgment.
- Apply `assets/judgment-review-catalog.json` through `mise run token-packet -- <args>` as a noncompensating token-local gate. Source fidelity, semantic role, accessible range, spacing relationships, responsive behavior, familiarity, standards, uniqueness, and rendered proof must each pass.
- Treat related-item, inset, group, section, shell, and wide-aperture spacing as semantic relationships. A regular scale, unusual value, or source resemblance alone cannot prove good grouping or rhythm.
- Call the reusable proof structure a token-proof scaffold. Reserve `UI composition template` for reusable screen structure and `Code Connect mapping template` for a repository mapping artifact.
- Global uniqueness remains outside this skill's valid claim scope.

## Completion

| Gate | Done only when | Check with |
| --- | --- | --- |
| Pipeline | All 25 current records and owners resolve. | `mise run token-status -- <args>` |
| Deliverables | `.tokens.json`, `.evidence.json`, `.proof.html`, and `.run.json` agree. | `mise run token-prove -- <args>` |
| Conformance | Current DTCG bytes pass with exit 0. | `mise run token-validate -- <tokens>` |
| Accounting | Every source, intent, token, context, extension, and exclusion appears once. | `mise run artifact-contract` |
| Exploration | At least three experiments and every material comparison earn locks. | `mise run validate-exploration` |
| Specificity | Five source-derived decisions and eligible typography trace to pixels. | `mise run font-prepare -- <args>` |
| Visual judgment | Current coverage, readback, defects, and invariants pass with zero unresolved vetoes; `globally_unique` stays false. | `mise run token-packet -- <args>` |
| Package | Every file has a route and factory receipts plus `mise run ci` pass. | `mise run audit-files` |

If any gate fails or lacks evidence, run `mise run token-block -- <args>`, return `BLOCKED`, name each failed gate and exact recovery need, and withhold non-slop, originality, corpus uniqueness, and completion claims.

## Optional final step

Run this only after every required gate passes. Freeze the last accepted package, evaluator, fixtures, environment, time budget, repetitions, and applicable resource measures. Change one named dimension at its smallest owner. Run `mise run improvement-policy`, the owning DTCG task, and `mise run ci` against frozen inputs. Keep the candidate only when that dimension improves materially while correctness, elapsed time, deterministic coverage, token efficiency, creative range, experimental range, direct visual judgment, simplicity, portability, safety, and the current DTCG contract do not regress. Otherwise restore the last accepted version and its digest, then rerun its narrow proof. Record keep, discard, or crash outside the editable package.
