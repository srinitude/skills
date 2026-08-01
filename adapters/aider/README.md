# Aider adapter

Read a canonical [`SKILL.md`](../../skills/always-current-datetime/SKILL.md) by absolute path from the project where Aider is running. The same route works for every skill in the collection:

```sh
aider --read /absolute/path/to/skills/skills/always-current-datetime/SKILL.md
aider --read /absolute/path/to/skills/skills/logic-audit/SKILL.md
aider --read /absolute/path/to/skills/skills/outcome-bounded-work/SKILL.md
aider --read /absolute/path/to/skills/skills/prime-vector/SKILL.md
aider --read /absolute/path/to/skills/skills/reify/SKILL.md
aider --read /absolute/path/to/skills/skills/starting-point/SKILL.md
aider --read /absolute/path/to/skills/skills/skill-factory/SKILL.md
aider --read /absolute/path/to/skills/skills/visual-design-system-extractor/SKILL.md
aider --read /absolute/path/to/skills/skills/would-agents-actually/SKILL.md
aider --read /absolute/path/to/skills/skills/would-humans-actually/SKILL.md
```

The root [`.aider.conf.yml`](../../.aider.conf.yml) is a checkout-local convenience. Its relative read path works when the current directory is this repository:

```sh
cd /absolute/path/to/skills
aider --config .aider.conf.yml
```

This adapter does not install a plugin or start the MCP server. It adds the skill files as read-only context. Update the root config when another canonical skill is added.
