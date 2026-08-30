import { access, mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterEach, expect, test } from 'vitest';

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
  expect(result.entries).toContain('package/skills/always-current-datetime/SKILL.md');
  expect(result.entries).toContain('package/skills/dedupe/SKILL.md');
  expect(result.entries).toContain('package/skills/design-like-im-5/SKILL.md');
  expect(result.entries).toContain('package/skills/dtcg-tokens/SKILL.md');
  expect(result.entries).toContain('package/skills/goal-prompt/SKILL.md');
  expect(result.entries).toContain('package/skills/logic-audit/SKILL.md');
  expect(result.entries).toContain('package/skills/meaning-preserving-rewrite/SKILL.md');
  expect(result.entries).toContain('package/skills/mobile-first-website-design/SKILL.md');
  expect(result.entries).toContain('package/skills/only-one-interpretation/SKILL.md');
  expect(result.entries).toContain('package/skills/outcome-bounded-work/SKILL.md');
  expect(result.entries).toContain('package/skills/prompt-enhancer/SKILL.md');
  expect(result.entries).toContain('package/skills/by-design/SKILL.md');
  expect(result.entries).toContain('package/skills/reify/SKILL.md');
  expect(result.entries).toContain('package/skills/simplify-skill/SKILL.md');
  expect(result.entries).toContain('package/skills/starting-point/SKILL.md');
  expect(result.entries).toContain('package/skills/skill-factory/SKILL.md');
  expect(result.entries).toContain('package/skills/timebox/SKILL.md');
  expect(result.entries).toContain('package/skills/tool-call-configuration-for/SKILL.md');
  expect(result.entries).toContain(
    'package/skills/visual-design-system-extractor/SKILL.md',
  );
  expect(result.entries).toContain('package/skills/would-agents-actually/SKILL.md');
  expect(result.entries).toContain('package/skills/would-humans-actually/SKILL.md');
  expect(result.entries.filter((entry) => entry.endsWith('/SKILL.md'))).toEqual([
    'package/skills/always-current-datetime/SKILL.md',
    'package/skills/by-design/SKILL.md',
    'package/skills/dedupe/SKILL.md',
    'package/skills/design-like-im-5/SKILL.md',
    'package/skills/dtcg-tokens/SKILL.md',
    'package/skills/goal-prompt/SKILL.md',
    'package/skills/logic-audit/SKILL.md',
    'package/skills/meaning-preserving-rewrite/SKILL.md',
    'package/skills/mobile-first-website-design/SKILL.md',
    'package/skills/only-one-interpretation/SKILL.md',
    'package/skills/outcome-bounded-work/SKILL.md',
    'package/skills/prompt-enhancer/SKILL.md',
    'package/skills/reify/SKILL.md',
    'package/skills/simplify-skill/SKILL.md',
    'package/skills/skill-factory/SKILL.md',
    'package/skills/starting-point/SKILL.md',
    'package/skills/timebox/SKILL.md',
    'package/skills/tool-call-configuration-for/SKILL.md',
    'package/skills/visual-design-system-extractor/SKILL.md',
    'package/skills/would-agents-actually/SKILL.md',
    'package/skills/would-humans-actually/SKILL.md',
  ]);
  expect(result.entries).toEqual(
    expect.arrayContaining([
      'package/.agents/plugins/marketplace.json',
      'package/.claude-plugin/marketplace.json',
      'package/.claude-plugin/plugin.json',
      'package/.codex-plugin/plugin.json',
      'package/.cursor-plugin/plugin.json',
      'package/docs/openrouter-sweeps.md',
      'package/evidence/agent-plugins-v1.json',
      'package/gemini-extension.json',
      'package/mcp.json',
      'package/openclaw.plugin.json',
      'package/plugin.json',
      'package/plugin.yaml',
      'package/mcp/dist/server.mjs',
      'package/schemas/agent-plugins/1.0.0/mcp.schema.json',
      'package/schemas/agent-plugins/1.0.0/plugin.schema.json',
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
}, 30_000);

test('produces identical MCP bundle bytes in consecutive builds', async () => {
  const first = await mkdtemp(join(tmpdir(), 'skills-package-'));
  const second = await mkdtemp(join(tmpdir(), 'skills-package-'));
  temporary.push(first, second);
  const left = await buildPackage(root, first);
  const right = await buildPackage(root, second);
  expect(left.mcp_sha256).toBe(right.mcp_sha256);
}, 30_000);
