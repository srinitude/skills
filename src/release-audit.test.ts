import { execFile } from 'node:child_process';
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';

import { expect, test } from 'vitest';

import { auditRepository } from './release-audit.js';

const run = promisify(execFile);
const root = dirname(dirname(fileURLToPath(import.meta.url)));

test('records one concrete disposition for every non-skill repository file', async () => {
  const { stdout } = await run('git', ['rev-parse', 'HEAD'], { cwd: root });
  const report = await auditRepository(root, stdout.trim());
  const paths = report.files.map((file) => file.path);

  expect(report.baseline).toBe(stdout.trim());
  expect(paths.length).toBeGreaterThan(500);
  expect(paths.some((path) => path.startsWith('skills/'))).toBe(false);
  expect(new Set(paths).size).toBe(paths.length);
  expect(report.files.every((file) => file.reason.length > 20)).toBe(true);
  expect(report.files.every((file) => file.sha256.match(/^[a-f0-9]{64}$/))).toBe(true);
});

test('classifies committed, changed, and untracked files without skills', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'skills-release-audit-'));
  try {
    await mkdir(join(fixture, 'skills', 'example'), { recursive: true });
    await writeFile(join(fixture, 'AGENTS.md'), '# Rules\n');
    await writeFile(join(fixture, 'package.json'), '{}\n');
    await writeFile(join(fixture, 'skills', 'example', 'SKILL.md'), '# Skill\n');
    await run('git', ['init', '-q'], { cwd: fixture });
    await run('git', ['config', 'user.name', 'Audit Test'], { cwd: fixture });
    await run('git', ['config', 'user.email', 'audit@example.com'], { cwd: fixture });
    await run('git', ['add', '.'], { cwd: fixture });
    await run('git', ['commit', '-qm', 'test: freeze audit fixture'], { cwd: fixture });
    const { stdout } = await run('git', ['rev-parse', 'HEAD'], { cwd: fixture });
    await writeFile(join(fixture, 'package.json'), '{"private":true}\n');
    await writeFile(join(fixture, 'README.md'), '# Read me\n');

    const report = await auditRepository(fixture, stdout.trim());
    const dispositions = Object.fromEntries(
      report.files.map((file) => [file.path, file.disposition]),
    );
    expect(dispositions).toEqual({
      'AGENTS.md': 'verified current',
      'README.md': 'changed',
      'package.json': 'changed',
    });
  } finally {
    await rm(fixture, { force: true, recursive: true });
  }
});
