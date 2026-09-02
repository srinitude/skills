# Code Connect workflow

## Boundary model

Code Connect links a published Figma component to an existing production component, source path, import, label, and optional property-aware code example. Repository artifacts and Figma metadata are separate owners. Dev Mode displays mapping results to people. MCP supplies mapping results as machine context. Neither consumer edits production code by itself.

Use [../assets/code-connect-mechanisms.json](../assets/code-connect-mechanisms.json) as the complete planning checklist checked by `mise run complete` for the current source boundary. Select mechanisms by need; do not force all 47 into each component.

## Prerequisites

Confirm the current plan, eligible seat, published team-library component, component node URL, authentication, repository read access, code export, and target label. CLI work requires a current supported runtime and the `@figma/code-connect` package. Publication needs file-content read and Code Connect write access. UI GitHub browsing needs repository authorization and may need organization approval.

Read the live schema or current docs before acting because plan, seat, permissions, labels, and tool fields can drift.

## UI mapping path

The Code Connect UI stores mapping metadata in Figma. A simple mapping associates a published component with a repository path, optional export name, and label. It does not write repository files or encode dynamic prop behavior.

GitHub-backed browsing can read an authorized repository to discover paths and exports. One library file may connect to a repository and selected directories. The effective read boundary is the intersection of app permission, selected repositories, and user access. A repository connection does not authorize commits, branches, package changes, or CI changes.

One design component may have several independent UI mappings for frameworks or languages. Each mapping keeps its own label, source, component name, and optional instructions. Custom MCP instructions guide code generation but are metadata, not source code or tests.

CLI-created mappings appear in the UI but remain repository-owned and are edited through their artifacts and CLI. Keep origin in the mapping ledger before updates.

## Repository template path

For a new individual mapping, create `Component.figma.ts` with a default export and `figma.code`. Never create `.figma.tsx` or a new `figma.connect()` authoring file under version 2.

```ts
// url=https://www.figma.com/design/FILE/Library?node-id=1-2
import figma from 'figma';

const instance = figma.selectedInstance;
const label = instance.getString('Label');

export default {
  id: 'button',
  imports: ['import { Button } from "@scope/ui"'],
  example: figma.code`<Button>${label}</Button>`,
  metadata: { nestable: true },
};
```

Repository touchpoints may include `.figma.ts`, existing or migrated `.figma.js`, `.figma.batch.json`, `.figma.batch.ts`, relative helper modules, `figma.config.json`, `package.json`, a lockfile, `tsconfig.json`, source files, exports, and CI workflow files. Change only the needed artifacts.

For TypeScript checking, use `@figma/code-connect/figma-types`. A project that already has Node types may use `@figma/code-connect/figma-types-no-require` to avoid a global `require` conflict.

## Property mapping

Read the exact Figma component definition and real code API before writing. Figma property names are case-sensitive. Code prop names come from the production component, never from guesswork.

| Figma surface        | Template access                                             | Mapping rule                                                                                 |
| -------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Text property        | `getString('Name')`                                         | Map labels, titles, placeholders, or content only to a real string or child API              |
| Boolean property     | `getBoolean('Name', mapping?)`                              | Emit a boolean, conditional attribute, or mapped value                                       |
| Variant property     | `getEnum('Name', values)`                                   | Include every current Figma value and map it to the real code value                          |
| Instance swap        | `getInstanceSwap('Name')`                                   | Resolve the selected nested instance, check `type === 'INSTANCE'`, then execute its template |
| Slot property        | `getSlot('Name')`                                           | Interpolate returned structured sections; do not treat them as a string or instance          |
| Named child instance | `findInstance('Layer')`                                     | Use only when no component property owns the child; type-check before execution              |
| Connected child      | `findConnectedInstance(id)` or `findConnectedInstances(fn)` | Resolve by Code Connect ID when layer names are unstable                                     |
| Text layer           | `findText('Layer').textContent`                             | Use named text only when no text property owns it                                            |
| Arbitrary descendant | `findLayers(fn)`                                            | Use a precise filter and preserve traversal boundaries                                       |

Use `traverseInstances: true` only when the code API truly forwards a nested descendant and the target sits behind an instance boundary. Use `path` to disambiguate repeated layer names.

String and enum values need code-language quoting. Nested result sections from `executeTemplate().example` need code-language expression wrapping. Slot sections interpolate directly inside `figma.code`. Conditional booleans should emit or omit the real syntax.

Map every relevant Figma property when a valid code correspondence exists. If no code prop or composition exists, omit the property and record the gap. Do not invent a prop, export, helper, import, or fallback child.

For each component, freeze a bidirectional parity ledger for every current `TEXT`, `BOOLEAN`, `VARIANT`, `INSTANCE_SWAP`, `SLOT`, and nested connected property. Record the Figma property and values, product need, controlled comparison ID, exploration and experiment links, TypeScript code export and public API, mapping mechanism, rendered behavior, nested connection, current evidence, and status. Mark a property `mapped` only when every named layer exists and agrees. Mark it `not_applicable` only with owner evidence and a current comparison showing that the property would add no valid product control. Coverage for its own sake fails, and silent omission fails.

Link each parity row to the owning focus-intent record. State whether and how the property or connected child changes the intended target, location, timing, mechanism, reason, sequence, competition, or recovery. Verify the same effect in Figma, TypeScript behavior, and the mapping preview. Do not add a text, boolean, enum, swap, slot, or nested connection merely to expose focus control. Record justified non-use when attention should remain fixed at the owning component.

Text maps only to real string or child APIs. Booleans must change real rendered behavior. Enum mappings must cover every current value and a closed code value set. Instance swaps must resolve compatible instances dynamically. Slots must remain structured sections. Nested connected components must retain their own mapping and execute through the parent instead of flattening into copied markup.

## Nested and compound components

Connect configurable children independently, then execute their templates from the parent. Prefer `getInstanceSwap` when a swap property exists because a layer name changes with the selected instance. Use a slot only for a Figma property whose actual type is `SLOT`.

Call `executeTemplate()` after an `INSTANCE` type check. Do not guard it with `hasCodeConnect`; the runtime owns the missing-connection behavior. Never concatenate or join `ResultSection[]`; interpolate each section through `figma.code`.

When a slot exposes `connectedInstances`, use those current connected children when the code API renders an iterable slot. Keep parent and child template responsibilities aligned with the production component boundary.

## Generated families and batch templates

Use batch templates for large, repetitive families such as icons only when one shared template and per-entry data preserve the same documents as individual templates. The artifacts are `.figma.batch.json` plus `.figma.batch.ts`. Include the batch JSON in project config. Parse before and after a migration; delete individual files only with explicit authority and equal-output proof.

Relative helper imports may share formatting or utility logic across template files. Only project-relative helpers are bundled. External package imports are not helper bundles. Keep helpers used, bounded, and parse-checked.

## Configuration

Inspect `figma.config.json` before adding or changing it. Current core fields include `codeConnect.include`, `exclude`, `label`, `language`, `defaultBranch`, `interactiveSetupFigmaFileUrl`, and `documentUrlSubstitutions`; current source also accepts `apiUrl`.

Legacy parser fields may include `parser`, `importPaths`, `paths`, `storybook`, Xcode or Swift package paths, source package paths, import mappings, and `parserCommand`. Preserve them only when an existing legacy workflow needs migration or unpublish.

Source links are derived from repository origin, branch, and source path. Confirm remote URL and branch rather than fabricating a link. Use document URL substitutions only for intentional, tested URL rewrites.

## CLI lifecycle

Use the current package locally or in CI. Version 2 supports these maintained commands for template workflows:

| Command                          | Boundary effect                                                           |
| -------------------------------- | ------------------------------------------------------------------------- |
| `npx figma connect create URL`   | Writes a boilerplate `.figma.ts` file after reading a published component |
| `npx figma connect parse`        | Reads local artifacts and outputs Code Connect document JSON; no publish  |
| `npx figma connect preview FILE` | Renders local snippets for Inspect-style review; no publish               |
| `npx figma connect migrate`      | Writes parserless template artifacts from legacy inputs                   |
| `npx figma connect publish`      | Validates and writes mapping metadata to Figma                            |
| `npx figma connect unpublish`    | Removes matching published mapping metadata from Figma                    |

Use `publish --dry-run` to test publication without writing metadata. Use `--exit-on-unreadable-files` in CI. Use `--force` only with explicit authority because it can overwrite UI-created mappings. Use labels deliberately when one node has several implementations.

Preview supports property inspection and current state rendering with `--inspect`, `--props`, `--all`, `--max-combinations`, and `--unique`. These flags are subcases of one preview mechanism, not separate integration mechanisms.

CI may run parse, validation, or publication on source changes. A secret, token, workflow, event filter, branch rule, or publication step is a repository or hosting-system change and needs separate authority. CI success does not prove Dev Mode display until mapping readback.

## Legacy boundary

Framework-specific React, HTML, SwiftUI, Compose, and Storybook parsers are legacy authoring surfaces. Version 2 allows them only for migration and unpublish. Install and pin version 1 only if the user explicitly chooses a legacy authoring workflow and accepts its unsupported status.

Custom parsers were documented as preview. Under version 2 they do not become a maintained new-authoring path. Preserve their config and parser protocol only for an existing v1 workflow, migration analysis, or unpublish.

## Dev Mode and MCP

Published template mappings display real imports and property-aware examples in Dev Mode Inspect. Simple UI mappings display source path and optional component name without a dynamic user-authored example. Both are human handoff and make no repository change.

MCP design context can include a `CodeConnectSnippet` or equivalent selected mapping context. Platform and language hints select among several mappings. UI custom instructions may add codebase context. MCP output is machine context, not proof that a file was generated, compiled, tested, committed, or published.

Current broader Figma tools can read a mapping, read template authoring context, list published components and properties, suggest mappings, save one simple or template mapping, save reviewed batches, enrich design context, and enrich design-system search. Each direct metadata write needs approval and readback.

## Source and effect ledger

For each mapping record the Figma file and node, published-library state, mapping origin, label, source URL or path, component name, code export, imports, property coverage, template path, config path, package version, validation commands, publish or unpublish authority, metadata readback, Dev Mode display evidence, and MCP context evidence.

Keep repository change, Figma component change, Figma mapping metadata change, Dev Mode display, MCP context, suggestion, and no persistent change as separate outcomes.

## Does not do

Code Connect does not generate the production component, make Figma and code bidirectionally synchronized, infer production props automatically in parserless templates, publish a component library, update code when a designer changes a variant, update Figma visuals when code changes, validate runtime behavior, test accessibility, commit repository changes, configure GitHub or CI by itself, or guarantee visual equality.

A source link is not a source edit. A generated snippet is not compiled code. A suggestion is not a saved mapping. A saved mapping is not a repository artifact. A repository template is not Figma metadata until published. Published metadata does not change component pixels or production code.
