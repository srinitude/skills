# Hermes Agent plugin

The Skills Hub tap is the primary route for this skill collection. [`skills.sh.json`](../../skills.sh.json) groups the canonical [`reify`](../../skills/reify/SKILL.md), [`starting-point`](../../skills/starting-point/SKILL.md), and [`skill-factory`](../../skills/skill-factory/SKILL.md) skills.

```sh
hermes skills tap add srinitude/skills
hermes skills install srinitude/skills/reify
hermes skills install srinitude/skills/starting-point
hermes skills install srinitude/skills/skill-factory
```

The repository root is also a native Python plugin. [`plugin.yaml`](../../plugin.yaml) declares it, and [`__init__.py`](../../__init__.py) registers the canonical skill path.

```sh
hermes plugins install srinitude/skills
hermes plugins enable srinitude-skills
```

The plugin claims no tools or hooks. It registers skill paths only. Namespacing is applied by the client at load time. The repository MCP server is a separate adapter.
