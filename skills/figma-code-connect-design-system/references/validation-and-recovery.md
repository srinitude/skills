# Validation and recovery

## Proof classes

Keep source evidence, deterministic validation, repository runtime proof, Figma structural readback, Figma mapping readback, rendered-pixel review, interaction or motion review, and user approval as separate proof classes. No class substitutes for another.

## Stage checks

| Stage                  | Minimum proof                                                                                                                                                                                                                                                     |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Intake                 | Exact UI, platform, mode, sources, targets, permissions, and unknowns                                                                                                                                                                                             |
| Product model          | Tasks, states, flows, constraints, and evidence links                                                                                                                                                                                                             |
| Screen inventory       | Every required screen and state has an owner and reason                                                                                                                                                                                                           |
| Tokens                 | DTCG validation, source evidence, proof artifact, and vision review                                                                                                                                                                                               |
| Components             | Variable bindings, component API, variants, slots, accessibility, metadata, and pixels                                                                                                                                                                            |
| Templates and screens  | Correct instances, responsive behavior, content extremes, state coverage, and pixels                                                                                                                                                                              |
| Controlled comparisons | Exact inventory coverage across every hierarchy level, exploration and frozen experiment links, one changed factor, fixed conditions, distinct A and B renders, current vision, and stale propagation                                                             |
| Canvas cleanliness     | Current whole-canvas and active-area before-and-after views, affected IDs and ancestry, explicit status zones, eye, brain, and touch findings, bad-work dispositions, retained evidence, cleanup authority, invalidations, and zero unresolved cleanliness vetoes |
| Code Connect           | Existing mapping read, code export and props read, parse or preview, and final metadata readback if published                                                                                                                                                     |
| Integrated result      | Current lineage, zero stale dependencies, exact effect ledger, and full requested visual surface                                                                                                                                                                  |

The integrated result also needs every retained direct requirement, property-kind disposition, component-property parity entry, nested governance owner, token-local evidence reference, and canonical design-quality gate. All nine design gates must pass independently with current whole-view, detail, responsive, and input-path evidence.

The comparison inventory must cover every retained token primitive, atom, molecule, organism, UI composition template, screen, and flow exactly once. Each pair must resolve to its exploration source and frozen experiment. Each component property kind must resolve to a current pair, Figma owner, TypeScript API, mapping, and render or a justified non-use record. Reject missing items, duplicate pairs, mixed factors, stale vision, changed controls, or a passing dependent with stale lower evidence. Do not treat controlled visual comparisons as live-user causal proof.

## Visual review

Inspect the complete requested surface at readable size and relevant screen widths or platform sizes. Check wide and narrow layouts, default and material states, text, icons, images, focus, touch targets, contrast, clipping, overlap, hierarchy, spacing, motion, reduced motion, and content extremes. Stored node properties, hashes, test passes, and screenshots that were not actually viewed do not prove visual quality.

For Figma work, also inspect the whole canvas before, during, and after each mutation batch. Reject overlap, clipping, off-canvas required content, accidental stacking, unnamed or orphaned residue, misleading order, duplicate owners, stale evidence, and mixed accepted, exploratory, rejected, historical, or quarantine material. Require the same executor's eye, brain, and touch findings and bad design, bad output, and bad practice dispositions. A clean claim stays `STALE` after any affected move, reparent, style, token, component, or lower-owner change until current readback passes.

Use video or timed frame sampling when motion correctness matters. A resting screenshot does not prove animation timing, easing, ordering, or reduced-motion behavior.

## Code Connect validation

Read back each template file. Check `.figma.ts`, `figma.code`, source URL, export ID, imports, real code prop names, exhaustive variant values, boolean handling, string interpolation, instance type guards, slot shape, connected child execution, and absence of hardcoded configurable children.

Run the current CLI `parse` or `preview` before publication. Use `preview --inspect`, `--props`, `--all`, or `--unique` only when they answer the current property-state question. A dry run validates publish intent without publishing. A publish pass still needs mapping readback.

Validate property use and non-use. A passing mapping count does not prove that text, boolean, enum, swap, slot, or nested APIs exist in both Figma and production, behave dynamically, or are appropriate for the component. Reject a mapped property without product need and an omitted property without owner evidence.

## Recovery states

Use `STALE` when evidence was once valid but a source, component, token, mapping, or code export changed. Use `BLOCKED` when an access, authority, source, plan, seat, library publication, authentication, capability, or product choice prevents a retained claim. Do not downgrade a blocked required stage to `not_applicable`.

## Resume procedure

Read the run ledger, then independently re-inspect its external targets. Compare source hashes or revisions, Figma node existence and metadata, mapping labels and origins, repository paths and exports, and current screenshots. Mark invalid proof stale before continuing. Resume at the lowest stale or blocked dependency, not the last narrated step.

## Failure response

Return the failed gate, affected nodes and dependents, evidence seen, safe work completed, changes already made, rollback or recovery state, and smallest missing action. Do not repeat an unchanged failed call. Choose a different authorized route after the cause is understood.

## Package validation

When this package changes, run `mise run ci` twice from the package root, run the factory validators, verify all source-lineage hashes, scan for project-specific or retired owner names, and read every changed public file. Exercise one integrated negative case and one current passing case through `mise run validate-run`. Package validation does not execute this skill against a product.
