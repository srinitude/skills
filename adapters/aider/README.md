# Aider adapter

Read the canonical [`SKILL.md`](../../skills/starting-point/SKILL.md) by absolute path from the project where Aider is running:

```sh
aider --read /absolute/path/to/skills/skills/starting-point/SKILL.md
```

The root [`.aider.conf.yml`](../../.aider.conf.yml) is a checkout-local convenience. Its relative read path works when the current directory is this repository:

```sh
cd /absolute/path/to/skills
aider --config .aider.conf.yml
```

This adapter does not install a plugin or start the MCP server. It adds the skill file as read-only context. Update the root config when another canonical skill is added.
