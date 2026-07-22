# Continue adapter

Install the canonical skill through the skills CLI:

```sh
npx skills add srinitude/skills
```

Select Continue when the installer asks for a target. Verify that the installed bytes match [`skills/starting-point/SKILL.md`](../../skills/starting-point/SKILL.md) and [`skills/skill-factory/SKILL.md`](../../skills/skill-factory/SKILL.md).

Continue does not have a repository plugin manifest in this package. To use the local MCP server, add a stdio server in Continue with command `node` and the absolute path to `mcp/dist/server.mjs` as its first argument.
