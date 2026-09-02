# Design-system lineage

## Atomic hierarchy

The required order is `DTCG tokens -> atoms -> molecules -> organisms -> UI composition templates -> screens`. Each level consumes the proved lower levels and adds only the behavior, composition, or context owned at that level.

| Level                    | Owns                                                | Must consume                       | Typical design form                                        | Typical code form                                      |
| ------------------------ | --------------------------------------------------- | ---------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------ |
| DTCG tokens              | Named visual and behavioral values with evidence    | Source observations                | Variables, styles, modes                                   | Token JSON, platform transforms, constants             |
| Atoms                    | Smallest reusable visible or behavioral controls    | Tokens                             | Component, variant set, property-bearing primitive         | Exported component, headless primitive, native wrapper |
| Molecules                | Small task units                                    | Tokens and atoms                   | Nested instances, slots, small component sets              | Compound or composed component                         |
| Organisms                | Major product sections                              | Tokens, atoms, molecules           | Structured component with nested parts                     | Feature component or coordinated subcomponents         |
| UI composition templates | Reusable view structure without final instance data | Every lower layer                  | Page, panel, modal, drawer, shell, or responsive structure | Route, layout, view scaffold, screen factory           |
| Screens                  | A concrete state of the bounded UI                  | Every lower layer and product data | Template instance with state and content                   | Rendered route, view, controller, scene, or window     |

Tokens and styles are not components until they are packaged behind a reusable UI contract. Assets are not components unless exposed through a reusable component. A whole page is not a component unless the system deliberately publishes it as a reusable view or template.

## Three template kinds

UI composition templates are product artifacts. Workflow templates are package procedures and ledgers. Code Connect mapping templates are repository mappings. Keep different names, files, validation, and owners for all three.

## Screen derivation

For one UI, derive the complete set of screens and states needed to perform its job. Include entry, loading, empty, populated, partial, error, permission, destructive confirmation, recovery, success, offline or stale data, keyboard and focus, reduced motion, localization, content extremes, and responsive or platform-adaptive states only when product evidence makes them applicable. The list is discovered, not imposed as a closed catalog.

Turn stable screen structure into UI composition templates. Keep data, copy, permission, navigation position, and temporary state at the screen instance unless the system deliberately exposes them as reusable properties.

## Bottom-up construction

Use proved DTCG tokens to create atoms. Use tokens and atoms to create molecules. Use tokens, atoms, and molecules to create organisms. Use all lower parts to create UI composition templates. Use the full hierarchy to create screens.

The codebase should mirror the same ownership edges when the platform supports them. A Figma nested instance should correspond to an actual imported component, subcomponent, slot, child view, or composition found in code. Do not force identical file boundaries when the platform's native component model differs; preserve the functional dependency and public API instead.

When production component, mapping, and generator scopes exist, place nested `AGENTS.md` files at their nearest shared owners. Each child must require the parent chain, state that the design system owns UI truth, name its generated-file owner, and forbid direct repair of generated outputs. Validate the parent and child instructions together.

## Update and invalidation

A lower-level change invalidates every dependent higher artifact. Mark dependents `stale` before repair. Rebuild in topological order, then re-run structural, behavioral, accessibility, and visual checks only for affected nodes plus an integrated screen readback.

Each accepted owner also carries its artifact quality checkpoint and freshness. A lower-owner edit invalidates dependent rendered pixels, interaction evidence, responsive evidence, component-property parity, and Code Connect mappings. Recounting files or components cannot refresh those claims.

A screen-only content change does not invalidate its template if the reusable structure and API remain valid. A code export or prop change invalidates the relevant Code Connect mapping and code consumers; it does not invalidate tokens unless the semantic design contract also changed. A mapping metadata change does not change production code or Figma component visuals.

## Focus-intent lineage

Every token primitive, atom, molecule, organism, UI composition template, screen, and flow carries the same current focus-intent record. Record `user_task`, `focus_target`, `focus_location`, `focus_timing`, `focus_mechanism`, `focus_reason`, `attention_sequence`, `competing_signals`, `defocus_and_recovery`, and `failure_evidence`. The token owner proves salience capacity. The product-design owner judges the attention sequence in whole views, details, responsive states, and input paths. This lifecycle owner proves that the accepted intent reaches the exact Figma node, variable, property, or nested component and the matching production behavior and mapping.

Use the focus intent to select a meaningful controlled comparison, not to justify a decision after sight. A lower-owner change invalidates every dependent focus-intent disposition. A higher layer may change the sequence for its task only by naming the new context and preserving each lower part's semantic contract. Multiple focal targets need an explicit order or a reason they are simultaneous. Visual prominence, property count, and mapping coverage do not prove intentional attention.

## Controlled comparison lineage

Maintain one comparison inventory across DTCG token primitives, atoms, molecules, organisms, UI composition templates, screens, and flows. Every inventory item must be covered by one current material-direction comparison before its owner can pass. Several items may share a comparison only when one indivisible owner relationship changes. The token skill owns primitive-token and token-relationship evidence. The product-design skill owns visual choice. This skill owns complete inventory coverage, Figma and code propagation, and stale-state transport.

Each pair changes one named owned relationship while holding the specimen, content, state, viewport, input path, and unrelated tokens fixed. It must state a material effect on hierarchy, meaning, behavior, task effort, grouping, responsive composition, or state understanding. Reject a one-pixel difference, adjacent token step, near-isomorphic candidate, or other pure optimization that only might help unless the user explicitly requested it. A small observed-defect or required-threshold repair is not pure optimization when current evidence names the threshold and crossing. Read both Figma variants back, inspect complete and detail pixels with current vision, and verify that the retained API and Code Connect mapping still express the chosen structure.

Do not add a token, property, swap, slot, nested component, or layer merely to create a test case. Record justified non-use at the relevant owner. A controlled visual pair supports a bounded design judgment; it is not a randomized live-user A/B test.

A changed lower-owner factor invalidates its pair and every dependent pair, render, Figma property readback, production API proof, and Code Connect mapping. Mark those dependents stale before repair and rebuild in hierarchy order.

## Lowest-cause repair

When a screen fails, trace the failure through screen, template, organism, molecule, atom, and token evidence. Repair the lowest incorrect owner. Do not patch a screen with a one-off value when the cause belongs to a token or component. Do not rewrite a token when the defect is instance data or screen-only logic.

## One-to-many platform implementations

One Figma component may map to independent web, iOS, Android, desktop, embedded, or cross-platform implementations. Record one lineage edge and mapping per implementation label. Shared design identity does not make those code implementations synchronized with each other.

## Lineage proof

Every lineage node records `id`, `level`, `status`, `depends_on`, source proof, Figma node when applicable, code export when applicable, Code Connect mapping when applicable, and current review evidence. The validator rejects cycles and a passing node that depends on a stale node; qualitative correctness still needs model and visual judgment.
