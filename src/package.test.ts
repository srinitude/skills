import { access, mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterEach, expect, test } from 'vitest';

import { buildPackage } from './package.js';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const temporary: string[] = [];

afterEach(async () => {
  await Promise.all(
    temporary.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

test('builds a safe package with canonical skills and client manifests', async () => {
  const destination = await mkdtemp(join(tmpdir(), 'skills-package-'));
  temporary.push(destination);
  const result = await buildPackage(root, destination);

  expect(result.sha256).toMatch(/^[a-f0-9]{64}$/);
  expect(result.entries).toContain('package/skills/reify/SKILL.md');
  expect(result.entries).toContain('package/skills/starting-point/SKILL.md');
  expect(result.entries).toContain('package/skills/skill-factory/SKILL.md');
  expect(result.entries.filter((entry) => entry.endsWith('/SKILL.md'))).toEqual([
    'package/skills/reify/SKILL.md',
    'package/skills/skill-factory/SKILL.md',
    'package/skills/starting-point/SKILL.md',
  ]);
  expect(result.entries).toEqual(
    expect.arrayContaining([
      'package/.agents/plugins/marketplace.json',
      'package/.claude-plugin/marketplace.json',
      'package/.claude-plugin/plugin.json',
      'package/.codex-plugin/plugin.json',
      'package/.cursor-plugin/plugin.json',
      'package/docs/openrouter-sweeps.md',
      'package/gemini-extension.json',
      'package/openclaw.plugin.json',
      'package/plugin.yaml',
      'package/mcp/dist/server.mjs',
    ]),
  );
  expect(result.entries.some((entry) => entry.includes('../'))).toBe(false);
  expect(result.entries.some((entry) => entry.includes('.test.'))).toBe(false);
  expect(result.entries).not.toContain('package/CLAUDE.md');
  expect(result.symlinks).toEqual([]);
  const bundle = await readFile(join(root, 'mcp', 'dist', 'server.mjs'), 'utf8');
  expect(bundle).not.toContain('sourceMappingURL=');
  await expect(access(join(root, 'mcp', 'dist', 'server.mjs.map'))).rejects.toMatchObject({
    code: 'ENOENT',
  });
});

test('produces identical MCP bundle bytes in consecutive builds', async () => {
  const first = await mkdtemp(join(tmpdir(), 'skills-package-'));
  const second = await mkdtemp(join(tmpdir(), 'skills-package-'));
  temporary.push(first, second);
  const left = await buildPackage(root, first);
  const right = await buildPackage(root, second);
  expect(left.mcp_sha256).toBe(right.mcp_sha256);
});
