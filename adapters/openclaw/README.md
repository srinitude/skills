# OpenClaw plugin

The root [`openclaw.plugin.json`](../../openclaw.plugin.json) is the native plugin manifest. Its `skills` field points to [`./skills`](../../skills/), so OpenClaw reads the canonical bytes.

Install and enable the native plugin:

```sh
openclaw plugins install git:github.com/srinitude/skills@v0.1.0
openclaw plugins enable srinitude-skills
openclaw plugins inspect srinitude-skills --json
```

The manifest declares no configuration property and no code extension. It supplies skills only. The repository MCP server is separate.
