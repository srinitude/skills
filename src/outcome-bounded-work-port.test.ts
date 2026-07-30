import { createHash } from 'node:crypto';
import { access, readFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from 'vitest';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const packetRoot = join(root, 'evidence', 'ports', 'outcome-bounded-work');
const skillRoot = join(root, 'skills', 'outcome-bounded-work');
const sourceHashes = {
  'SKILL.md': '4f9b92967f57925205ece279186616cb417cc060b89ffbedafc70dffd77a8a79',
  'references/eval-cases.json':
    '3bab97f9a03a07e97c544113f8ada34ea699d209d74481f53e48a30f82918aa3',
};
const packetFiles = {
  'SKILL.md': 'SKILL.native.md',
  'references/eval-cases.json': 'eval-cases.native.json',
};
const sourceCases = [
  'conversation-candidate-path',
  'exact-method-is-deliverable',
  'imperative-method-ambiguous',
  'better-route-drops-scope',
  'safety-rule-sounds-procedural',
  'evidence-not-recipe',
  'privacy-forbidden-outcome',
  'simple-request-no-meta-work',
  'audit-does-not-mutate',
  'mode-consistency',
];
const lineageCases = sourceCases.map(
  (_, index) => `NOBW-${String(index + 1).padStart(3, '0')}`,
);

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

test('keeps a byte-exact packet of every native source file', async () => {
  for (const [sourcePath, packetName] of Object.entries(packetFiles)) {
    const bytes = await readFile(join(packetRoot, packetName));
    expect(sha256(bytes)).toBe(sourceHashes[sourcePath as keyof typeof sourceHashes]);
  }
});

test('maps every nonblank source line and native case without a drop', async () => {
  const mapping = await json('skills/outcome-bounded-work/evals/source-mapping.json');
  const entries = mapping.entries as Array<Record<string, unknown>>;
  const expected = [] as Array<{
    source_line: number;
    source_line_sha256: string;
    source_path: string;
  }>;
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
  expect(mapping.coverage).toEqual({
    mapped_nonblank_lines: 228,
    ratio: 1,
    source_nonblank_lines: 228,
  });
  expect(
    entries.map(({ source_line, source_line_sha256, source_path }) => ({
      source_line,
      source_line_sha256,
      source_path,
    })),
  ).toEqual(expected);
  expect(entries.every((entry) => !('source_text' in entry))).toBe(true);
  expect(
    entries.every((entry) =>
      ['keep', 'split', 'move', 'clarify'].includes(String(entry.action)),
    ),
  ).toBe(true);
  expect(entries.every((entry) => entry.review_state === 'approved')).toBe(true);
  expect(
    entries.every(
      (entry) => Boolean(entry.public_target) && Boolean(entry.evidence_target),
    ),
  ).toBe(true);
  expect(mapping.case_mapping).toEqual(
    Object.fromEntries(
      sourceCases.map((source, index) => [
        source,
        {
          lineage_source_id: lineageCases[index],
          public_id: `OBW-${String(index + 1).padStart(3, '0')}`,
        },
      ]),
    ),
  );
});

test('binds every public file to the frozen native packet', async () => {
  const lineage = await json('skills/outcome-bounded-work/evals/source-lineage.json');
  expect(lineage).toMatchObject({
    native_manifest_sha256:
      '75d2a9fad3962caf9f1f1e05f8783522c3481e8a9c2c2d36a75899762e61a2f2',
    native_version: '1.0.0',
    public_version: '0.1.0',
    source_case_ids: lineageCases,
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
});
