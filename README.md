# srinitude skills

Portable Agent Skills from one canonical source tree, with a read-only local
MCP server and a per-project injection tool.

This repository is an [Agent Plugins 1.0.0](https://agent-plugins.org/specification)
package of portable skills that follow the [Agent Skills specification](https://agentskills.io/specification).
Every supported client loads the same skill bytes from one canonical tree, so a
skill behaves identically whether it runs in Claude Code, Codex, Gemini CLI,
Cursor, opencode, Continue, Aider, OpenClaw, or Hermes Agent.

[![License: MIT](https://img.shields.io/badge/license-MIT-111111)](LICENSE)
[![Install with skills.sh](https://img.shields.io/badge/skills.sh-install-111111)](https://www.skills.sh/srinitude)

## Scope

The toolkit ships eighteen skills, a bundled read-only MCP server, a validation
and evaluation CLI, and adapters for eleven clients. It is open source under
the MIT License.

What it is:

- A canonical skill tree under `skills/` where each skill owns its body,
  references, scripts, examples, and evaluation inputs.
- A read-only stdio MCP server that exposes six tools for listing, searching,
  reading, and validating skills without network access or credentials.
- A CLI for offline validation, fixture evaluation, speed benchmarking, and
  paid OpenRouter sweeps with explicit spend approval.
- Adapters that point every supported client at the same canonical `SKILL.md`
  path rather than copying a second skill body into each integration.
- A per-project injection script that copies a selected subset of skills into
  a target project with a revert manifest, for teams that do not want a
  global install.

What it is not:

- It is not a hosted service. The MCP server runs locally, reads only from the
  repository skill tree, and has no write tool, telemetry, credentials, or
  network call.
- It is not a wrapper around a language model. Skills are markdown procedures
  and scripts that an agent loads on demand. No skill adds a background
  process or a daemon.
- It is not a placebo. Each skill ships executable validation scripts, worked
  examples with real script output, trigger and behavior evaluations, and
  speed budgets that fail the gate if a run drifts below its recorded baseline.

## Who it is for

- Developers who use AI coding agents (Claude Code, Codex, Gemini CLI, Cursor,
  opencode, Continue, Aider) and want portable, versioned skills that move
  between clients without per-client copies.
- Teams who want to standardize how their agents handle prompt quality, design
  decisions, timeboxed execution, deduplication, and reasoning audits across
  every client they adopt.
- Contributors who want to author new skills against a fixed contract with
  offline validation, schema provenance, and a release pipeline rather than
  hand-editing markdown and hoping it loads.
- Anyone building applications (including APKs and other packaged software)
  who wants a fast, modular skill layer that adds no runtime cost when a skill
  is not loaded.

## Efficiency

The toolkit is designed to add no processing power or time when a skill is not
in use, and minimal cost when it is.

- Skills load on demand. An agent reads a short description from the skill
  frontmatter and loads the full `SKILL.md` body only when a trigger matches.
  References, examples, and scripts load only when the skill body tells the
  agent to load them, so unused detail never enters the context window.
- `SKILL.md` bodies stay under 200 lines. Optional detail moves to
  `references/` with an explicit load condition, which keeps the per-skill
  context footprint small and predictable.
- The `--slim` injection mode copies only `SKILL.md`, `references/`,
  `examples/`, and `scripts/`, dropping evaluation fixtures, local CI, and
  image prompt shards that a consuming project never runs. This is the lowest
  token cost for a project that carries only the skills it uses.
- The MCP server is read-only, stdio, and local. It has no network call, no
  telemetry, no credentials, and no write tool, so it adds no background load.
- Speed budgets per skill fail the local gate if a benchmark run drops below
  its recorded baseline, which prevents silent regressions in runtime cost.

## Install

### Global install (skills.sh)

```sh
npx skills add srinitude/skills
```

Use `npx skills add srinitude/skills --list` to inspect available skills first.
The CLI reports anonymous install telemetry to skills.sh unless
`DISABLE_TELEMETRY=1` is set.

### Per-project injection (no global install)

For a single project, use the injection script to copy a subset of skills in
and revert it later. This adds nothing to your shell profile, global config,
or any registry. It is the recommended path for air-gapped, offline, or
pin-to-commit workflows.

```sh
# from a checkout of this repository
scripts/inject-skills.sh ./my-app --skills timebox,goal-prompt --slim
scripts/inject-skills.sh --revert ./my-app
```

See [Per-project injection](docs/per-project-injection.md) for the full
command reference, safety properties, and pinning instructions.

### Develop in the checkout

Clone the repository and run the local gate:

```sh
git clone https://github.com/srinitude/skills
cd skills
npm ci --include=dev
mise run ci
```

Node 24 or newer is required. [Mise](https://mise.jdx.dev/) pins the full local
toolchain. The local gate runs typecheck, lint, format check, the test suite,
offline skill validation, and fixture evaluation.

## Revert

### Revert a global install

Remove the installed package through the same route you used to install it.

```sh
npx skills remove srinitude/skills
```

For a client marketplace, uninstall through the client plugin UI. Removing the
package removes discovery; it does not modify your project files.

### Revert a per-project injection

```sh
scripts/inject-skills.sh --revert ./my-app
```

Revert reads the manifest at `./my-app/.agent-skills/.inject-manifest.json`,
deletes only the files it lists, prunes the empty directories it created, and
removes the manifest. If you used a custom `--into` folder on inject, pass the
same folder on revert. Revert refuses to delete paths outside the destination
directory, so a hand-edited manifest cannot escape the target.

## Client support

| Client | Route | Local MCP |
| --- | --- | --- |
| MCP-capable Agent Plugins v1 clients | Root portable package | Yes |
| Claude Code | Root plugin and marketplace | Yes |
| Codex | Root plugin and marketplace | Yes |
| ChatGPT | Codex plugin format | Yes |
| Gemini CLI | Root extension | Yes |
| Cursor | Root local plugin | No claim |
| OpenClaw | Root native plugin | Skills only |
| Hermes Agent | Root Python plugin | Skills only |
| opencode | Project config plus skills install | Yes |
| Continue | Skills CLI adapter | Optional |
| Aider | Read-only config | No |

### Claude Code

```text
/plugin marketplace add srinitude/skills
/plugin install srinitude-skills@srinitude-skills
```

The plugin loads `./skills` and `.mcp.json` from the same checkout.

### Codex and ChatGPT

Start Codex with plugin support, open `/plugins`, add `srinitude/skills` as a
marketplace, and install `srinitude-skills`.

```sh
codex --enable plugins
```

The same package metadata is the ChatGPT plugin route documented by the Codex
plugin format.

### Gemini CLI

```sh
gemini extensions install https://github.com/srinitude/skills
```

`gemini-extension.json` starts the bundled MCP server from the installed
extension path.

### Cursor

The root `.cursor-plugin/plugin.json` uses automatic `skills/` discovery. Load
the checkout as a local plugin. This repository does not claim a Cursor
Marketplace listing.

### OpenClaw

Use the tag-pinned native plugin route and cold-discovery check in the
[OpenClaw adapter note](adapters/openclaw/README.md).

### Hermes Agent

Use the Skills Hub tap or optional Python plugin route in the
[Hermes Agent adapter note](adapters/hermes-agent/README.md). Both load the
existing `SKILL.md` path.

### opencode

Use the repository installation above. `opencode.json` starts the local MCP
server when running opencode from this checkout.

### Continue and Aider

Use the [Continue adapter note](adapters/continue/README.md) or
[Aider adapter note](adapters/aider/README.md). Both point to the canonical
`SKILL.md` rather than copying it.

## Local MCP server

Build it with:

```sh
npm run build:mcp
```

The stdio server exposes six read-only tools:

- `list_skills`
- `search_skills`
- `get_skill`
- `get_reference`
- `get_eval_manifest`
- `validate_skill`

Paths are confined to the repository skill tree. Absolute paths, traversal,
hidden files, nested references, and symlink escapes fail closed. The server
has no write tool, telemetry, credentials, or network call.

## Validate and evaluate

```sh
SKILL_NAME=your-skill-name
npm run skills -- validate --all --report .artifacts/skill-validation.json
npm run skills -- eval --skill "$SKILL_NAME" --transport fixture --report ".artifacts/evals/$SKILL_NAME-fixture"
npm run skills -- benchmark --skill "$SKILL_NAME" --transport fixture --samples 1000 --report ".artifacts/benchmarks/$SKILL_NAME-fixture.json"
```

Fixture results prove runner behavior only. They are not evidence about a
language model. Paid OpenRouter evaluation is a separate post-release step
with a frozen model inventory, checkpoint files, a cost estimate, and
explicit spend approval.

Use the fixed-route, capped procedure in [OpenRouter sweeps](docs/openrouter-sweeps.md).

Run the complete local gate with:

```sh
mise run ci
```

## Included skills

| Skill | Purpose |
| --- | --- |
| `always-current-datetime` | Anchor every reply to the current local date and time |
| `by-design` | Run a design-decision gate with a library of execution-time questions |
| `dedupe` | Detect and merge duplicate records across sources |
| `dtcg-tokens` | Extract and validate design token format compliant tokens |
| `goal-prompt` | Package a goal into a plan-ready input prompt |
| `logic-audit` | Audit reasoning for unsupported claims and logical gaps |
| `meaning-preserving-rewrite` | Rewrite prose without changing its meaning |
| `mobile-first-website-design` | Produce mobile-first website design output |
| `outcome-bounded-work` | Bound a task to a measurable outcome before starting |
| `prompt-enhancer` | Enhance a task prompt for clarity and completeness |
| `reify` | Turn an idea into a concrete, decision-ready artifact |
| `simplify-skill` | Simplify a skill body without losing required behavior |
| `skill-factory` | Author a new skill against the repository contract |
| `starting-point` | Choose a starting point for an open-ended request |
| `timebox` | Timebox a task to a deadline and record the outcome |
| `visual-design-system-extractor` | Extract a visual design system from a reference |
| `would-agents-actually` | Test whether an agent would actually use a proposed behavior |
| `would-humans-actually` | Test whether a human would actually use a proposed feature |

## Contribute and report problems

Read [CONTRIBUTING.md](CONTRIBUTING.md) before changing a skill or integration.
The [skills.sh publishing notes](docs/skills-sh.md) record discovery, telemetry,
API, and listing-correction rules. Security reports follow
[SECURITY.md](SECURITY.md). Other help is covered by [SUPPORT.md](SUPPORT.md).

## License

[MIT](LICENSE)
