# Repository rules

## Goal

Build and publish portable Agent Skills from one canonical skill tree.
Every supported client must load the same skill bytes.

## Source layout

- `skills/<name>/SKILL.md` owns each skill body.
- Put optional detail in `references/`, executable code in `scripts/`, and evaluation inputs in `evals/`.
- Keep file references relative to the skill root and one level deep.
- Don't copy a skill body into a client integration.
- Put generated local output only in `.artifacts/`.

## Skill contract

- Follow every current page listed in `evidence/agentskills-pages.json`.
- Each skill directory name must equal its frontmatter `name`.
- Names use lowercase letters, digits, and single hyphens. The limit is 64 characters.
- Descriptions must be non-empty and fewer than 60 characters.
- Descriptions state when the skill applies and must not summarize its procedure.
- `metadata.author` is `Kiren Srinivasan`.
- New skills start at `metadata.version: "0.1.0"`.
- Each skill owns its version. It must not depend on a package, integration, GitHub release, or another skill version.
- Metadata values are strings.
- Keep `SKILL.md` below 200 lines. Move optional detail out before 150 lines.
- Tell the reader exactly when to load each reference.

## Writing

- Lead with the result or goal.
- Explain why before a multi-step method.
- Use short sentences and one idea per section.
- Define a technical term the first time it appears.
- Show a full path before using its short form.
- Prefer a concrete example to an abstract claim.
- Use plain words. Cut filler and repeated claims.
- Don't label readers by ability or background.
- Don't use em dash or en dash characters.
- Keep client and product names inside the integration or install context that needs them.

## Test-first work

1. Add or update the focused test.
2. Run it and confirm the expected behavior failure.
3. Add the smallest implementation that passes.
4. Run the focused test again.
5. Run the affected regression task.

Mise owns every repeatable command. `mise run ci` is the complete local gate.
Don't add placeholders, skipped tests, or fake passing output.

## Evaluations

Each skill must test:

- positive activation
- rejection and near-neighbor prompts
- required behavior
- forbidden behavior
- failure handling
- recovery
- with-skill and without-skill conditions
- cold and warm speed

Record discovery, full-load, task, and transport timing separately.
A component PASS never proves the full package.

## Local MCP server

- Use stdio transport.
- Keep every tool read-only and path-confined.
- Reject absolute paths, traversal, hidden files, and symlink escapes.
- Write protocol data to stdout and diagnostics to stderr.
- Make unknown names and invalid input fail with stable error codes.
- Don't add telemetry, credentials, network calls, hosted transport, or write tools.

## Integrations

- Claim native support only when a current first-party format exists.
- Label path installs, MCP configuration, and read-only adapters honestly.
- Resolve every integration to canonical skill bytes.
- Keep client-specific rules in that integration's directory.

## Source control

- Use `Kiren Srinivasan <kiren@fantasymetals.com>` for commits.
- Don't add generated attribution or co-author trailers.
- Don't commit credentials, `.env` files, temporary homes, reports, or paid-run output.
- A release requires two clean local CI passes and passing remote CI.
