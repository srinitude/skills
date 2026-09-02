# Agent Plugins v1

Runtime summary and backlink: [`../README.md`](../README.md) `PD-101`. Read this page when installing, validating, packaging, or reviewing the portable Agent Plugins route.

## Package result

The repository is an Agent Plugins 1.0.0 package. It keeps all portable components in the specification's fixed root locations:

```text
plugin.json
skills/
mcp.json
mcp/dist/server.mjs
```

`plugin.json` names and describes the package. It does not list components because Agent Plugins discovery uses fixed paths.

`skills/` is the only skill-body owner. A client discovers each immediate child directory that contains `SKILL.md`.

`mcp.json` declares the bundled read-only stdio server. The command is one executable token, `node`, and the server path is rooted at `${PLUGIN_ROOT}`.

## Install

Installation, trust, permissions, sandboxing, updates, and marketplace distribution belong to each client. Use the current [compatible-client registry](https://agent-plugins.org/compatible-clients) and that client's first-party install instructions.

A client that accepts a local Agent Plugin can load this repository checkout or its packaged archive. The package does not require copied skill bodies or a hosted service.

The existing skills.sh and client-specific routes in the root README remain supported. Those files are compatibility surfaces beside the portable core, not alternate Agent Plugin definitions.

## Validate

Install the pinned toolchain and dependencies, then run the repository gate:

```sh
mise install
mise run bootstrap
mise run ci
```

The Agent Plugins check performs all of these checks offline:

- validates `plugin.json` against the canonical 1.0.0 manifest schema;
- validates `mcp.json` against the canonical 1.0.0 MCP schema;
- verifies the vendored schema digests against `evidence/agent-plugins-v1.json`;
- discovers every immediate child skill and requires a regular `SKILL.md`;
- resolves package paths and rejects a path or symlink that escapes the plugin root;
- starts the configured stdio server through a real MCP client;
- requires exactly the six documented read-only tools;
- inspects the npm archive for both portable manifests, all canonical skills, the MCP bundle, schemas, and evidence.

Run only the focused tests with:

```sh
mise run test-focus -- src/agent-plugin.test.ts mcp/src/stdio-smoke.test.ts src/package.test.ts
```

## Schema provenance

The repository vendors the canonical schemas so validation does not depend on live network access. Their source URLs and SHA-256 digests are recorded in `evidence/agent-plugins-v1.json`.

The live specification remains authoritative. A future Agent Plugins version requires a new versioned schema directory, source record, tests, and reviewed manifest change. Do not silently replace the 1.0.0 files.

## Security boundary

Agent Plugins is a package format, not a sandbox. Review the plugin before enabling it under a client's trust model.

This package's MCP server has no write tool, network call, telemetry, credential field, or hosted transport. It confines reads to the canonical skill tree and rejects absolute paths, traversal, hidden paths, nested references, and symlink escapes.

`PLUGIN_ROOT` and `PLUGIN_DATA` are client-owned reserved variables. The package does not override them in `env`.

Report a credential leak, path escape, command injection, package traversal, or unsafe plugin action through the private process in [`../SECURITY.md`](../SECURITY.md).

## Normative sources

- [Agent Plugins Specification 1.0.0](https://agent-plugins.org/specification)
- [Agent Plugins manifest schema](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json)
- [Agent Plugins MCP schema](https://agent-plugins.org/schemas/1.0.0/mcp.schema.json)
- [Agent Skills specification](https://agentskills.io/specification)
