import { mkdir, mkdtemp, rm, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, expect, test } from 'vitest';

import { loadCatalog } from './catalog.js';
import { validateCopy } from './copy.js';

const temporary: string[] = [];

afterEach(async () => {
  await Promise.all(
    temporary.splice(0).map((path) => rm(path, { force: true, recursive: true })),
  );
});

test('LOGIC-005 copy validation rejects symlinks before packaging can omit them', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'copy-special-entry-'));
  temporary.push(fixture);
  await mkdir(join(fixture, 'skills', 'sample'), { recursive: true });
  await writeFile(join(fixture, 'skills', 'sample', 'SKILL.md'), '# Sample\n');
  await writeFile(join(fixture, 'outside.txt'), 'outside\n');
  await symlink(
    join(fixture, 'outside.txt'),
    join(fixture, 'skills', 'sample', 'escape.md'),
  );

  const report = await validateCopy(fixture);

  expect(report.status).toBe('FAIL');
  expect(report.findings.map((finding) => finding.code)).toContain('SPECIAL_ENTRY');
});

test('LOGIC-008 catalog loading rejects a directory and frontmatter name mismatch', async () => {
  const fixture = await mkdtemp(join(tmpdir(), 'catalog-name-mismatch-'));
  temporary.push(fixture);
  await mkdir(join(fixture, 'skills', 'wrong-directory'), { recursive: true });
  await writeFile(
    join(fixture, 'skills', 'wrong-directory', 'SKILL.md'),
    [
      '---',
      'name: declared-name',
      'description: Use when testing catalog identity.',
      'metadata:',
      '  version: 0.1.0',
      '---',
      '',
    ].join('\n'),
  );

  await expect(loadCatalog(fixture)).rejects.toThrow(/does not match name/i);
});
