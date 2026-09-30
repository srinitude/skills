import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const skill = join(root, 'skills', 'human-language');
const evidence = join(root, 'evidence', 'ports', 'human-language');
const packet = 'dcf912359a2c9bee00fda168542a8f8880ec98e07bbfbc8ba024ecef053d49b4';
const sourceCases = Array.from(
  { length: 36 },
  (_, index) => `HL-${String(index + 1).padStart(3, '0')}`,
);

function digest(value: Buffer | string): string {
  return createHash('sha256').update(value).digest('hex');
}

async function json(path: string): Promise<Record<string, unknown>> {
  return JSON.parse(await readFile(path, 'utf8')) as Record<string, unknown>;
}

test('keeps an exact packet of all 8 native source files', async () => {
  const manifest = await json(join(evidence, 'manifest.json'));
  const files = manifest.files as Array<{
    evidence_path: string;
    sha256: string;
    source_path: string;
  }>;
  expect(files).toHaveLength(8);
  const rows: string[] = [];
  for (const file of [...files].sort((a, b) => (a.source_path < b.source_path ? -1 : 1))) {
    expect(digest(await readFile(join(evidence, file.evidence_path)))).toBe(file.sha256);
    rows.push(`${file.source_path}\0${file.sha256}\n`);
  }
  expect(digest(rows.join(''))).toBe(packet);
  expect(manifest.source_case_ids).toEqual(sourceCases);
  expect(manifest.native_case_ids as string[]).toHaveLength(36);
});

test('binds all source cases and public files to lineage', async () => {
  const lineage = await json(join(skill, 'evals', 'source-lineage.json'));
  const cases = await json(join(skill, 'evals', 'cases.json'));
  expect(lineage).toMatchObject({
    native_manifest_sha256: packet,
    native_version: 'unversioned',
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

test('publishes the human-language contract', async () => {
  const source = await readFile(join(skill, 'SKILL.md'), 'utf8');
  for (const marker of [
    'Read [writing rules and output checks](references/writing-rules.md) before writing.',
    'run their required gate before each output',
    'Do not fill missing context with guesses.',
    'On any skill change, run [validation cases](references/validation.md) before calling the skill tested.',
    '## Package checks and examples',
    '`evals/cases.json`',
  ])
    expect(source).toContain(marker);
  expect(source).not.toMatch(/Hermes|skill_view|skill_manage/);
  expect(source.trimEnd().split('\n').length).toBeLessThan(200);
});
