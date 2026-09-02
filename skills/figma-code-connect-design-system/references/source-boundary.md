# Source boundary

## Current baseline

Retrieved on 2026-08-31. The Code Connect package baseline is `@figma/code-connect` 2.0.0, published 2026-08-18. The repository tag commit is `f55fc3a8d9392df0dd80a9e859ffdddbd5c50019`. The inspected Figma plugin and skill baseline is 2.0.21; its publication date is not stated. The inspected `srinitude/skills` main commit is `a80a9f88b6b72c6358f6101e53aed64ed715058a`.

## First-party sources

- Agent Skills specification: <https://agentskills.io/specification>
- `srinitude/skills`: <https://github.com/srinitude/skills>
- DTCG Format Module 2025.10: <https://www.designtokens.org/TR/2025.10/format/>
- Figma Code Connect introduction: <https://developers.figma.com/docs/code-connect/>
- Figma UI and CLI comparison: <https://developers.figma.com/docs/code-connect/comparing-cc/>
- Figma CLI reference: <https://developers.figma.com/docs/code-connect/cli-reference/>
- Figma template API: <https://developers.figma.com/docs/code-connect/template-api/>
- Figma template migration: <https://developers.figma.com/docs/code-connect/templates-migration-guide/>
- Figma MCP introduction: <https://developers.figma.com/docs/figma-mcp-server/>
- Figma Code Connect repository: <https://github.com/figma/code-connect/tree/f55fc3a8d9392df0dd80a9e859ffdddbd5c50019>

## Evidence precedence

Live capability schemas define what the connected runtime can be asked to do. Current package source, registry metadata, and changelog define CLI behavior. Current developer docs define documented product behavior where they do not conflict with source. Installed specialist skills define guarded tool procedure for their installed version.

## Known current status

Version 2.0.0 makes parserless templates the actively maintained authoring path. Framework-specific parsers are limited to migration and unpublish in version 2. New users should create `.figma.ts` template files. JavaScript template files, batch files, helper bundling, local previews, migration, and unpublish remain current surfaces with narrower roles.

DTCG 2025.10 is the current stable Format Module, published 2025-10-28. The token specialist owns exact conformance, source evidence, and proof artifacts.

Code Connect is available on Organization and Enterprise plans with an eligible Dev or Full seat. CLI and UI prerequisites differ. UI mappings can use GitHub repository access and can map one design component to several implementations. CLI templates can map Figma properties to dynamic code examples and publish metadata used by Dev Mode and MCP.

## Completeness claim

The 47-entry registry is exhaustive only within the first-party documentation, version 2.0.0 source and changelog, package registry, and inspected plugin 2.0.21 schemas used for this build. It is not a claim that every future, private, account-gated, experimental, or unavailable Figma surface is known.

## Refresh procedure

On `refresh-sources`, run `mise run domain-research-policy`, then inspect the live capability catalog and full schemas. Check the current package version and publish time, repository tag and changelog, CLI and Template API docs, MCP integration docs, GitHub permission docs, Agent Skills specification, and skill registry. Compare each changed claim to `assets/code-connect-mechanisms.json` and `assets/capability-contracts.json`. Report drift before changing this package.

## Conflict record

Documentation may lag executable release behavior. Keep the executable version gate for framework parsers. Tool aliases may vary by host; capability roles are canonical and aliases are adapters. Product plan and seat text can change; read current identity and entitlement before any gated action.
