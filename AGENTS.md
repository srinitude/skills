# Repository rules

## Goal

Build and publish portable Agent Skills from one canonical skill tree.
Every supported client must load the same skill bytes.
This file is the one rule set for the repository and its skills. It merges the
original repository rules with the generation contract that ships inside
`skills/skill-factory/references/generation-contract.md`. Where the two rule
sets conflicted, the generation contract's rule holds, with two exceptions
recorded below: the description limit follows the agentskills.io specification,
and new skills start at `metadata.version: "0.1.0"`.

## Source layout

- `skills/<name>/SKILL.md` owns each skill body.
- Put optional detail in `references/`, executable code in `scripts/`, and evaluation inputs in `evals/`.
- A skill may also bundle `assets/` templates, tests in `scripts/tests/`, and its own `mise.toml` task graph so it verifies itself with its own `mise run ci`.
- Keep file references relative to the skill root and at most one subdirectory deep.
- Don't copy a skill body into a client integration.
- Put generated local output only in `.artifacts/`.

## Skill contract

- Follow every current page listed in `evidence/agentskills-pages.json`.
- Each skill directory name must equal its frontmatter `name`.
- Registry skill names use lowercase letters, digits, and single hyphens. The limit is 64 characters. Skills generated for use outside this registry may use the wider generation-contract pattern `^[a-z0-9][a-z0-9._-]*$`.
- Descriptions are non-empty and at most 1024 characters, the agentskills.io limit.
- Descriptions start with `Use when`, state when the skill applies, and carry the keywords a user would type. They must not summarize the skill's procedure.
- `metadata.author` is `Kiren Srinivasan`.
- New skills start at `metadata.version: "0.1.0"`.
- Each skill owns its version. It must not depend on a package, integration, GitHub release, or another skill version.
- Metadata values are strings.
- Keep `SKILL.md` below 200 lines. Move optional detail out before 150 lines.
- Tell the reader exactly when to load each reference.

## Markdown layout

- Skill markdown uses the one-line layout: every wrappable block, a paragraph or a list item plus its continuation lines, is one physical line with no internal hard breaks and no maximum length.
- Exempt from the one-line rule: YAML frontmatter, headings, table rows, code fences and their content, indented code, and blank lines.
- Blank lines between elements stay exactly as markdown readability requires.
- Repository documents outside `skills/` keep their existing wrapping; do not rewrap them in unrelated changes.

## Writing

- Lead with the result or goal.
- Explain why before a multi-step method.
- Use short sentences and one idea per section.
- Define a technical term the first time it appears.
- Show a full path before using its short form.
- Prefer a concrete example to an abstract claim.
- Use plain words. Cut filler, hedges, and repeated claims.
- Numbers, file names, and commands beat adjectives.
- Don't label readers by ability or background.
- Don't use em dash or en dash characters.
- The banned word and frame lists live in `skills/skill-factory/scripts/lint_writing.py`; skill markdown must pass that lint.
- Keep client and product names inside the integration or install context that needs them. No file under `skills/` names an agent product or a model; describe capabilities instead.

## Test-first work

1. Add or update the focused test.
2. Run it and confirm the expected behavior failure.
3. Add the smallest implementation that passes.
4. Run the focused test again.
5. Run the affected regression task.

For a new skill the build order is fixed: `mise.toml`, then the CI contract tests that pin the task graph, then script tests, then scripts, then docs, then evals.

Mise owns every repeatable command. `mise run ci` is the complete local gate.
Don't add placeholders, skipped tests, mocks in shipped code, or fake passing output.

## Evaluations

Every registry skill ships the repository eval artifact set under `evals/`: `manifest.json`, `cases.json`, `trigger-cases.json`, `contract.md`, `rubric.md`, `speed-budgets.json`, and `source-lineage.json` with real sha256 hashes of the source files and a `public_version` equal to the skill's `metadata.version`. A skill may also ship the skill-local format from the generation contract, `evals.json` plus `trigger-queries.json`; `skill-factory` ships both.

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
