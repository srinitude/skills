# Changelog

All notable changes to this project are recorded here.

## Unreleased

- Added the `skill-factory` Agent Skill at `metadata.version: "0.1.0"` with the full registry eval artifact set and source-lineage hashes.
- Unified the repository rules and the skill-factory generation contract in `AGENTS.md`.
- Raised the skill description limit to the 1024-character agentskills.io specification limit; descriptions still start with `Use when`.
- Adopted the one-line markdown layout for skill markdown and applied it to `starting-point`.
- Kept `starting-point` at `metadata.version: "0.1.0"`.
- Added the platform-neutral `reify` skill with frozen source lineage.
- Added trigger, behavior, failure, recovery, and speed evaluations for `reify`.
- Updated package, plugin, MCP, skills.sh, Aider, Continue, and Hermes Agent discovery routes.

## GitHub release 0.1.2

- Allowed verified zero-cost routes through the full ledger path.
- Added durable pending records that block automatic repayment after an ambiguous failure.
- Released rejected-request reservations only when route metadata proves no provider attempt occurred.
- Blocked unknown-price requests before creating a ledger reservation.
- Kept every skill version unchanged.

## GitHub release 0.1.1

- Added a fixed-route, capped, resumable OpenRouter sweep runner.
- Added manifest-bound user approval and first-party route and cost checks.
- Removed repository validation that tied skill versions to the package version.
- Kept `starting-point` at `metadata.version: "0.1.0"`.

## 0.1.0

Initial public package.

- Added the `starting-point` Agent Skill with source-lineage evidence.
- Added positive, rejection, behavior, failure, recovery, and speed evaluations.
- Added strict validators and JSON Schemas.
- Added a bundled read-only MCP server.
- Added plugin or adapter routes for ten clients.
- Added deterministic package and copy checks.
