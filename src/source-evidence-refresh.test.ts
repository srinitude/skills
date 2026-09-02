import { createHash } from 'node:crypto';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

import { afterEach, expect, test } from 'vitest';

import { refreshRepositoryBaseline } from './source-evidence-refresh.js';

const roots: string[] = [];
const digest = (value: string) => createHash('sha256').update(value).digest('hex');

afterEach(async () =>
  Promise.all(roots.splice(0).map((root) => rm(root, { recursive: true }))),
);

async function fixture(): Promise<string> {
  const root = await mkdtemp(join(tmpdir(), 'source-refresh-'));
  roots.push(root);
  const skill = join(root, 'skills', 'sample');
  await mkdir(join(skill, 'evals'), { recursive: true });
  await writeFile(join(skill, 'SKILL.md'), '# Sample\n');
  await writeFile(
    join(skill, 'evals', 'source-lineage.json'),
    JSON.stringify({
      native_manifest_sha256: digest('native'),
      source_files: [{ path: 'SKILL.md', sha256: digest('# Sample\n') }],
    }),
  );
  return root;
}

test('writes a checked repository baseline manifest', async () => {
  const root = await fixture();
  const result = await refreshRepositoryBaseline(root, 'sample');
  const saved = JSON.parse(
    await readFile(join(root, 'evidence/ports/sample/source-manifest.json'), 'utf8'),
  );
  expect(result.files).toBe(1);
  expect(saved).toMatchObject({ skill: 'sample', source_kind: 'repository_baseline' });
  expect(saved.files[0]).toMatchObject({
    bytes: 9,
    location_kind: 'repository',
    location_path: 'skills/sample/SKILL.md',
  });
});

test('refuses to replace hybrid evidence', async () => {
  const root = await fixture();
  const port = join(root, 'evidence/ports/sample');
  await mkdir(port, { recursive: true });
  await writeFile(
    join(port, 'source-manifest.json'),
    JSON.stringify({ source_kind: 'hybrid_archived_and_repository_baseline' }),
  );
  await expect(refreshRepositoryBaseline(root, 'sample')).rejects.toThrow(
    'not a repository baseline',
  );
});
