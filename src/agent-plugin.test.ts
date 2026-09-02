import { cp, mkdir, mkdtemp, readFile, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { afterEach, expect, test } from 'vitest';

import { validateAgentPlugin } from './agent-plugin.js';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const temporary: string[] = [];
const pluginSchema = 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json';
const mcpSchema = 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json';

function pluginManifest(extra: Record<string, unknown> = {}): Record<string, unknown> {
  return { $schema: pluginSchema, name: 'fixture-plugin', ...extra };
}

function mcpManifest(): Record<string, unknown> {
  return {
    $schema: mcpSchema,
    mcpServers: {
      fixture: {
        args: ['${PLUGIN_ROOT}/mcp/dist/server.mjs'],
        command: 'node',
        cwd: '${PLUGIN_ROOT}',
        type: 'stdio',
      },
    },
  };
}

async function json(path: string, value: unknown): Promise<void> {
  await writeFile(path, `${JSON.stringify(value, null, 2)}\n`);
}

async function fixture(): Promise<string> {
  const target = await mkdtemp(join(tmpdir(), 'agent-plugin-'));
  temporary.push(target);
  await mkdir(join(target, 'skills', 'sample'), { recursive: true });
  await mkdir(join(target, 'mcp', 'dist'), { recursive: true });
  await cp(
    join(root, 'schemas', 'agent-plugins'),
    join(target, 'schemas', 'agent-plugins'),
    {
      recursive: true,
    },
  );
  await mkdir(join(target, 'evidence'), { recursive: true });
  await cp(
    join(root, 'evidence', 'agent-plugins-v1.json'),
    join(target, 'evidence', 'agent-plugins-v1.json'),
  );
  await json(join(target, 'plugin.json'), pluginManifest());
  await json(join(target, 'mcp.json'), mcpManifest());
  await writeFile(
    join(target, 'skills', 'sample', 'SKILL.md'),
    '---\nname: sample\ndescription: Use when testing.\n---\n',
  );
  await writeFile(join(target, 'mcp', 'dist', 'server.mjs'), 'export {};\n');
  return target;
}

afterEach(async () => {
  await Promise.all(
    temporary.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

test('validates the repository as an Agent Plugins 1.0.0 package', async () => {
  const report = await validateAgentPlugin(root);

  expect(report.status, report.findings.map((finding) => finding.message).join('\n')).toBe(
    'PASS',
  );
  expect(report.skills).toHaveLength(22);
  expect(report.servers).toEqual(['srinitude-skills']);
  expect(report.schema_version).toBe('1.0.0');
});

test('keeps the portable documents at the reviewed package contract', async () => {
  expect(JSON.parse(await readFile(join(root, 'plugin.json'), 'utf8'))).toEqual({
    $schema: pluginSchema,
    author: {
      email: 'kiren@fantasymetals.com',
      name: 'Kiren Srinivasan',
      url: 'https://github.com/srinitude',
    },
    description: 'Portable Agent Skills and read-only local tools.',
    homepage: 'https://github.com/srinitude/skills',
    keywords: ['agent-plugins', 'agent-skills', 'mcp', 'workflow'],
    license: 'MIT',
    name: 'srinitude-skills',
    repository: 'https://github.com/srinitude/skills',
    version: '0.1.0',
  });
  expect(JSON.parse(await readFile(join(root, 'mcp.json'), 'utf8'))).toEqual({
    $schema: mcpSchema,
    mcpServers: {
      'srinitude-skills': {
        args: ['${PLUGIN_ROOT}/mcp/dist/server.mjs'],
        command: 'node',
        cwd: '${PLUGIN_ROOT}',
        type: 'stdio',
      },
    },
  });
});

test('rejects plugin manifest fields outside the canonical schema', async () => {
  const target = await fixture();
  await json(join(target, 'plugin.json'), pluginManifest({ unknown: true }));

  const report = await validateAgentPlugin(target);

  expect(report.status).toBe('FAIL');
  expect(report.findings.map((finding) => finding.code)).toContain('PLUGIN_SCHEMA');
});

test('reports one malformed skill without dropping a valid sibling', async () => {
  const target = await fixture();
  await mkdir(join(target, 'skills', 'broken'));

  const report = await validateAgentPlugin(target);

  expect(report.status).toBe('FAIL');
  expect(report.skills).toEqual(['sample']);
  expect(report.findings.map((finding) => finding.code)).toContain(
    'SKILL_DOCUMENT_MISSING',
  );
});

test('rejects a bundled server symlink that escapes the plugin root', async () => {
  const target = await fixture();
  const outside = join(target, '..', `${target.split('/').at(-1)}-outside.mjs`);
  temporary.push(outside);
  await writeFile(outside, 'export {};\n');
  await rm(join(target, 'mcp', 'dist', 'server.mjs'));
  await symlink(outside, join(target, 'mcp', 'dist', 'server.mjs'));

  const report = await validateAgentPlugin(target);

  expect(report.status).toBe('FAIL');
  expect(report.findings.map((finding) => finding.code)).toContain('PATH_ESCAPE');
});

test('rejects portable document symlinks that escape the plugin root', async () => {
  for (const file of ['plugin.json', 'mcp.json']) {
    const target = await fixture();
    const outside = join(target, '..', `${target.split('/').at(-1)}-${file}`);
    temporary.push(outside);
    await cp(join(target, file), outside);
    await rm(join(target, file));
    await symlink(outside, join(target, file));

    const report = await validateAgentPlugin(target);

    expect(report.status).toBe('FAIL');
    expect(report.findings.map((finding) => finding.code)).toContain('PATH_ESCAPE');
  }
});

test('rejects an absolute working directory outside the plugin root', async () => {
  const target = await fixture();
  const config = mcpManifest() as {
    mcpServers: Record<string, Record<string, unknown>>;
  };
  config.mcpServers.fixture = { ...config.mcpServers.fixture, cwd: dirname(target) };
  await json(join(target, 'mcp.json'), config);

  const report = await validateAgentPlugin(target);

  expect(report.status).toBe('FAIL');
  expect(report.findings.map((finding) => finding.code)).toContain('PATH_ESCAPE');
});

test('detects a vendored schema that no longer matches its source record', async () => {
  const target = await fixture();
  const path = join(target, 'schemas', 'agent-plugins', '1.0.0', 'plugin.schema.json');
  await writeFile(path, `${await readFile(path, 'utf8')}\n`);

  const report = await validateAgentPlugin(target);

  expect(report.status).toBe('FAIL');
  expect(report.findings.map((finding) => finding.code)).toContain('SCHEMA_DIGEST');
});
