# Contributing

Changes must keep one canonical skill tree and preserve every tested client route.

## Before changing code or Markdown

1. Install the pinned tools with `mise install`.
2. Install dependencies with `npm ci --include=dev`.
3. Read `AGENTS.md`.
4. Find the focused test that owns the behavior.

## Test-first sequence

1. Add or update the focused test.
2. Run it and confirm the expected failure.
3. Add the smallest implementation that passes.
4. Run the focused test again.
5. Run the affected Mise task.
6. Run `mise run ci` before opening a pull request.

Do not add skipped tests, placeholder output, or generated attribution.

## Skill rules

Each `skills/<name>/SKILL.md` must:

- use the same name as its directory;
- have a description shorter than 60 characters;
- use `Kiren Srinivasan` as `metadata.author`;
- start at version `0.1.0` when new;
- stay below 200 lines;
- point to optional detail one level below the skill root;
- include positive, rejection, behavior, failure, recovery, and speed tests.

Update `evidence/agentskills-pages.json` only after reading every page listed by the live Agent Skills sitemap.

## Integrations

A client manifest must point to `skills/` or the bundled MCP server. Do not copy a skill body into a plugin, adapter, fixture, or package.

Claim native support only when a current first-party format exists. Label local adapters and marketplace status directly.

## MCP changes

Keep the server on stdio. Tools must remain read-only and path-confined. Reject absolute paths, traversal, hidden paths, nested references, and symlink escapes. Protocol data goes to stdout. Diagnostics go to stderr.

## Pull requests

Describe the behavior change, the focused RED and GREEN commands, and the whole-package result separately. Do not commit `.artifacts/`, temporary homes, credentials, or paid evaluation output.
