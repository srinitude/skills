# srinitude skills

Portable Agent Skills from one canonical source tree.

This repository ships `starting-point`, a skill for finding the real outcome, choosing a route, and setting proof before doing the requested work. Its format follows the [Agent Skills specification](https://agentskills.io/specification).

## What ships

- One canonical skill at [`skills/starting-point/SKILL.md`](skills/starting-point/SKILL.md).
- Trigger, behavior, failure, recovery, and speed evaluations.
- A bundled, read-only local MCP server.
- Native plugin metadata or an honest adapter for ten clients.
- Strict JSON Schemas for manifests, reports, benchmarks, and checkpoints.

No client integration contains a second skill body.

GitHub release versions and skill metadata versions are independent. Skills don't depend on each other's versions.

## Install the repository

```sh
git clone https://github.com/srinitude/skills.git
cd skills
npm ci --include=dev
npm run build:mcp
```

Node 24 or newer is required. [Mise](https://mise.jdx.dev/) pins the full local toolchain.

## Client support

| Client       | Route                              | Local MCP   |
| ------------ | ---------------------------------- | ----------- |
| Claude Code  | Root plugin and marketplace        | Yes         |
| Codex        | Root plugin and marketplace        | Yes         |
| ChatGPT      | Codex plugin format                | Yes         |
| Gemini CLI   | Root extension                     | Yes         |
| Cursor       | Root local plugin                  | No claim    |
| OpenClaw     | Root native plugin                 | Skills only |
| Hermes Agent | Root Python plugin                 | Skills only |
| opencode     | Project config plus skills install | Yes         |
| Continue     | Skills CLI adapter                 | Optional    |
| Aider        | Read-only config                   | No          |

### Claude Code

```text
/plugin marketplace add srinitude/skills
/plugin install srinitude-skills@srinitude-skills
```

The plugin loads [`./skills`](skills/) and [`.mcp.json`](.mcp.json) from the same checkout.

### Codex and ChatGPT

Start Codex with plugin support, open `/plugins`, add `srinitude/skills` as a marketplace, and install `srinitude-skills`.

```sh
codex --enable plugins
```

The same package metadata is the ChatGPT plugin route documented by the Codex plugin format.

### Gemini CLI

```sh
gemini extensions install https://github.com/srinitude/skills
```

[`gemini-extension.json`](gemini-extension.json) starts the bundled MCP server from the installed extension path.

### Cursor

The root [`.cursor-plugin/plugin.json`](.cursor-plugin/plugin.json) uses automatic `skills/` discovery. Load the checkout as a local plugin. This repository does not claim a Cursor Marketplace listing.

### OpenClaw

Use the tag-pinned native plugin route and cold-discovery check in the [OpenClaw adapter note](adapters/openclaw/README.md).

### Hermes Agent

Use the Skills Hub tap or optional Python plugin route in the [Hermes Agent adapter note](adapters/hermes-agent/README.md). Both load the existing SKILL.md path.

### opencode

Install the skill with the skills CLI. Use [`opencode.json`](opencode.json) when running opencode from this checkout to start the local MCP server.

```sh
npx skills add srinitude/skills
```

### Continue and Aider

Use the [Continue adapter note](adapters/continue/README.md) or [Aider adapter note](adapters/aider/README.md). Both point to the canonical SKILL.md rather than copying it.

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

Paths are confined to the repository skill tree. Absolute paths, traversal, hidden files, nested references, and symlink escapes fail closed. The server has no write tool, telemetry, credentials, or network call.

## Validate and evaluate

```sh
npm run skills -- validate --all --report .artifacts/skill-validation.json
npm run skills -- eval starting-point --transport fixture --report .artifacts/evals/starting-point-fixture
npm run skills -- benchmark starting-point --transport fixture --samples 1000 --report .artifacts/benchmarks/starting-point-fixture.json
```

Fixture results prove runner behavior only. They are not evidence about a language model. Paid OpenRouter evaluation is a separate post-release step with a frozen model inventory, checkpoint files, a cost estimate, and explicit spend approval.

Use the fixed-route, capped procedure in [OpenRouter sweeps](docs/openrouter-sweeps.md).

Run the complete local gate with:

```sh
mise run ci
```

## Contribute and report problems

Read [CONTRIBUTING.md](CONTRIBUTING.md) before changing a skill or integration. Security reports follow [SECURITY.md](SECURITY.md). Other help is covered by [SUPPORT.md](SUPPORT.md).

## License

[MIT](LICENSE)
