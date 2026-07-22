import { readFile, realpath } from 'node:fs/promises';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { parse as parseYaml } from 'yaml';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));

async function json(path: string): Promise<Record<string, unknown>> {
  return JSON.parse(await readFile(resolve(root, path), 'utf8')) as Record<string, unknown>;
}

async function yaml(path: string): Promise<Record<string, unknown>> {
  return parseYaml(await readFile(resolve(root, path), 'utf8')) as Record<string, unknown>;
}

async function expectInside(path: string): Promise<void> {
  const target = await realpath(resolve(root, path));
  expect(relative(await realpath(root), target)).not.toMatch(/^\.\.(?:\/|$)/);
}

test('Codex and ChatGPT plugin point to canonical skills and MCP config', async () => {
  const manifest = await json('.codex-plugin/plugin.json');
  expect(manifest).toMatchObject({
    description: 'Portable Agent Skills and read-only local tools.',
    license: 'MIT',
    name: 'srinitude-skills',
    skills: './skills/',
    version: '0.1.0',
  });
  expect(manifest.mcpServers).toBe('./.mcp.json');
  await expectInside('skills');
  await expectInside('.mcp.json');
});

test('Claude Code plugin points to canonical skills and MCP config', async () => {
  const manifest = await json('.claude-plugin/plugin.json');
  expect(manifest).toMatchObject({
    license: 'MIT',
    name: 'srinitude-skills',
    skills: './skills/',
    version: '0.1.0',
  });
  expect(manifest.mcpServers).toBe('./.mcp.json');
  await expectInside('skills');
  await expectInside('.mcp.json');
});

test('shared plugin MCP config uses the documented compatibility variable', async () => {
  const config = await json('.mcp.json');
  expect(config).toEqual({
    mcpServers: {
      'srinitude-skills': {
        args: ['${CLAUDE_PLUGIN_ROOT}/mcp/dist/server.mjs'],
        command: 'node',
      },
    },
  });
});

test('Cursor plugin uses automatic canonical skill discovery', async () => {
  const manifest = await json('.cursor-plugin/plugin.json');
  expect(manifest).toMatchObject({
    description: 'Portable Agent Skills from one canonical tree.',
    name: 'srinitude-skills',
    version: '0.1.0',
  });
  expect(manifest.skills).toBeUndefined();
  expect(manifest.mcpServers).toBeUndefined();
  await expectInside('skills');
});

test('Gemini CLI extension uses canonical skills and its extension path', async () => {
  const manifest = await json('gemini-extension.json');
  expect(manifest).toMatchObject({
    description: 'Portable Agent Skills and read-only local tools.',
    name: 'srinitude-skills',
    version: '0.1.0',
  });
  expect(manifest.mcpServers).toEqual({
    'srinitude-skills': {
      args: ['${extensionPath}/mcp/dist/server.mjs'],
      command: 'node',
      cwd: '${extensionPath}',
    },
  });
  expect(manifest.settings).toBeUndefined();
  await expectInside('skills');
});

test('opencode adapter starts the bundled read-only server', async () => {
  const config = await json('opencode.json');
  expect(config).toEqual({
    $schema: 'https://opencode.ai/config.json',
    mcp: {
      'srinitude-skills': {
        command: ['node', 'mcp/dist/server.mjs'],
        cwd: '.',
        enabled: true,
        type: 'local',
      },
    },
  });
});

test('Aider adapter reads the canonical skill without copying it', async () => {
  expect(await yaml('.aider.conf.yml')).toEqual({
    read: ['skills/starting-point/SKILL.md', 'skills/skill-factory/SKILL.md'],
  });
  await expectInside('skills/starting-point/SKILL.md');
  await expectInside('skills/skill-factory/SKILL.md');
});

test('publishes Claude Code and Codex marketplace indexes', async () => {
  const claude = await json('.claude-plugin/marketplace.json');
  expect(claude).toMatchObject({
    description: 'Portable Agent Skills from srinitude.',
    name: 'srinitude-skills',
    plugins: [{ name: 'srinitude-skills', source: './', version: '0.1.0' }],
  });

  const codex = await json('.agents/plugins/marketplace.json');
  expect(codex).toMatchObject({
    name: 'srinitude-skills',
    plugins: [
      {
        name: 'srinitude-skills',
        source: { path: './', source: 'local' },
      },
    ],
  });
});

test('groups canonical skills for skills-hub clients', async () => {
  expect(await json('skills.sh.json')).toEqual({
    $schema: 'https://skills.sh/schemas/skills.sh.schema.json',
    groupings: [
      { skills: ['starting-point'], title: 'Planning' },
      { skills: ['skill-factory'], title: 'Skill Authoring' },
    ],
  });
});
