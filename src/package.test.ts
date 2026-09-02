import { access, mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterEach, expect, test } from 'vitest';

import { loadCatalog } from './catalog.js';
import { buildPackage, packOutput } from './package.js';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const temporary: string[] = [];

test('accepts npm pack array and keyed-object payloads', () => {
  expect(packOutput([{ filename: 'legacy.tgz' }])).toEqual({ filename: 'legacy.tgz' });
  expect(packOutput({ '@srinitude/skills': { filename: 'current.tgz' } })).toEqual({
    filename: 'current.tgz',
  });
  expect(packOutput({})).toBeUndefined();
});

test('declares no runtime dependencies for the self-contained archive', async () => {
  const manifest = JSON.parse(await readFile(join(root, 'package.json'), 'utf8')) as {
    dependencies?: Record<string, string>;
  };
  expect(manifest.dependencies).toBeUndefined();
});

afterEach(async () => {
  await Promise.all(
    temporary.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

test('builds a safe package with canonical skills and client manifests', async () => {
  const destination = await mkdtemp(join(tmpdir(), 'skills-package-'));
  temporary.push(destination);
  const result = await buildPackage(root, destination);
  const expectedSkills = (await loadCatalog(root)).map((entry) => `package/${entry.path}`);

  expect(result.sha256).toMatch(/^[a-f0-9]{64}$/);
  expect(result.entries.filter((entry) => entry.endsWith('/SKILL.md'))).toEqual(
    expectedSkills,
  );
  expect(result.entries).toEqual(
    expect.arrayContaining([
      'package/.agents/plugins/marketplace.json',
      'package/.claude-plugin/marketplace.json',
      'package/.claude-plugin/plugin.json',
      'package/.codex-plugin/plugin.json',
      'package/.cursor-plugin/plugin.json',
      'package/docs/openrouter-sweeps.md',
      'package/evidence/agent-plugins-v1.json',
      'package/evidence/skills-sh-pages.json',
      'package/gemini-extension.json',
      'package/mcp.json',
      'package/plugin.json',
      'package/plugin.yaml',
      'package/mcp/dist/server.mjs',
      'package/schemas/agent-plugins/1.0.0/mcp.schema.json',
      'package/schemas/agent-plugins/1.0.0/plugin.schema.json',
    ]),
  );
  expect(result.entries.some((entry) => entry.includes('../'))).toBe(false);
  expect(result.entries.some((entry) => entry.includes('.test.'))).toBe(false);
  expect(result.entries.some((entry) => entry.includes('/scripts/tests/'))).toBe(false);
  expect(result.entries.some((entry) => entry.startsWith('package/evidence/ports/'))).toBe(
    false,
  );
  expect(result.entries.some((entry) => entry.includes('__pycache__'))).toBe(false);
  expect(result.entries.some((entry) => entry.endsWith('.pyc'))).toBe(false);
  expect(result.entries).not.toContain('package/CLAUDE.md');
  expect(result.entries).not.toContain('package/openclaw.plugin.json');
  expect(result.symlinks).toEqual([]);
  const bundle = await readFile(join(root, 'mcp', 'dist', 'server.mjs'), 'utf8');
  expect(bundle).not.toContain('sourceMappingURL=');
  await expect(access(join(root, 'mcp', 'dist', 'server.mjs.map'))).rejects.toMatchObject({
    code: 'ENOENT',
  });
}, 30_000);

test('produces identical archive and MCP bytes in consecutive builds', async () => {
  const first = await mkdtemp(join(tmpdir(), 'skills-package-'));
  const second = await mkdtemp(join(tmpdir(), 'skills-package-'));
  temporary.push(first, second);
  const left = await buildPackage(root, first);
  const right = await buildPackage(root, second);
  expect(left.sha256).toBe(right.sha256);
  expect(left.mcp_sha256).toBe(right.mcp_sha256);
  expect(left.entries).toEqual(right.entries);
}, 30_000);
