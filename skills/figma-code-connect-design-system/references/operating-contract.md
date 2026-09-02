# Operating contract

## Outcome

Create or update the design system for the bounded UI and platform named by the user. The result may include an approved Figma file or library, repository tokens and components, Code Connect artifacts and metadata, a screen set, and proof ledgers. Create and update are equal modes and share every gate.

## Mode selection

Use `create` only when the approved target does not yet exist. Use `update` when an existing Figma file, library, token set, code component, mapping, or run ledger is in scope. In `auto`, inspect first and choose `update` if any approved target exists; otherwise choose `create`. Never replace an existing target merely because a blank target is easier.

## Required run records

The run directory is outside this package and contains these owner files when they apply: `run.json`, `sources.json`, `product-model.json`, `screen-inventory.json`, `hierarchy.json`, `figma-state.json`, `code-connect.json`, `changes.json`, `reviews.json`, and `completion.json`.

Each record names its schema version, run ID, current source hashes or revisions, owner, status, proof, unknowns, and invalidators. The run also keeps a requirement ledger, token evidence reference, canonical design-quality reference, property-kind dispositions, component-property parity, and nested governance evidence. Keep secrets, private source bytes, and access tokens out of these records.

Every direct requirement stays in the requirement ledger in source order with its exact request, owner, `use` or justified `not_applicable` disposition, current evidence, status, and invalidators. New work may refine or invalidate an earlier entry, but it may not silently remove it.

## Fixed stage order

1. `freeze-intake` fixes outcome, UI, platform, sources, mode, targets, permissions, and proof.
2. `audit-sources` inventories source authority, freshness, rights, conflicts, and gaps.
3. `model-product` uses the product-design owner to derive tasks, states, constraints, and flows.
4. `inventory-screens` lists every screen and state needed for the bounded UI to work.
5. `inspect-design-system` reads the current Figma and repository systems before proposing change.
6. `harden-dtcg-tokens` delegates tokens, evidence, rendered proof, and atom proof.
7. `harden-atoms` creates or updates the smallest reusable UI parts from proved tokens.
8. `harden-molecules` composes atoms and tokens into small task units.
9. `harden-organisms` composes lower parts into major view sections.
10. `harden-design-templates` composes organisms into reusable view structures.
11. `compose-screens` instantiates templates for every required screen and state.
12. `maintain-code-connect` creates, updates, validates, and if authorized publishes mappings.
13. `integrated-validation` re-reads current Figma, repository, mappings, lineage, pixels, states, and effects.

Apply the canonical quality record at three points. The direction checkpoint follows research and materially unlike options. The artifact checkpoint follows each rendered owner. The integrated checkpoint follows the last dependent mutation across whole views, readable details, responsive sequences, and input paths. This skill carries and invalidates the record from `design-like-im-5`; it does not redefine or score that judgment.

Before any hierarchy item passes, its lowest owner must supply the controlled comparison required by `references/design-system-lineage.md` through `mise run validate-run`. The run ledger inventories every item, records one changed factor and fixed conditions, links the pair to its exploration source and frozen experiment, carries current vision evidence, and marks all dependent comparisons stale after a lower-owner change.

Do not skip a stage. A stage may be `not_applicable` only with evidence tied to the bounded UI. A blocked stage stops only its dependents.

## Create path

Inspect accessible libraries and code before creating a file. Resolve a plan and destination. Create variables and styles before components, components before component sets and composed views, and published-library prerequisites before Code Connect metadata. Build one verified slice before scaling.

## Update path

Read existing pages, variables, styles, components, variants, descriptions, mappings, screen instances, code exports, props, package paths, and prior ledgers. Classify each item as keep, modify, add, deprecate, migrate, unpublish, or remove. Destructive classes need their own authority and exact-ID readback.

## Intake boundary

At least one of these inputs is required: FigJam, PRD, image, codebase, existing Figma design file, or published library. Any one may start a run, but no one input automatically proves the others.

## Source conflict rule

Do not use a fixed global source-of-truth order. Identify the canonical owner for the disputed fact. Product intent may belong to a signed PRD, current implementation to code at a revision, visual component state to the inspected Figma library, and customer flow logic to an owned product map. Present a material unresolved conflict before mutating a dependent target.

## Permission rule

Read permission does not imply write permission. Repository write, Figma write, metadata publish, metadata unpublish, library publication, deletion, package installation, GitHub authorization, and CI configuration are independent effects.

## Completion record

Return `PASS` only when every retained stage and requirement passes, no dependency is stale, token and canonical design-quality evidence are current, component-property parity and governance pass, current readback proves each claimed external effect, the requested screens and states pass vision review, and the final result contains no unsupported synchronization or code-generation claim. Return `STALE` when prior proof is invalidated but safe recovery is known. Return `BLOCKED` when an unmet prerequisite prevents the retained outcome.
