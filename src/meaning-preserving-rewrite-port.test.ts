import { createHash } from 'node:crypto';
import { access, readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const packetRoot = join(root, 'evidence', 'ports', 'meaning-preserving-rewrite');
const skillRoot = join(root, 'skills', 'meaning-preserving-rewrite');
const manifestHash = 'aa62cbdacdfe43f82ef90507f75400c2032791701b852cfd11544014a59dad28';
const sourceHashes = {
  'SKILL.md': 'a779c5dca688441ec314426a5f0f46ea14838577054a755d3ef1ed38ed170723',
  'references/baseline-task.md':
    'ab8fb06144c9ad7d9e93cd837fc8dc99549172e6a603adb98557777ac9abe771',
  'references/final-validation.md':
    '2818fac953449a3a64941baa0c83c5deea8c245dae106d8f825071f10e58aa64',
  'references/hermes-docs-inventory.md':
    'ae55b0d0377064e498e57148961ee552d0105711cdd0877cfe8f160f57a778f9',
  'references/ledger-template.md':
    '2e26202c3f1fb5cd9c14e6407c35fcff20d89ebaaca85e379e33d03da86d65c8',
  'references/voice-check.md':
    '91fe711e5c0c769baf0c5efa29224371f04c45ec59de911ac62338af57b1a082',
};
const packetFiles = {
  'SKILL.md': 'native/SKILL.native.md',
  'references/baseline-task.md': 'native/references/baseline-task.md',
  'references/final-validation.md': 'native/references/final-validation.md',
  'references/hermes-docs-inventory.md': 'native/references/hermes-docs-inventory.md',
  'references/ledger-template.md': 'native/references/ledger-template.md',
  'references/voice-check.md': 'native/references/voice-check.md',
};

function sha256(bytes: Buffer | string): string {
  return createHash('sha256').update(bytes).digest('hex');
}

async function json(relative: string): Promise<Record<string, unknown>> {
  return JSON.parse(await readFile(join(root, relative), 'utf8')) as Record<
    string,
    unknown
  >;
}

function nonblankLines(text: string): Array<{ line: number; text: string }> {
  return text
    .split('\n')
    .map((value, index) => ({ line: index + 1, text: value }))
    .filter(({ text: value }) => value.trim().length > 0);
}

test('keeps every native meaning rewrite file byte exact', async () => {
  const records: string[] = [];
  for (const [sourcePath, packetName] of Object.entries(packetFiles)) {
    const bytes = await readFile(join(packetRoot, packetName));
    const digest = sourceHashes[sourcePath as keyof typeof sourceHashes];
    expect(sha256(bytes)).toBe(digest);
    records.push(`${sourcePath}\0${digest}\n`);
  }
  expect(sha256(records.join(''))).toBe(manifestHash);
  const manifest = await json('evidence/ports/meaning-preserving-rewrite/manifest.json');
  expect(manifest.source_manifest_sha256).toBe(manifestHash);
  expect(manifest.source_case_ids).toEqual([]);
  expect(manifest.excluded_entries).toEqual([]);
});

test('maps every nonblank native line without a drop', async () => {
  const mapping = await json('skills/meaning-preserving-rewrite/evals/source-mapping.json');
  const entries = mapping.entries as Array<Record<string, unknown>>;
  const expected = [] as Array<Record<string, unknown>>;
  for (const [sourcePath, packetName] of Object.entries(packetFiles)) {
    const text = await readFile(join(packetRoot, packetName), 'utf8');
    for (const line of nonblankLines(text)) {
      expected.push({
        source_line: line.line,
        source_line_sha256: sha256(line.text),
        source_path: sourcePath,
      });
    }
  }
  expect(
    entries.map(({ source_line, source_line_sha256, source_path }) => ({
      source_line,
      source_line_sha256,
      source_path,
    })),
  ).toEqual(expected);
  expect(mapping.coverage).toEqual({
    mapped_nonblank_lines: expected.length,
    ratio: 1,
    source_nonblank_lines: expected.length,
  });
  expect(entries.every((entry) => entry.action !== 'drop')).toBe(true);
  expect(entries.every((entry) => entry.review_state === 'approved')).toBe(true);
  expect(entries.every((entry) => entry.public_target && entry.evidence_target)).toBe(true);
});

test('binds public files and target-only cases to native lineage', async () => {
  const lineage = await json('skills/meaning-preserving-rewrite/evals/source-lineage.json');
  expect(lineage).toMatchObject({
    native_manifest_sha256: manifestHash,
    native_version: '2.2.0',
    public_version: '0.1.0',
    source_case_ids: ['MPR-NO-NATIVE-CASES'],
    source_files: Object.entries(sourceHashes).map(([path, hash]) => ({
      path,
      sha256: hash,
    })),
  });
  const publicFiles = lineage.public_files as Array<{
    path: string;
    source_paths: string[];
  }>;
  expect(publicFiles.length).toBeGreaterThan(0);
  await Promise.all(publicFiles.map((entry) => access(join(skillRoot, entry.path))));
  expect(publicFiles.every((entry) => entry.source_paths.length > 0)).toBe(true);
  const cases = await json('skills/meaning-preserving-rewrite/evals/cases.json');
  const publicCases = cases.cases as Array<Record<string, unknown>>;
  expect(publicCases.map((entry) => entry.source_id)).toEqual(lineage.active_case_ids);
  expect(publicCases.every((entry) => entry.pressures instanceof Array)).toBe(true);
});

test('preserves meaning checks in a portable package', async () => {
  const skill = await readFile(join(skillRoot, 'SKILL.md'), 'utf8');
  expect(skill).not.toMatch(
    /Hermes Agent|SOUL|AGENTS|skill_manage|skill_view|global-coding-policy/,
  );
  expect(skill).toContain('Never use `drop`');
  expect(skill).toContain('requirement strength');
  expect(skill).toContain('owner-only backup');
  expect(skill).toContain('non-independent');
  expect(skill).toContain('component result');
  const reconciliation = await readFile(
    join(skillRoot, 'references', 'dependency-reconciliation.md'),
    'utf8',
  );
  expect(reconciliation).toContain('package simplification peer');
  expect(reconciliation).toContain('host writing policy');
  expect(reconciliation).toContain('does not replace source meaning');
});
