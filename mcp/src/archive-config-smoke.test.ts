import { execFile } from 'node:child_process';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

import { afterEach, expect, test } from 'vitest';

import { loadCatalog } from '../../src/catalog.js';
import { buildPackage } from '../../src/package.js';
import { loadMcpConfigs, probeMcp } from './config-smoke.js';

const execFileAsync = promisify(execFile);
const root = dirname(dirname(dirname(fileURLToPath(import.meta.url))));
const temporary: string[] = [];

afterEach(async () => {
  await Promise.all(
    temporary.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

test('starts every declared MCP route from packaged canonical bytes', async () => {
  const destination = await mkdtemp(join(tmpdir(), 'skills-mcp-archive-'));
  temporary.push(destination);
  const packaged = await buildPackage(root, destination);
  await execFileAsync('tar', ['-xf', packaged.tarball, '-C', destination]);
  const archiveRoot = join(destination, 'package');
  const configs = await loadMcpConfigs(archiveRoot);
  const catalog = await loadCatalog(archiveRoot);
  const expectedResources = await Promise.all(
    catalog.map(async (entry) => ({
      description: entry.description,
      mimeType: 'text/markdown',
      name: `skill-${entry.name}`,
      text: await readFile(join(archiveRoot, entry.path), 'utf8'),
      title: entry.name,
      uri: `skill://${entry.name}/SKILL.md`,
    })),
  );
  const expectedTools = [
    'get_eval_manifest',
    'get_reference',
    'get_skill',
    'list_skills',
    'search_skills',
    'validate_skill',
  ];

  expect(configs.map((config) => config.id)).toEqual([
    'agent-plugins-v1',
    'claude-codex-shared',
    'gemini-extension',
    'opencode',
  ]);
  for (const config of configs) {
    const proof = await probeMcp(config);
    expect(proof.toolNames).toEqual(expectedTools);
    expect(proof.resourceCount).toBe(22);
    expect(proof.resources).toEqual(expectedResources);
    expect(proof.annotationsValid).toBe(true);
  }
  const packagedSkill = await readFile(
    join(archiveRoot, 'skills', 'starting-point', 'SKILL.md'),
  );
  const canonicalSkill = await readFile(join(root, 'skills', 'starting-point', 'SKILL.md'));
  expect(packagedSkill).toEqual(canonicalSkill);
}, 30_000);
