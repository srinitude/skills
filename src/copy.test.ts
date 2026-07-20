import { mkdtemp, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, test } from 'vitest';

import { validateCopy } from './copy.js';

const temporary: string[] = [];

afterEach(async () => {
  await Promise.all(
    temporary.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

test('passes the current public repository copy', async () => {
  const root = process.cwd();
  const report = await validateCopy(root);
  expect(report.status, report.findings.map((finding) => finding.message).join('\n')).toBe(
    'PASS',
  );
  expect(report.inspected_files).toBeGreaterThan(10);
  expect(report.skill_files).toEqual(['skills/starting-point/SKILL.md']);
});

test('reports banned wording and duplicate skill locations', async () => {
  const root = await mkdtemp(join(tmpdir(), 'copy-gate-'));
  temporary.push(root);
  await writeFile(join(root, 'README.md'), 'We leverage this route.\n', 'utf8');
  await writeFile(join(root, 'SKILL.md'), 'copied body\n', 'utf8');

  const report = await validateCopy(root);
  expect(report.status).toBe('FAIL');
  expect(report.findings.map((finding) => finding.code)).toEqual(
    expect.arrayContaining(['BANNED_TERM', 'DUPLICATE_SKILL_LOCATION']),
  );
});
