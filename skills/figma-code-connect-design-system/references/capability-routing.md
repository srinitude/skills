# Capability routing

## Route by effect

Use [../assets/capability-contracts.json](../assets/capability-contracts.json) as the current adapter registry through `mise run validate`. Select a capability by role and effect, then inspect the live schema before use. A missing alias blocks only that capability; do not invent a substitute effect.

| Need                                | Capability role                                | Effect           | Required specialist or check                                                     |
| ----------------------------------- | ---------------------------------------------- | ---------------- | -------------------------------------------------------------------------------- |
| Resolve plan and seat               | `figma.identity`                               | Read             | Check entitlement before gated work                                              |
| Read a FigJam product map           | `figma.figjam.read`                            | Read             | Load `figma-use-figjam` before any later FigJam execution                        |
| Create a blank target               | `figma.file.create`                            | Figma write      | Load `figma-create-new-file`; resolve exact plan and user authority              |
| Read design structure               | `figma.metadata.read`                          | Read             | Design files only; use FigJam reader for boards                                  |
| Inspect pixels                      | `figma.visual.read`                            | Read             | Strong vision judges the rendered result                                         |
| Read code-oriented design context   | `figma.design-context.read`                    | Context          | Load `figma-design-to-code`; Code Connect stays enabled unless directly disabled |
| Read variables and libraries        | `figma.variables.read`, `figma.libraries.read` | Read             | Page through libraries before scoped search                                      |
| Search reusable design assets       | `figma.design-system.search`                   | Context          | Search one intent at a time; inspect matches before reuse                        |
| Read published component graph      | `figma.component-graph.read`                   | Read             | Use for batch planning and dependency discovery                                  |
| Discover mapping gaps               | `figma.code-connect.suggest`                   | Suggestion       | Review candidates before saving                                                  |
| Read mapping properties             | `figma.code-connect.authoring-context`         | Context          | Use exact property names and types                                               |
| Read current mapping                | `figma.code-connect.read-map`                  | Read             | Record label and origin before update                                            |
| Save one mapping                    | `figma.code-connect.write-map`                 | Metadata publish | Separate simple and template mappings; require approval                          |
| Save reviewed mappings              | `figma.code-connect.bulk-write`                | Metadata publish | Preserve per-item node, source, label, name, and template data                   |
| Create or edit native Figma content | `figma.canvas.execute`                         | Figma write      | Load `figma-use` plus the domain skill; execute sequentially and return IDs      |
| Move assets                         | `figma.asset.transfer`                         | Figma write      | Confirm rights, bytes, destination, and readback                                 |
| Capture a running web UI            | `figma.web-capture`                            | Figma write      | Use only for an authorized existing file and applicable web source               |
| Gather pattern evidence             | `research.pattern-library`                     | Reference        | Record provenance; never treat examples as product authority                     |

## Figma skill chain

Load the current owner before its guarded tool. Use `figma-use` for native execution, `figma-use-figjam` for boards, `figma-generate-library` for system foundations and components, `figma-generate-design` for composed views, `figma-design-to-code` for design-context extraction into code, `figma-use-motion` for authoring motion in Figma, `figma-implement-motion` for implementing Figma motion in code, and `figma-swiftui` for SwiftUI translation in either direction.

The design-system workflow must inspect the Figma file before writes, create variables before components, use auto layout for structural groups, load fonts before text mutation, set variable scopes and code syntax, return every affected node ID, and verify structure and pixels after each small write.

## Fastest valid Figma loop

Freeze independent hypotheses, candidates, fixed conditions, and acceptance rules in one pass. Start high-latency reads and independent non-mutating checks together. Repair the highest-fanout lowest incorrect owner through one spatially bounded write, return exact IDs, re-fetch native properties immediately, then use the same executor's vision on the whole page and readable detail before the next dependent write. Keep one writer and one visual decision active at a time.

Count progress only after the owning Figma, repository, mapping, or proof artifact changed and its current readback passed. A plan, task entry, queued command, successful request without readback, capture not directly viewed, or unchanged external state is not progress. A faster path is invalid if it narrows exploration, removes a real candidate, weakens falsification, skips a product state, viewport, input path, property kind, dependency, or proof gate, or lets structure replace eye, brain, and touch judgment.

## Continuous canvas cleanliness

Treat canvas cleanliness as part of every Figma write, not as a final cleanup stage. Before the first write, inspect the whole page and the intended work area, record existing accepted, exploration, rejected, historical, and quarantine zones, and identify overlaps, clipping, off-canvas required content, accidental stacking, unnamed or orphaned residue, misleading order, duplicate owners, unreachable targets, and stale evidence. During work, use small spatially bounded batches and keep each created item named, parented, separated, and status-readable. After each batch, re-fetch affected IDs and ancestry, inspect the whole canvas and readable detail, and recheck neighbors and invalidated dependents.

The same executor uses current vision and human eye, brain, and touch judgment. Eye owns visual order, grouping, crowding, alignment, edge conditions, and status separation. Brain owns product meaning, provenance, comparison logic, reading sequence, next action, and false relationships. Touch owns selection safety, target gaps, reach, view occlusion, manipulation effort, input changes, accidental-edit risk, and recovery. Bad design, bad output, or bad practice prevents a clean disposition even if node geometry and page ancestry pass.

Cleanup may move, relabel, reparent, or place exact evidence in a named quarantine area when authority allows. It may not delete proof, flatten component or token lineage, detach reusable ownership, conceal a failed comparison, or convert historical evidence into current authority. Record before and after views, affected IDs, retained evidence, authorized cleanup, invalidations, and the eye, brain, touch, and bad-work dispositions. If live whole-canvas sight or the active Figma control path is unavailable, mark the affected claim `BLOCKED`.

## Capability disposition

Every selected role gets one disposition. `use` means its schema was inspected and its prerequisites passed. `not_applicable` needs evidence that the bounded UI does not need the role. `blocked` names the missing capability or prerequisite. `pending` is allowed only before execution.

## Research boundaries

Mobbin, Refero, Lazyweb, and open-web sources can reveal conventions, comparable patterns, accessibility guidance, motion ideas, and visual references. They cannot supply missing product requirements, repository truth, Figma ownership, component node IDs, publication authority, or production validation.

## Readback rule

After a Figma write, re-read returned IDs and inspect pixels. After a repository write, read the final bytes and run project checks. After a mapping publish or unpublish, read the mapping from Figma. After a library or permission change, read the owning system. A successful request without current readback is not completion proof.
