import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const skill = join(root, 'skills', 'simplify-skill');
const evidence = join(root, 'evidence', 'ports', 'simplify-skill');
const sources: Record<string, string> = {
  'SKILL.md': '40e5fb7120ee0f12d88b1a3e746d4b5a2fbccab27e24df09a10c471931c45744',
  'references/eval-cases.json':
    '255f8fd2faeee23517d7bf3ece71ef589c0b5740c97fd32b3da05aa876a37eb6',
  'references/preservation-contract.md':
    '8c5e1e6bb47f2d6be3d10bbd794992dd45ac2e11f1a51534f69a9f54d69cba75',
  'references/simplification-model.md':
    '190898eda63f44af800c1c0cb4b18a5fab592b6c7b329d2dd3715cec88294598',
};
const packet = '0061515853b8d4bf3075b7db9d1a70d0e055b573a95cd87f560cad1ade1656dc';

interface SourceManifest {
  excluded_entries: unknown[];
  files: Array<{ evidence_path: string; sha256: string; source_path: string }>;
  source_case_ids: string[];
}

interface SourceMapping {
  coverage: { mapped_nonblank_lines: number; ratio: number; source_nonblank_lines: number };
  entries: Array<{
    action: string;
    evidence_target: string;
    public_target: string;
    review_state: string;
  }>;
}

interface SourceLineage {
  active_case_ids: string[];
  native_manifest_sha256: string;
  public_files: Array<{ path: string; source_paths: string[] }>;
  source_case_ids: string[];
}

interface EvalCases {
  cases: Array<{ source_id: string }>;
}

function digest(value: Buffer | string): string {
  return createHash('sha256').update(value).digest('hex');
}

async function json<T>(path: string): Promise<T> {
  return JSON.parse(await readFile(path, 'utf8')) as T;
}

test('preserves every native file and native case in committed evidence', async () => {
  const manifest = await json<SourceManifest>(join(evidence, 'manifest.json'));
  const rows: string[] = [];
  for (const [source, sha256] of Object.entries(sources)) {
    const file = manifest.files.find((entry) => entry.source_path === source);
    expect(file?.sha256).toBe(sha256);
    if (!file) throw new Error(`missing evidence entry for ${source}`);
    const bytes = await readFile(join(evidence, file.evidence_path));
    expect(digest(bytes)).toBe(sha256);
    rows.push(`${source}\0${sha256}\n`);
  }
  expect(digest(rows.join(''))).toBe(packet);
  expect(manifest.source_case_ids).toEqual(
    Array.from({ length: 10 }, (_, index) => `CASE-${String(index + 1).padStart(3, '0')}`),
  );
  expect(manifest.excluded_entries).toEqual([]);
});

test('maps every nonblank source line without unauthorized loss', async () => {
  const mapping = await json<SourceMapping>(join(skill, 'evals', 'source-mapping.json'));
  expect(mapping.coverage).toEqual({
    mapped_nonblank_lines: 503,
    ratio: 1,
    source_nonblank_lines: 503,
  });
  expect(mapping.entries).toHaveLength(503);
  expect(mapping.entries.every((entry) => entry.action !== 'drop')).toBe(true);
  expect(mapping.entries.every((entry) => entry.review_state === 'approved')).toBe(true);
  expect(
    mapping.entries.every((entry) => entry.public_target && entry.evidence_target),
  ).toBe(true);
});

test('binds all native cases to the portable eval contract', async () => {
  const lineage = await json<SourceLineage>(join(skill, 'evals', 'source-lineage.json'));
  const cases = await json<EvalCases>(join(skill, 'evals', 'cases.json'));
  expect(lineage.native_manifest_sha256).toBe(packet);
  expect(lineage.source_case_ids).toEqual(
    Array.from({ length: 10 }, (_, index) => `CASE-${String(index + 1).padStart(3, '0')}`),
  );
  expect(cases.cases.map((entry) => entry.source_id)).toEqual(lineage.active_case_ids);
  for (const file of lineage.public_files) {
    expect(file.source_paths.length).toBeGreaterThan(0);
    expect(await readFile(join(skill, file.path), 'utf8')).not.toHaveLength(0);
  }
});

test('publishes a portable deterministic simplification contract', async () => {
  const source = await readFile(join(skill, 'SKILL.md'), 'utf8');
  expect(source).toContain('declared complexity cost');
  expect(source).toContain('Never accept line count alone');
  expect(source).toContain(
    'DISCOVER -> BASELINE -> CONTRACT -> SELECT -> REWRITE -> VERIFY -> ACCEPT',
  );
  expect(source).toContain('NEEDS_APPROVAL');
  expect(source).toContain('protected spans');
  expect(source).toContain('component status');
  expect(source).toContain('references/dependency-reconciliation.md');
  expect(source).not.toMatch(
    /Hermes|skill_view|skills_list|skill_manage|global-coding-policy/,
  );
});
