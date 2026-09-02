import { access, readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const evalRoot = join(root, 'skills', 'starting-point', 'evals');
const reifyEvalRoot = join(root, 'skills', 'reify', 'evals');

test('binds the public starting-point port to its complete baseline packet', async () => {
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
      '56de13051e3eb01974c9d819af3546efb136bf83de85e25a026901912950c156',
    native_version: '0.1.0',
    public_version: '0.1.0',
  });
  expect(lineage.source_case_ids).toHaveLength(18);
  expect(new Set(lineage.source_case_ids).size).toBe(18);
  expect(lineage.source_files).toHaveLength(15);

  expect(lineage.public_files.length).toBeGreaterThanOrEqual(15);
  expect(lineage.public_files).toContainEqual({
    path: 'SKILL.md',
    source_paths: ['SKILL.md', 'target-scaffolding'],
  });
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

const behaviorPorts = [
  {
    slug: 'would-agents-actually',
    nativeVersion: '0.1.0',
    manifest: 'cb00bfd6e965bb60c8ba5dc6de57e00dc96c058fa4d75ba6db8dc0684fe17e16',
    sourcePrefix: 'WAA',
  },
  {
    slug: 'would-humans-actually',
    nativeVersion: '0.1.0',
    manifest: 'bd926d166cf355ee311edae1280280e23286daaaf928a4a36dbac3083f27577a',
    sourcePrefix: 'WHA',
  },
];

test.each(behaviorPorts)('binds $slug to its frozen native packet', async (port) => {
  const directory = join(root, 'skills', port.slug, 'evals');
  const lineage = JSON.parse(
    await readFile(join(directory, 'source-lineage.json'), 'utf8'),
  ) as {
    native_manifest_sha256: string;
    native_version: string;
    public_files: Array<{ path: string }>;
    public_version: string;
    source_case_ids: string[];
  };
  const cases = JSON.parse(await readFile(join(directory, 'cases.json'), 'utf8')) as {
    cases: Array<{ id: string }>;
  };
  expect(lineage).toMatchObject({
    native_manifest_sha256: port.manifest,
    native_version: port.nativeVersion,
    public_version: '0.1.0',
  });
  expect(lineage.source_case_ids).toEqual(
    Array.from(
      { length: 8 },
      (_, index) => `${port.sourcePrefix}-${String(index + 1).padStart(3, '0')}`,
    ),
  );
  expect(cases.cases.map((entry) => entry.id)).toEqual(lineage.source_case_ids);
  await Promise.all(
    lineage.public_files.map((entry) =>
      access(join(root, 'skills', port.slug, entry.path)),
    ),
  );
});
