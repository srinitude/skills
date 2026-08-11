import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const skill = join(root, 'skills', 'goal-prompt');
const evidence = join(root, 'evidence', 'ports', 'goal-prompt');
const packet = '8c1269a76a5ad57e785f4968a4ca71ccd8d15ee5a22e4955573dfcfb6b182243';
const sources: Record<string, string> = {
  'SKILL.md': '5a27d47bc07ddd68a60a09e26e774cfa487c20853a569c502f9d5f5b5addac59',
  'references/plan-package-input.md':
    '3b657d32a7e8f7ee4a9af0b91895605fd52b5e57d1b42eb653d5e6fa217be955',
};

function digest(value: Buffer | string): string {
  return createHash('sha256').update(value).digest('hex');
}

async function json(path: string): Promise<Record<string, unknown>> {
  return JSON.parse(await readFile(path, 'utf8')) as Record<string, unknown>;
}

test('preserves both native files and records no native cases', async () => {
  const manifest = await json(join(evidence, 'manifest.json'));
  const files = manifest.files as Array<{
    evidence_path: string;
    sha256: string;
    source_path: string;
  }>;
  const rows: string[] = [];
  for (const [source, sha256] of Object.entries(sources)) {
    const file = files.find((entry) => entry.source_path === source);
    if (!file) throw new Error(`missing ${source}`);
    expect(digest(await readFile(join(evidence, file.evidence_path)))).toBe(sha256);
    rows.push(`${source}\0${sha256}\n`);
  }
  expect(digest(rows.join(''))).toBe(packet);
  expect(manifest.source_case_ids).toEqual([]);
  expect(manifest.excluded_entries).toEqual([]);
});

test('maps every nonblank source line without drop', async () => {
  const mapping = await json(join(skill, 'evals', 'source-mapping.json'));
  expect(mapping.coverage).toEqual({
    mapped_nonblank_lines: 171,
    ratio: 1,
    source_nonblank_lines: 171,
  });
  const entries = mapping.entries as Array<{ action: string; review_state: string }>;
  expect(entries).toHaveLength(171);
  expect(
    entries.every((entry) => entry.action !== 'drop' && entry.review_state === 'approved'),
  ).toBe(true);
});

test('binds target-only cases and every public file to source lineage', async () => {
  const lineage = await json(join(skill, 'evals', 'source-lineage.json'));
  const cases = await json(join(skill, 'evals', 'cases.json'));
  expect(lineage.native_manifest_sha256).toBe(packet);
  expect(lineage.source_case_ids).toEqual(['GOAL-NO-NATIVE-CASES']);
  expect(
    (cases.cases as Array<{ source_id: string }>).map((entry) => entry.source_id),
  ).toEqual(lineage.active_case_ids);
  for (const file of lineage.public_files as Array<{
    path: string;
    source_paths: string[];
  }>) {
    expect(file.source_paths.length).toBeGreaterThan(0);
    expect(await readFile(join(skill, file.path), 'utf8')).not.toHaveLength(0);
  }
});

test('publishes a portable goal packaging contract', async () => {
  const source = await readFile(join(skill, 'SKILL.md'), 'utf8');
  for (const marker of [
    'six-line command',
    '1900 characters',
    'source snapshot',
    '100% coverage',
    'five consecutive qualifying turns',
    '20 top-level tool calls',
    'steering and task mutation',
    'references/plan-package-input.md',
  ])
    expect(source).toContain(marker);
  expect(source).not.toMatch(/Hermes|global-coding-policy|skill_view|skill_manage/);
});
