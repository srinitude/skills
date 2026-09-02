---
name: figma-code-connect-design-system
description: 'Use when a FigJam board, product requirements document, reference image, Figma design file, published library, or codebase must become or update an evidence-traceable Figma design system, DTCG token hierarchy, platform-specific UI templates, production components, and verified Code Connect mappings. Covers create, update, plan, run, validate, resume, and source-refresh work for one bounded UI or a larger product system across web, mobile, desktop, embedded, and other platforms.'
license: MIT
metadata:
  author: Kiren Srinivasan
  version: '0.3.0'
---

# Figma Code Connect design system

Create or update one coherent design system from the product truth available in a FigJam board, PRD, image, existing Figma file or library, and codebase. Keep design, code, Code Connect, evidence, permissions, and change effects explicit so no generated suggestion is mistaken for a production change.

## Commands

| Command                                       | Result                                                                                                                                                   |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `help`                                        | Explain inputs, outputs, permissions, commands, and stop conditions without changing anything.                                                           |
| `plan <inputs> [--mode create\|update\|auto]` | Inspect sources, choose create or update, inventory screens, route capabilities, and write only an authorized run ledger.                                |
| `run <inputs> [--mode create\|update\|auto]`  | Execute the approved workflow, harden the hierarchy from tokens upward, and maintain Code Connect after each primitive is ready.                         |
| `validate <run-or-target>`                    | Re-read current repository, Figma, visual, mapping, and lineage state without adding new scope.                                                          |
| `resume <run-ledger>`                         | Reconstruct current state, invalidate stale proof, and continue from the first unproved dependency.                                                      |
| `refresh-sources`                             | Compare the package baseline with current first-party specifications, schemas, docs, repository, package registry, and changelog; return a drift report. |

After `mise run validate` confirms package shape, read the matching worked file in `examples/` before each command. Read `examples/failure-missing-authority.md` when any write, publish, delete, or source authority is unclear.

## Ordered workflow

1. **Freeze the result.** Mise: run `mise run skill-info`. Model: name the Figma and code outcome, rights, bounds, sources, and proof without adding scope.
2. **Ground the domain.** Mise: run `mise run domain-research-policy` and `mise run use-case-policy`. Model: read current first-party Figma sources, test counterevidence, and record each source use or limit.
3. **Prove the task graph.** Mise: run `mise run task-graph-policy` and `mise run mise-primitives-policy`. Model: keep one default path and leave sight, product meaning, and choice outside scripts.
4. **Start or resume one run.** Mise: run `mise run new-run` for a new ledger or `mise run validate-run` for an old one. Model: freeze every direct need and mark inherited proof stale.
5. **Experiment from low owners upward.** Mise: run `mise run validate-run` after each saved step. Model: use `dtcg-tokens` and `design-like-im-5`, compare unlike directions, inspect current pixels, and lock a passed lower owner before higher work.
6. **Change Figma in small owned writes.** Mise: keep the run ledger current through `mise run validate-run`. Model: use the required Figma capability, read back each node, inspect the whole canvas and clear details, then keep or repair the write.
7. **Prove production parity.** Mise: run `mise run validate-run`. Model: connect each real Figma property to a real TypeScript React API and parserless Code Connect mapping, including nested and responsive behavior.
8. **Run integrated checks.** Mise: run `mise run complete`, then the target repository's owning Mise gate. Model: reject any script PASS that lacks current Figma, code, rendered, or direct visual proof.
9. **Account for this invocation.** Mise: run `mise run invocation-policy -- RECEIPT`. Model: link each run task to current output or a request-specific not-applicable proof.
10. **Maintain last.** Mise: run `mise run mise-primitives-update` only after the accepted outcome. Model: reconcile any changed Mise part, rerun `mise run complete`, and stop at the first full accepted state.

## Start every run

1. Read [references/operating-contract.md](references/operating-contract.md), [assets/run-contract.json](assets/run-contract.json), and the matching example through `mise run new-run`; create an authorized external ledger.
2. Freeze UI, platform, sources, mode, authority, outputs, and proof. Read [assets/capability-contracts.json](assets/capability-contracts.json) through `mise run validate-run` and classify each capability.
3. Inspect current Figma structure, code, tokens, components, mappings, and renders before mutation. Keep read, display, repository write, Figma write, publish, and delete permissions separate.
4. Preserve every direct requirement with its owner, disposition, proof, status, and invalidators. Later work cannot displace it.
5. Start from zero trust. Mark inherited artifacts and verdicts `STALE` until current proof earns `PASS`. This is a review prior: inspect first, preserve passes, and reject needless change.
6. Minimize elapsed time to verified lowest-owner change without reducing experiments, states, viewports, parity, or same-executor vision. Batch reads; serialize writers and visual decisions. Plans and unviewed output are not progress.

## Resolve input truth

- Treat every input as evidence with an owner, location, freshness, rights, and confidence. Do not merge conflicts silently.
- A FigJam board may describe product logic but does not prove current code or design-file state.
- A PRD may define intended behavior but does not prove implementation.
- An image proves only visible pixels and cannot prove hidden states, motion, semantics, tokens, or component structure.
- A codebase proves current inspected code at a revision, not current Figma metadata.
- An existing Figma file or published library proves current inspected design state, not code behavior.
- Prefer live owning sources for current facts. Record conflicts and ask only when the choice changes the product or authorized target.

## Execute in one dependency order

Follow the exact stages in [assets/run-contract.json](assets/run-contract.json) through `mise run validate-run`. Read [references/design-system-lineage.md](references/design-system-lineage.md) through the same task before the first token, component, or screen decision.

1. Load and follow `design-like-im-5` for product modeling, screen coverage, state discovery, design judgment, and visual review.
2. Load and follow `dtcg-tokens` for source-specific DTCG tokens, token evidence, atom proof, and its rendered proof artifact.
3. Build only in this cumulative order: DTCG tokens, atoms, molecules, organisms, UI composition templates, then screens.
4. Reuse every proved lower layer in each higher layer. A higher layer may not bypass, duplicate, or restate a lower rule.
5. When a defect appears, repair the lowest incorrect dependency, mark every dependent higher artifact stale, rebuild upward, and visually recheck the affected surfaces.
6. After a reusable primitive is hardened, load and follow `figma-code-connect` to connect that primitive to inspected production code.
7. Carry token-local evidence and the canonical `design-like-im-5` quality record through lineage. Apply direction, artifact, and integrated checkpoints. Any lower-owner edit makes dependent pixels, behavior, property parity, and Code Connect proof stale.
8. Inventory every layer and compare materially different directions at the true owner before acceptance. Freeze one-factor conditions and use current eye, brain, touch, bad-design, bad-output, and bad-practice judgment. Micro tuning needs an explicit request, observed defect, or required threshold. Link each pair to its source, experiment, Figma owner, production API, and Code Connect mapping.
9. Carry one current focus-intent record for every item through its comparison and through Figma, TypeScript production behavior, and Code Connect. Prove what the person notices, where, when, how, why, and in what order. Lower-owner change makes dependent focus proof stale; unjustified properties are non-use, not invented controls.
10. Treat portrait and landscape as separate mobile and tablet proof contexts through Figma, production, Code Connect, and renders. Add an orientation prop only when anatomy or behavior changes; otherwise prove both contexts with one API.

## Keep three template kinds separate

- A UI composition template is a reusable page or view structure made from organisms.
- A workflow template is this skill's reusable operating packet, ledger, schema, checklist, or command example.
- A Code Connect mapping template is a repository artifact that renders code usage for a Figma component.
- Never use one kind as evidence that another exists or passes.

## Route Figma work by capability

Read [references/capability-routing.md](references/capability-routing.md) through `mise run validate` before any Figma tool call. Use capability roles first and treat current tool aliases as versioned adapters.

- Load `figma-use` before native Figma execution, `figma-use-figjam` for FigJam, and `figma-create-new-file` before file creation.
- Load `figma-generate-library` for variables, styles, components, variants, library structure, and Code Connect integration.
- Load `figma-generate-design` for composed screens, `figma-design-to-code` before design-context extraction for code, and the motion or SwiftUI owner when that platform or behavior applies.
- Use design reference services and current web sources only as evidence. They do not override product truth or authorize a change.
- Make Figma writes incrementally, return every affected node ID, read back metadata, inspect rendered pixels with strong vision, and repair before continuing.
- Keep the canvas clean throughout mutation through [references/capability-routing.md#continuous-canvas-cleanliness](references/capability-routing.md#continuous-canvas-cleanliness) and `mise run validate-run`. Inspect whole canvas and active area, separate work zones, and record before and after cleanliness. Bad design, output, or practice blocks the claim.
- Register one canonical page per depth-one owner. Re-fetch acyclic ancestry after each mutation; wrong pages, duplicates, orphans, stale records, or missing placement sight fail. Moving an owner invalidates descendants, code lineage, mappings, and visual proof.
- The paramount visual-proof rule governs every visual claim. The same invoking strong vision-capable executor must inspect current pixels through every applicable available vision capability across whole views, details, pages, states, viewports, input paths, before and after each change and invalidation. Proxies may veto but cannot grant visual `PASS`; missing sight is `BLOCKED`.
- For Figma desktop audits, use `computer-use` as the platform-neutral local application-control capability. Load `dtcg-tokens`, `design-like-im-5`, this skill, and `computer-use` before deciding. The same executor must operate and directly inspect the Figma application and own each visual disposition.
- Record every page, primitive, component, node, and layer with current direct-vision, web, Mobbin, Refero, Lazyweb, project inspiration, product API, event or webhook, and runtime source receipts or a blocked disposition. This applies only to Computer Use Figma audits; each skill stays standalone elsewhere.

## Maintain Code Connect

Read [references/code-connect.md](references/code-connect.md) and [assets/code-connect-mechanisms.json](assets/code-connect-mechanisms.json) through `mise run complete` before planning or changing a mapping.

- Distinguish UI path/name mappings from repository-authored and CLI-published Code Connect mapping templates.
- For new individual mappings, create parserless `.figma.ts` files with `figma.code`; never create `.figma.tsx` or a new framework-parser mapping.
- Preserve or migrate existing `.figma.js`, batch templates, or legacy artifacts only through the current documented path.
- Map only real code exports, props, imports, package paths, source paths, and composition found in the repository.
- Read exact Figma properties and map text, booleans, variants, instance swaps, slots, descendants, and nested connected components without inventing code props.
- Record every `TEXT`, `BOOLEAN`, `VARIANT`, `INSTANCE_SWAP`, `SLOT`, and nested connected property as mapped or justified not applicable. Link each disposition to current controlled comparison evidence. Use a property only when the product and component contract need it. Prove both Figma and TypeScript production APIs, dynamic mapping, rendered behavior, and current nested connections.
- Validate locally before publish. Publishing and unpublishing change Figma metadata and require separate authority, authentication, entitlement, and readback.
- Keep one Figma component free to map to several independent platform implementations. Do not imply synchronized source code.
- Require nested `AGENTS.md` governance at production component, mapping, and generator owners when those repository scopes exist. Each deeper file must require its parent chain, keep the design system as UI source truth, and direct generated-file repair to the canonical generator.

## Mutation gates

- `plan`, `validate`, and `refresh-sources` are read-only unless the user separately authorizes a local report or ledger file.
- A repository write needs an exact repository target and repository-write authority.
- A Figma write needs an exact file and node scope plus Figma-write authority.
- Mapping publish, mapping unpublish, library publication, deletion, GitHub authorization, package installation, and CI changes are separate effects with separate gates.
- Record the authorization ID, exact target, effect, result, and readback for every executed mutation.
- Stop the affected action when authority, plan, seat, published-library state, authentication, repository access, or source ownership is missing. Continue independent read-only work.

## Validate and return

Read [references/validation-and-recovery.md](references/validation-and-recovery.md) through `mise run validate-run`. Run `mise run validate-run -- RUN.json`, then run `mise run complete` when this package changed.

- A script pass proves structure only. Strong vision owns rendered-pixel judgment; design owners own product choices; repository checks own code behavior; Figma readback owns current node and mapping state.
- Figma validation also requires the current canvas-cleanliness receipt defined in [references/validation-and-recovery.md](references/validation-and-recovery.md) through `mise run validate-run`. A neat layer tree, passing ancestry task, or cropped screenshot cannot replace current whole-canvas eye, brain, and touch judgment.
- Perfection is not a valid integrated claim. Define each observable layer outcome and the metric, measure, proxy, objective, or direct judgment that can test it, then keep the claim inside that evidence boundary. Current strong vision is the primary authority for visual quality after measured constraints pass; neither metrics nor polish may compensate for another failed gate.
- Return the run status, mode, target, sources, conflicts, capability dispositions, hierarchy and stale nodes, repository changes, Figma changes, metadata changes, display or context-only effects, validations, limits, and next blocked action.
- Use only `PASS`, `STALE`, or `BLOCKED` for the integrated result. `PASS` requires current proof for every retained claim and zero open lower-layer defects.
- An integrated `PASS` also requires the canonical noncompensating design record. Truth, access, task, perception, familiarity, standards, uniqueness, craft, and resilience must all pass. Counts, polished crops, or mapping coverage cannot replace human eye, brain, touch, responsive, and input-path judgment.

## Package owners

- [references/source-boundary.md](references/source-boundary.md) owns versions, evidence scope, conflicts, and refresh rules through `mise run domain-research-policy`.
- [references/decisions.md](references/decisions.md) owns durable package decisions through `mise run decision-policy`.
- `assets/` owns machine-readable contracts and the 47-mechanism registry checked by `mise run complete`.
- The `mise.toml` task graph owns deterministic scaffolding, checks, and behavior tests checked by `mise run task-graph-policy`.
- `evals/` owns trigger, behavior, failure, recovery, speed, and source-lineage cases checked by `mise run evals`.
- [references/generation-contract.md](references/generation-contract.md) applies only when this package changes and is checked by `mise run validate`.

## Factory policy

- Read [references/use-case-specificity.md](references/use-case-specificity.md) through `mise run domain-research-policy`. Read [references/resource-and-experiment-design.md](references/resource-and-experiment-design.md) through `mise run improvement-policy`.
- Run `mise run factory-assets-write` after a task or policy change. Run `mise run domain-research-policy`, `mise run use-case-policy`, `mise run mise-primitives-policy`, `mise run primitive-lifecycle-policy`, `mise run task-graph-policy`, and `mise run decision-policy` before package acceptance.
- Use `mise run agentic-request` for a long prompt, a digest-bound skill dependency, or an open Figma capability. The caller owns runner authority. The task checks the envelope and never replaces model sight, meaning, creativity, or product judgment.
- Mise owns fixed mechanics, state checks, ordering, hashes, and receipts. The model owns source meaning, product choice, experiments, direct vision, and the use of all authorized capabilities that code cannot supply.

## Optional final step

After all required Figma and code work passes, run `mise run improvement-policy`. Change one named skill part at its smallest owner. Keep it only if that part improves and correctness, time, token use, portability, creativity, experiments, visual judgment, and every current rule do not get worse. Otherwise restore the last passed version and check its digest.

## Done

The skill is done only when the requested create or update result exists at the approved target, every current source and mapping claim has readback, every affected hierarchy edge is current, visual review covers the requested surface and states, the Figma canvas has a current clean receipt with no unresolved overlap, clipping, accidental stacking, orphaned residue, mixed-status zone, or bad-work veto, repository and Figma effects are separated, and no unapproved mutation or unsupported synchronization claim remains. Package work also requires `mise run complete` and a valid invocation receipt.
