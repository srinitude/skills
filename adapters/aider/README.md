# Aider adapter

Read a canonical `SKILL.md` by absolute path from the project where Aider is running. Replace `<skill-name>` with a name reported by the canonical catalog:

```sh
aider --read /absolute/path/to/skills/skills/<skill-name>/SKILL.md
```

The root [`.aider.conf.yml`](../../.aider.conf.yml) is a checkout-local convenience. Its relative read path works when the current directory is this repository:

```sh
cd /absolute/path/to/skills
aider --config .aider.conf.yml
```

This adapter does not install a plugin or start the MCP server. It adds canonical skill files as read-only context. The root config is checked against the live catalog.
