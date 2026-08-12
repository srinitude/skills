import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const skill = join(root, 'skills', 'timebox');
const evidence = join(root, 'evidence', 'ports', 'timebox');
const packet = 'b2c2f242431a613f7001db2e9fef5d72e24b8899bceddb39e2452ad3d96994d5';
const sources: Record<string, string> = {
  'SKILL.md': '08109011d0ab6b98102768e4e9644059bf3aad8c600391715b5d03d1a025ae40',
  'references/eval-cases.json':
    '9f341462234e7365ac5f4895881035df07d0e7a8912aab7153788b27ca95a82f',
};
const sourceCases = Array.from(
  { length: 6 },
  (_, index) => `TB-${String(index + 1).padStart(3, '0')}`,
);

function digest(value: Buffer | string): string {
  return createHash('sha256').update(value).digest('hex');
}

async function json(path: string): Promise<Record<string, unknown>> {
  return JSON.parse(await readFile(path, 'utf8')) as Record<string, unknown>;
}

test('keeps an exact packet of both native source files', async () => {
  const manifest = await json(join(evidence, 'manifest.json'));
  const files = manifest.files as Array<{
    evidence_path: string;
    sha256: string;
    source_path: string;
  }>;
  const rows: string[] = [];
  for (const [sourcePath, sha256] of Object.entries(sources)) {
    const file = files.find((entry) => entry.source_path === sourcePath);
    if (!file) throw new Error(`missing ${sourcePath}`);
    expect(digest(await readFile(join(evidence, file.evidence_path)))).toBe(sha256);
    rows.push(`${sourcePath}\0${sha256}\n`);
  }
  expect(digest(rows.join(''))).toBe(packet);
  expect(manifest.source_case_ids).toEqual(sourceCases);
  expect(manifest.excluded_entries).toEqual([]);
});

test('maps every nonblank source line without loss', async () => {
  const mapping = await json(join(skill, 'evals', 'source-mapping.json'));
  expect(mapping.coverage).toEqual({
    mapped_nonblank_lines: 159,
    ratio: 1,
    source_nonblank_lines: 159,
  });
  const entries = mapping.entries as Array<{
    action: string;
    evidence_target: string;
    public_targets: string[];
    review_state: string;
  }>;
  expect(entries).toHaveLength(159);
  expect(
    entries.every(
      (entry) =>
        entry.action !== 'drop' &&
        entry.evidence_target.length > 0 &&
        entry.public_targets.length > 0 &&
        entry.review_state === 'approved',
    ),
  ).toBe(true);
});

test('binds all source cases and public files to lineage', async () => {
  const lineage = await json(join(skill, 'evals', 'source-lineage.json'));
  const cases = await json(join(skill, 'evals', 'cases.json'));
  expect(lineage).toMatchObject({
    native_manifest_sha256: packet,
    native_version: '1.0.2',
    public_version: '0.1.0',
    source_case_ids: sourceCases,
  });
  expect(
    (cases.cases as Array<{ source_id: string }>).map(({ source_id }) => source_id),
  ).toEqual(sourceCases);
  for (const file of lineage.public_files as Array<{
    path: string;
    source_paths: string[];
  }>) {
    expect(file.source_paths.length).toBeGreaterThan(0);
    expect(await readFile(join(skill, file.path), 'utf8')).not.toHaveLength(0);
  }
});

test('publishes the complete deadline and validation contract', async () => {
  const source = await readFile(join(skill, 'SKILL.md'), 'utf8');
  for (const marker of [
    'fresh clock anchor',
    'absolute deadline',
    'protected validation reserve',
    'TIMEBOX_PASS',
    'TIMEBOX_FAILED',
    'TIMEBOX_NOT_STARTED',
    'queued, delegated, pending approval, or unverified',
    'completion timestamp',
  ])
    expect(source).toContain(marker);
  expect(source).not.toMatch(/Hermes|skill_view|skill_manage/);
  expect(source.trimEnd().split('\n').length).toBeLessThan(200);
});
