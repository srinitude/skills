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

interface MappingEntry {
  action: string;
  evidence_target: string;
  preservation_judgment: string;
  public_assertions?: Array<{ contains: string; target: string }>;
  public_targets: string[];
  review_state: string;
  source_line: number;
  source_path: string;
  source_text_sha256: string;
}

function digest(value: Buffer | string): string {
  return createHash('sha256').update(value).digest('hex');
}

async function json(path: string): Promise<Record<string, unknown>> {
  return JSON.parse(await readFile(path, 'utf8')) as Record<string, unknown>;
}

async function loadNativeLines(): Promise<Map<string, string[]>> {
  const manifest = await json(join(evidence, 'manifest.json'));
  const files = manifest.files as Array<{ evidence_path: string; source_path: string }>;
  const lines = new Map<string, string[]>();
  for (const sourcePath of Object.keys(sources)) {
    const evidencePath = files.find(
      (entry) => entry.source_path === sourcePath,
    )?.evidence_path;
    if (!evidencePath) throw new Error(`missing evidence path for ${sourcePath}`);
    lines.set(
      sourcePath,
      (await readFile(join(evidence, evidencePath), 'utf8')).split('\n'),
    );
  }
  return lines;
}

async function expectMappedEntry(
  entry: MappingEntry,
  nativeLines: Map<string, string[]>,
): Promise<void> {
  const sourceLine = nativeLines.get(entry.source_path)?.[entry.source_line - 1];
  expect(sourceLine?.trim().length).toBeGreaterThan(0);
  expect(digest(sourceLine ?? '')).toBe(entry.source_text_sha256);
  expect(entry.action).not.toBe('drop');
  expect(entry.evidence_target.length).toBeGreaterThan(0);
  expect(entry.review_state).toBe('approved');
  if (entry.action === 'clarify') {
    expect(entry.public_targets).toEqual([]);
    expect(entry.preservation_judgment).toContain('portable omission');
    return;
  }
  expect(entry.public_targets.length).toBeGreaterThan(0);
  expect(entry.public_assertions?.length).toBeGreaterThan(0);
  for (const assertion of entry.public_assertions ?? []) {
    expect(entry.public_targets).toContain(assertion.target);
    expect(await readFile(join(skill, assertion.target), 'utf8')).toContain(
      assertion.contains,
    );
  }
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
  const entries = mapping.entries as MappingEntry[];
  expect(entries).toHaveLength(159);
  const nativeLines = await loadNativeLines();
  for (const entry of entries) await expectMappedEntry(entry, nativeLines);
});

test('binds all source cases and public files to lineage', async () => {
  const lineage = await json(join(skill, 'evals', 'source-lineage.json'));
  const cases = await json(join(skill, 'evals', 'cases.json'));
  expect(lineage).toMatchObject({
    native_manifest_sha256: packet,
    native_version: '1.0.2',
    public_version: '0.1.1',
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
    'hard acceptance constraint',
    'Only work that is complete, validated, and timestamped before the deadline may pass.',
    'fresh local clock anchor',
    'absolute deadline',
    'protected validation reserve',
    'has a proven bound that fits',
    'The chosen route preserves the full requested scope, safety rules, and decisive validation.',
    'subagents, queued jobs, approvals, restarts, and remote processing',
    'TIMEBOX_PASS',
    'TIMEBOX_FAILED',
    'TIMEBOX_NOT_STARTED',
    'queued, delegated, pending approval, or unverified',
    'completion timestamp',
    '## Progressive disclosure',
    '`evals/cases.json` owns objective pressure cases and acceptance.',
    '## Verification',
    'Partial, queued, late, or unvalidated work cannot pass.',
  ])
    expect(source).toContain(marker);
  expect(source).not.toMatch(/Hermes|skill_view|skill_manage/);
  expect(source.trimEnd().split('\n').length).toBeLessThan(200);
});

test('publishes source acceptance and backlink semantics', async () => {
  const native = await json(join(evidence, 'native', 'references', 'eval-cases.json'));
  const cases = await json(join(skill, 'evals', 'cases.json'));
  expect(cases.acceptance).toBe(native.acceptance);
  expect(cases.backlink).toBe(native.backlink);
  expect(
    (cases.cases as Array<Record<string, unknown>>).map((entry) => ({
      forbidden: entry.veto,
      id: entry.source_id,
      prompt: entry.prompt,
      required: entry.required,
    })),
  ).toEqual(native.cases);
});
