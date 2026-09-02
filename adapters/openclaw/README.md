# OpenClaw adapter

OpenClaw loads this repository as a Codex-compatible bundle. Under OpenClaw's documented detection order, `.codex-plugin/plugin.json` takes precedence over the root [`plugin.json`](../../plugin.json). That manifest discovers every canonical child under [`skills/`](../../skills/) and points MCP to `.mcp.json`.

Install and inspect the release-pinned bundle:

```sh
openclaw plugins install git:github.com/srinitude/skills@<release-tag>
openclaw plugins enable srinitude-skills
openclaw plugins inspect srinitude-skills --json
```

Use the current GitHub release tag. The Codex plugin manifest version is a separate compatibility axis. This adapter adds no native OpenClaw runtime module. The bundle supplies canonical skills and the read-only MCP server declared by [`.mcp.json`](../../.mcp.json).
