import { access, readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const evalRoot = join(root, 'skills', 'starting-point', 'evals');
const reifyEvalRoot = join(root, 'skills', 'reify', 'evals');

test('binds the public port to the frozen native v1.1.6 manifest', async () => {
  const lineage = JSON.parse(
    await readFile(join(evalRoot, 'source-lineage.json'), 'utf8'),
  ) as {
    native_manifest_sha256: string;
    native_version: string;
    public_files: Array<{ path: string; source_paths: string[] }>;
    public_version: string;
    source_case_ids: string[];
    source_files: Array<{ path: string; sha256: string }>;
  };

  expect(lineage).toMatchObject({
    native_manifest_sha256:
      'ef10e9c27dec7b9cb594b1bdd7f7a3bdec50caaeb663a21016d8cc483f8cc5f0',
    native_version: '1.1.6',
    public_version: '0.1.0',
  });
  expect(lineage.source_case_ids).toHaveLength(18);
  expect(new Set(lineage.source_case_ids).size).toBe(18);
  expect(lineage.source_files).toContainEqual({
    path: 'references/eval-contract.md',
    sha256: '6491133b245f06d8f4c386aa91c31159df110fc180d8c95b8f4558ea90534c35',
  });

  expect(lineage.public_files).toEqual([
    { path: 'SKILL.md', source_paths: ['SKILL.md'] },
    { path: 'references/core-loop.md', source_paths: ['references/path-check.md'] },
    { path: 'references/proof-checklist.md', source_paths: ['references/evidence.md'] },
    { path: 'evals/cases.json', source_paths: ['references/eval-cases.json'] },
    { path: 'evals/contract.md', source_paths: ['references/eval-contract.md'] },
  ]);
  await Promise.all(
    lineage.public_files.map((entry) =>
      access(join(root, 'skills', 'starting-point', entry.path)),
    ),
  );
});

test('keeps all frozen native pressure IDs in the public case file', async () => {
  const lineage = JSON.parse(
    await readFile(join(evalRoot, 'source-lineage.json'), 'utf8'),
  ) as {
    source_case_ids: string[];
  };
  const cases = JSON.parse(await readFile(join(evalRoot, 'cases.json'), 'utf8')) as {
    cases: Array<{ id: string }>;
  };
  expect(cases.cases.map((entry) => entry.id).sort()).toEqual(
    [...lineage.source_case_ids].sort(),
  );
});

test('binds reify to the frozen native v1.0.0 packet', async () => {
  const lineage = JSON.parse(
    await readFile(join(reifyEvalRoot, 'source-lineage.json'), 'utf8'),
  ) as {
    native_manifest_sha256: string;
    native_version: string;
    public_files: Array<{ path: string; source_paths: string[] }>;
    public_version: string;
    source_case_ids: string[];
  };

  expect(lineage).toMatchObject({
    native_manifest_sha256:
      'd9a6be674ac2999354f07b3510733a53351b468a7f0042c3ea8c1a65ea1b7c6a',
    native_version: '1.0.0',
    public_version: '0.1.0',
  });
  expect(lineage.source_case_ids).toEqual([
    'RFY-001',
    'RFY-002',
    'RFY-003',
    'RFY-004',
    'RFY-005',
  ]);
  await Promise.all(
    lineage.public_files.map((entry) => access(join(root, 'skills', 'reify', entry.path))),
  );
});
